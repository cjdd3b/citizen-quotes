from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from apps.content.models import Paragraph, Source


class SourceResource(ModelResource):
    '''
    API resource for Source objects. Used to enable filtering
    from QuoteResource for the search box in the interface.
    '''
    class Meta:
        queryset = Source.objects.all()
        resource_name = 'source'
        filtering = {
            "name": ALL,
        }


class QuoteResource(ModelResource):
    '''
    API resource for Paragraph objects.
    '''
    sources = fields.ToManyField(SourceResource, 'sources')
    class Meta:
        queryset = Paragraph.quotes.all().order_by('?')
        fields = ['text',]
        filtering = {
            "sources": ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        # Add the story link from the related Story object
        bundle.data['link'] = bundle.obj.story.get_absolute_url()
        return bundle