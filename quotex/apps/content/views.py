from django.views.generic import TemplateView
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Sum
from apps.content.models import Paragraph, Source


class IndexView(TemplateView):
    '''
    View for the one and only index page'
    '''
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        '''
        Extra context.
        '''
        context = super(IndexView, self).get_context_data(**kwargs)
        context['initial_quote'] = Paragraph.quotes.all().order_by('?')[0]
        context['quotes_count'] = Paragraph.quotes.all().count()
        context['sources_count'] = Source.objects.all().count()
        context['quoted_words_count'] = Paragraph.quotes.all().aggregate(Sum('num_words'))['num_words__sum']
        return context