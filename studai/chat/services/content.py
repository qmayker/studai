import uuid
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from chat.models import Chat, Content
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
    def _save_contents(self, batch_id: uuid.UUID):
        contents = []
        if self.image.images:
            contents += self.image.save_image_content(
                user=self.user, chat=self.chat, batch_id=batch_id
            )
        if self.text.text_content.strip():
            contents.append(
                self.text.save_text_content(
                    user=self.user, chat=self.chat, batch_id=batch_id
                )
            )
        return contents

    def validate_contents(self):
        if not self.image.images and not self.text.text_content.strip():
            raise ValidationError("Images and Text can not be empty at the same time")

    def save(self) -> list[Content]:
        self.validate_contents()
        batch_id = uuid.uuid4()
        return self._save_contents(batch_id=batch_id)
