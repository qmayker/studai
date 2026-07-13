from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from chat.models import Content, TextItem, ImageItem
from websocket.models import UserSocket
from logging import getLogger

logger = getLogger(__name__)


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


class SocketSerializer(serializers.Serializer):
    socket = serializers.PrimaryKeyRelatedField(queryset=UserSocket.objects.none())

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self._get_context()

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self._get_context()

    def _get_context(self):
        qs = self.context.get("socket_queryset")
        if qs is not None:
            self.fields["socket"].queryset = qs


class ContentsSerializer(serializers.Serializer):
    text = TextSerializer()
    image = ImageSerializer(many=True)
    socket = SocketSerializer()

    def validate(self, data):
        if not data.get("text").get("text_content") and not data.get("image"):
            raise serializers.ValidationError(
                "Either text_content or image_content must be provided."
            )
        return data
