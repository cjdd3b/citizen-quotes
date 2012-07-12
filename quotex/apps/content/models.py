from django.db import models
from django.utils.html import strip_tags


class Story(models.Model):
    '''
    Model representing a news story. This demo doesn't interact much
    on the story level. Most of the work is done on Paragraphs.
    '''
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Stories'

    def __unicode__(self):
        return self.title

    def get_stripped(self):
        '''
        Return a plaintextversion of the text with HTML stripped and unescaped.
        '''
        import HTMLParser
        h = HTMLParser.HTMLParser()
        return h.unescape(strip_tags(self.body))

    def get_fulltext(self):
        '''
        Returns the clean full text of a story by joining the text of its
        constituent paragraphs.
        '''
        return '\n'.join([p.text for p in self.paragraph_set.all()]).strip()


class Paragraph(models.Model):
    '''
    Simple model representing Paragraphs, which are assigned to stories.

    This is where most of the action happens. Stories are tokenized into
    paragraphs for the purposes of identifying quotes.
    '''
    story = models.ForeignKey(Story)
    text = models.TextField()
    quote = models.NullBooleanField(default=None)
    order = models.IntegerField()
    score = models.FloatField(blank=True, null=True)
    sources = models.ManyToManyField('Source')
    for_training = models.BooleanField(default=False)

    class Meta:
        ordering = ['story', 'order',]

    def __unicode__(self):
        return '%s: %s' % (self.story, self.order)


class Source(models.Model):
    '''
    Model representing sources, or the speakers of quotes, which are assigned
    to paragraphs via M2M.
    '''
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name