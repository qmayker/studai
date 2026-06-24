from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from chat.models import Content, TextItem, Chat


class TextContentServices:
    def __init__(self, text_content: str):
        self.text_content = text_content

    @atomic
    def save_text_content(self, chat: Chat, user):
        text_item = TextItem.objects.create(text_content=self.text_content, user=user)
        Content.objects.create(chat=chat, content_object=text_item)

    @classmethod
    def get_service(cls, data: dict):
        text_content = data.get("text_content")
        if not text_content:
            raise ValidationError(
                {"status": "not created", "message": "text_content can`t be empty"}
            )
        return cls(text_content=text_content)
