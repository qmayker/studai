from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from chat.models import Chat
from .image_content import ImageContentServices
from .text_content import TextContentServices


class ContentServices:
    def __init__(
        self,
        image_service: ImageContentServices,
        text_service: TextContentServices,
        chat: Chat,
        user,
    ):
        self.image = image_service
        self.text = text_service
        self.chat = chat
        self.user = user

    @atomic
    def _save_contents(self):
        if self.image.images:
            self.image.save_image_content(user=self.user, chat=self.chat)
        if self.text.text_content.strip():
            self.text.save_text_content(user=self.user, chat=self.chat)

    def validate_contents(self):
        if not self.image.images and not self.text.text_content.strip():
            raise ValidationError("Images and Text can not be empty at the same time")

    def save(self):
        self.validate_contents()
        self._save_contents()
