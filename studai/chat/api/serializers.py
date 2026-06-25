from rest_framework.serializers import ModelSerializer
from rest_framework.fields import SerializerMethodField
from chat.models import Content, TextItem, ImageItem


class ContentSerializer(ModelSerializer):
    content = SerializerMethodField()
    item_type = SerializerMethodField()

    class Meta:
        model = Content
        fields = ["id", "content", "item_type"]

    def get_content(self, obj: Content):
        return obj.get_content()

    def get_item_type(self, obj: Content):
        return obj.get_item_type()


class TextSerializer(ModelSerializer):
    class Meta:
        model = TextItem
        fields = ["text_content"]


class ImageSerializer(ModelSerializer):
    class Meta:
        model = ImageItem
        fields = ["image_content"]
