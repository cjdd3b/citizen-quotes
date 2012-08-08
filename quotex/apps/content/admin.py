from django.contrib import admin
from quotex.apps.content.models import Story, Paragraph, Source

########## INLINES ##########

class ParagraphInline(admin.TabularInline):
    model = Paragraph

########## ADMINS ##########

class StoryAdmin(admin.ModelAdmin):
	inlines = [ParagraphInline,]
admin.site.register(Story, StoryAdmin)

class GrafAdmin(admin.ModelAdmin):
    filter_horizontal = ['sources',]
    list_display = ['__unicode__', 'text', 'score', 'quote', 'for_training']
    search_fields = ['text', 'story__title']
    list_filter = ['quote',]
    list_editable = ['quote', 'for_training']
admin.site.register(Paragraph, GrafAdmin)

class SourceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Source, SourceAdmin)