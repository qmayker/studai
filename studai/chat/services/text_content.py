from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from logging import getLogger
from chat.api.serializers import TextSerializer
from chat.models import Content, TextItem, Chat

logger = getLogger(__name__)


class TextContentServices:
    serializer = TextSerializer

    def __init__(self, text_content: str):
        self.text_content = text_content

    @atomic
    def save_text_content(self, chat: Chat, user) -> Content:
        text_item = TextItem.objects.create(text_content=self.text_content, user=user)
        return Content.objects.create(chat=chat, content_object=text_item)

    @classmethod
    def get_service(cls, data):
        serializer = cls.serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return cls(text_content=serializer.validated_data["text_content"])
