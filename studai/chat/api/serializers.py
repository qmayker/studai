from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from chat.models import Content, TextItem, ImageItem
from websocket.models import UserSocket


class ContentSerializer(serializers.ModelSerializer):
    content = SerializerMethodField()
    item_type = SerializerMethodField()

    class Meta:
        model = Content
        fields = ["id", "content", "item_type"]

    def get_content(self, obj: Content):
        return obj.get_content()

    def get_item_type(self, obj: Content):
        return obj.get_item_type()


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextItem
        fields = ["text_content"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageItem
        fields = ["image_content"]


class ContentsSerializer(serializers.Serializer):
    text = TextSerializer()
    image = ImageSerializer(many=True)
    socket = serializers.PrimaryKeyRelatedField(queryset=UserSocket.objects.none())

    def validate(self, data):
        if not data.get("text").get("text_content") and not data.get("image"):
            raise serializers.ValidationError(
                "Either text_content or image_content must be provided."
            )
        return data

    def __init__(self, *args, socket_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        if socket_queryset is not None:
            self.fields["socket"].queryset = socket_queryset
