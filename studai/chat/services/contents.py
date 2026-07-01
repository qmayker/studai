import uuid
from abc import ABC, abstractmethod
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.transaction import atomic, on_commit
from django.contrib.contenttypes.models import ContentType
from logging import getLogger
from chat.models import ImageItem, Content, Chat, TextItem

logger = getLogger(__name__)


class BasicContentService(ABC):
    model = None

    def __init__(self, user, chat: Chat):
        self.user = user
        self.chat = chat
        self.content_type = ContentType.objects.get_for_model(self.model)

    @atomic
    @abstractmethod
    def save_content(self, batch_id: uuid.UUID) -> list[Content]:
        pass

    @property
    @abstractmethod
    def exists(self) -> bool: ...

    @abstractmethod
    def __str__(self) -> str: ...


class ImageContentServices(BasicContentService):
    model = ImageItem

    def __init__(
        self,
        images: list[dict[str, InMemoryUploadedFile]],
        user,
        chat: Chat,
        socket_id: str,
    ):
        self.images = images
        self.socket_id = socket_id
        super().__init__(user=user, chat=chat)

    @classmethod
    def get_data(cls, images: list[dict[str, InMemoryUploadedFile]]):
        data = []
        for image in images:
            data.append({"image_content": image})
        return data

    @atomic
    def save_content(self, batch_id: uuid.UUID) -> list[Content]:
        from studai.celery import generate_descriptions

        images = [
            self.model(**image, user=self.user, description=None)
            for image in self.images
        ]
        created_images = self.model.objects.bulk_create(images)
        contents = self._create_contents(
            created_images=created_images, chat=self.chat, batch_id=batch_id
        )
        created_contents = Content.objects.bulk_create(contents)

        def send_celery():
            logger.info("Starting celery task")
            generate_descriptions.delay(
                user_id=self.user.id, chat_id=self.chat.id, channel_id=self.socket_id
            )

        on_commit(lambda: send_celery())
        return created_contents

    def _create_contents(
        self, created_images: list[ImageItem], chat: Chat, batch_id: uuid.UUID
    ) -> list[Content]:
        contents = []
        for image in created_images:
            contents.append(
                Content(
                    chat=chat,
                    content_type=self.content_type,
                    object_id=image.id,
                    batch_id=batch_id,
                )
            )
        return contents

    @property
    def exists(self) -> bool:
        return bool(self.images)

    def __str__(self) -> str:
        return "Image Content Services"


class TextContentServices(BasicContentService):
    model = TextItem

    def __init__(self, text_content: str, user, chat: Chat):
        self.text_content = text_content
        super().__init__(user=user, chat=chat)

    @atomic
    def save_content(self, batch_id: uuid.UUID) -> list[Content]:
        text_item = TextItem.objects.create(
            text_content=self.text_content, user=self.user
        )
        return [
            Content.objects.create(
                chat=self.chat, content_object=text_item, batch_id=batch_id
            )
        ]

    @property
    def exists(self) -> bool:
        return bool(self.text_content.strip())

    def __str__(self) -> str:
        return "Text Content Services"
