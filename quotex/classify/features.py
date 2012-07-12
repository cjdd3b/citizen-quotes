'''
features.py

These are the features used in maxent.py in order to help classify direct quotations.

Active features (the ones actually being used in the demo) are listed under the active
features heading. Inactive features, which we tested but ended up not using, are listed
under the inactive features heading purely for instructional purposes.
'''
import re
import nltk
from classify.constants import ATTRIBUTION_WORDS_STEMMED, PRONOUNS, PUNCTUATION_TO_REMOVE
from nltk.stem.porter import PorterStemmer

########## HELPER FUNCTIONS ##########

def bracketed_find(s, start, end, startat=0):
    """
    Function to find content in between two words or characters without regex.
    From http://stackoverflow.com/questions/1116172/finding-content-between-two-words-withou-regex-beautifulsoup-lxml-etc
    """
    startloc=s.find(start, startat)
    if startloc==-1:
        return []
    endloc=s.find(end, startloc+len(start))
    if endloc == -1:
        return [s[startloc+len(start):]]
    return [s[startloc+len(start):endloc]] + bracketed_find(s, start, end, endloc+len(end))

def get_words_outside_quotes(words, n=5):
    """
    Function to get words within n characters of quote marks.
    """
    quote_indices = [m.start() for m in re.finditer('"', words)]
    for i in range(len(quote_indices)):
        if i % 2 != 0:
            index = quote_indices[i] + 1
            try:
                next = quote_indices[i+1]
            except IndexError:
                next = len(words)
            return words[index:next].strip().split()[:5]

def clean_text(words):
    """
    Function to clean input text by removing select punctuation and stopwords
    and stemming with a Porter stemmer.
    """
    for p in PUNCTUATION_TO_REMOVE:
        words = words.replace(p, '')
    stopwords = nltk.corpus.stopwords.words('english')
    return ' '.join([PorterStemmer().stem_word(w) for w in words.split() if w not in stopwords])

########## ACTIVE FEATURES ##########

def contains_quotes(words):
    """
    Returns true if the input string contains quote marks. Word of warning:
    be sure unicode smart quotes are swapped out for ascii dumb quotes or 
    this won't catch them. Same goes for any other feature that looks for
    quotes.
    """
    contains_quotes = False
    if words.find('"') > -1:
        contains_quotes = True
    return contains_quotes

def first_quote_index(words):
    """
    Returns the index of the first quote mark in the input string. Rounds to
    the nearest 10th position. So a quote that appears at position 5 in a string
    will actually be output as 10 from this function.

    The reason is because NLTK's particular maxent classifier doesn't deal well 
    with continuous variables. Grouping them as every 10th position effectively
    makes the data categorical (the 10s, 20s, 30s, etc.)
    """
    return round(words.find('"'), -1)

def last_word(words):
    '''
    Returns the last word in the input string. Useful because a lot of quote grafs
    end with something like "Smith said."
    '''
    words = clean_text(words)
    if len(words.split()) > 0:
        return words.split()[-1]
    return False

def said_near_source(words):
    '''
    Janky set of regexes that return true if the word said appears within five words
    of a pronoun or capitalized (proper) noun. This should be rewritten for about a
    million different reasons, but it works fine for demo purposes, so ....
    '''
    words = clean_text(words)
    said_near_source = False
    if len(re.findall(r'\b(he|she|[A-Z][a-z]+)\W+(?:\w+\W+){0,5}(said|added|says)\b', words)) > 0 \
        or len(re.findall(r'\b(said|added|says){0,5}(he|she|[A-Z][a-z]+)\W+(?:\w+\W+)\b', words)) > 0:
        said_near_source = True
    return said_near_source

def num_words_between_quotes(words):
    '''
    Uses the helper functions above to count the number of words in the input
    text that fall between quote marks. Returns that number rounded to the nearest
    5 words, again to make the continuous data more categorical.
    '''
    num_words_between_quotes = 0
    lots_of_words_between_quotes = False
    for q in bracketed_find(words, '"', '"'):
        num_words_between_quotes += len(q.split())
    return round(num_words_between_quotes, -1) / 2

def words_near_quotes(words):
    '''
    Creates features out of the 5 words (by default) that appear nearby but outside
    the quote marks in the input text.
    '''
    words = clean_text(words)
    if get_words_outside_quotes(words):
        for word in get_words_outside_quotes(words):
            yield word

########## INACTIVE FEATURES ##########

def first_word(words):
    '''
    Returns the first word in the input string.
    '''
    words = clean_text(words)
    if len(words.split()) > 0:
        return words.split()[0]
    return False

def word_features(words):
    '''
    Creates features out of all the words in the input text.
    '''
    words = clean_text(words)
    for word in words.split():
        yield word

def contains_attribution(words):
    '''
    Returns true if the input string contains a stemmed attribution 
    word like said.
    '''
    words = clean_text(words)
    contains_attribution = False
    for word in words.split():
        if word.lower() in ATTRIBUTION_WORDS_STEMMED:
            contains_attribution = True
            break
    return contains_attribution

def contains_pronoun(words):
    '''
    Returns true if the input string contains a pronoun.
    '''
    words = clean_text(words)
    contains_pronoun = False
    for word in words.split():
        if word.lower() in PRONOUNS:
            contains_pronoun = True
            break
    return contains_pronoun

def pct_words_between_quotes(words):
    '''
    Similar to the num_words_between_quotes feature above but converts
    that to a percentage.
    '''
    total_words = len(words.split())
    num_words_between_quotes = 0
    lots_of_words_between_quotes = False
    for q in bracketed_find(words, '"', '"'):
        num_words_between_quotes += len(q.split())
    return round(float(num_words_between_quotes)/float(total_words), 0)

def preceded_by_quote(story, graf_order):
    '''
    Returns true if the previous paragraph is also a quote.
    '''
    if Paragraph.objects.get(story=story, order=graf_order-1).quote == True:
        return True
    return False