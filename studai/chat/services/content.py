from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError, PermissionDenied
from chat.models import Content, TextItem, Chat


class ContentAPIServices:
    @staticmethod
    @atomic
    def save_text_content(text_content: str, chat: Chat):
        text_item = TextItem.objects.create(text_content=text_content)
        Content.objects.create(chat=chat, content_object=text_item)

    @staticmethod
    def get_text_content(data: dict):
        text_content = data.get("text_content")
        if not text_content:
            raise ValidationError(
                {"status": "not created", "message": "text_content can`t be empty"}
            )
        return text_content
    
