import uuid
from django.db.transaction import atomic
from django.contrib.contenttypes.prefetch import GenericPrefetch
from logging import getLogger
from chat.models import Content, ImageItem, TextItem
from chat.types.db import Status
from chat.api.serializers import ContentsSerializer
from .contents import BasicContentService

logger = getLogger(__name__)


class ContentServices:
    def __init__(
        self,
        *services: BasicContentService,
        socket_id: str,
    ):
        self.services = services
        self.socket_id = socket_id

    @atomic
    def _save_contents(self, batch_id: uuid.UUID):
        contents = []
        for service in self.services:
            if not service.exists:
                continue
            contents += service.save_content(batch_id=batch_id)
        return contents

    def save(self) -> list[Content]:
        batch_id = uuid.uuid4()
        return self._save_contents(batch_id=batch_id)


class ContentValidator:
    @staticmethod
    def validate_contents(data: dict, **kwargs):
        serializer = ContentsSerializer(data=data, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class ContentTextServices:
    model = Content

    def __init__(self, user_id: int, chat_id: int):
        self.user_id = user_id
        self.chat_id = chat_id

    def get_queryset(self):
        return self.model.objects.filter(chat_id=self.chat_id).prefetch_related(
            GenericPrefetch(
                "content_object",
                [
                    ImageItem.objects.all(),
                    TextItem.objects.all(),
                ],
            )
        )

    def get_text(self) -> str:
        qs = self.get_queryset()
        content_texts = []
        for content in qs:
            if not content.content_object.finished:
                continue
            text_content = content.content_object.text
            content_texts.append(text_content)

        return " ".join(content_texts)
