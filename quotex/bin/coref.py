'''
coref.py

Uses OpenCalais for pronoun coreference resolution. In this case, works
by just assigning entities to their associated paragraphs.

Another option would be to train a coreference detector using the coref
module in nltk_contrib (https://github.com/nltk/nltk_contrib). But the
module seems to count on the MUC6 corpus for training, and the MUC6 corpus
ain't free: http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2003T13

Calais was the cheap and easy way to start, which works fine for demo purposes.
'''
from calais import Calais
from apps.content.models import Story, Source

# OpenCalais API key. Get one here: http://www.opencalais.com/APIkey/
API_KEY = 'xzaj99phgusg94t4zdpgk6x8'

########## PRIVATE FUNCTIONS ##########

def _get_people(text):
    '''
    Runs input text through Calais to extract people, coreferences and their
    locations.

    This function returns a canonical name for any given source in the document
    and contextual information about where coreferences appear, based on the
    text before and after the pronoun occurrance.

    Takes full story text as input.

    This is a pretty bare-bones function. It doesn't handle Calais API errors, so 
    it tends to crap out from time to time. Future refinements should account for this.
    '''
    # Run input text through Calais
    calais = Calais(API_KEY, submitter="tbc-coref-test")
    annotations = calais.analyze(text)

    # If no entities come back, peace out
    if not hasattr(annotations, 'entities'):
        return False

    coref = {} # Dictionary to hold our corefence object.
    for e in annotations.entities:
        instances = []
        # We only care about Person entities, not companies, places, etc.
        if e['_type'] == 'Person':
            # For each instance of that entity (which includes pronouns and other references) ...
            for i in e['instances']:
                # Collect the coreference text (exact) the preceding text (prefix) and the
                # following text (suffix) for reference information. We'll need this later.
                instances.append((i.get('exact'), i.get('suffix', ''), i.get('prefix', '')))
            # Associate the canonical name with the coreference and context information gathered
            # above for use later.
            name = e.get("commonname", e.get('name', None))
            coref[name] = instances
    return coref

########## PUBLIC FUNCTIONS ##########

def resolve_pronouns(story):
    '''
    Function to resolve pronouns given our particularly funky use case.

    This function takes a full story text and resolves pronouns within the individual
    paragraph objects that make up that text. It's set up this way because our system's
    main unit of content is the paragraph, not the story.

    These nested loops are an awfully inefficient way of resolving pronouns. Would be great
    to see it cleaned up. But again, for demo purposes, works just fine.
    '''
    # Get the people dict using the private function above, given the full text of the story.
    people = _get_people(story.get_fulltext())

    # If no entities come back, fail silently. This almost never happens.
    if not people:
        return

    # For each person in the story ...
    for p in people.keys():
        canonical_name = p # The canonical name is the key
        # For each reference to that person (last name, pronoun, whatever) ...
        for i in people[p]:
            # Loop through each paragraph and see if we can find the prefix and suffix
            for paragraph in story.paragraph_set.all():
                pronoun, suffix, prefix = i # Unpack
                # If we find the prefix and suffix in a paragraph, either get or create a
                # source object and assign it to that paragraph.
                if paragraph.text.find(suffix) > -1 or paragraph.text.find(prefix) > -1:
                    source, created = Source.objects.get_or_create(name=canonical_name)
                    paragraph.sources.add(source)
                    source.save()
                    paragraph.save()
    return

########## MAIN ##########

if __name__ == '__main__':
    for s in Story.objects.all():
        print '%s -> %s' % (s.pk, s.title)
        resolve_pronouns(s)
