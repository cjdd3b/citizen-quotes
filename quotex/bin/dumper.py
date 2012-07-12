from apps.content.models import Story, Paragraph, Source
from django.core import serializers

if __name__ == '__main__':
    stories = Story.objects.all()[:100]
    paragraphs = Paragraph.objects.filter(story__in=stories)
    sources = Source.objects.filter(paragraph__in=paragraphs)

    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()

    with open("../fixtures/stories.json", "w") as out:
        json_serializer.serialize(stories, stream=out)

    with open("../fixtures/paragraphs.json", "w") as out:
        json_serializer.serialize(paragraphs, stream=out)

    with open("../fixtures/sources.json", "w") as out:
        json_serializer.serialize(sources, stream=out)
