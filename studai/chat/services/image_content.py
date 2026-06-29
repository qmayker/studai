import uuid
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.transaction import atomic, on_commit
from django.contrib.contenttypes.models import ContentType
from logging import getLogger
from chat.api.serializers import ImageSerializer
from chat.models import ImageItem, Content, Chat

logger = getLogger(__name__)


class ImageContentServices:
    serializer = ImageSerializer
    model = ImageItem

    def __init__(self, images: list[dict[str, InMemoryUploadedFile]]):
        self.images = images
        self.content_type = ContentType.objects.get_for_model(self.model)

    @classmethod
    def get_service(cls, images: list[dict[str, InMemoryUploadedFile]]):
        data = []
        for image in images:
            data.append({"image_content": image})
        serializer = cls.serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return cls(serializer.validated_data)

    @atomic
    def save_image_content(
        self, user, chat: Chat, batch_id: uuid.UUID
    ) -> list[Content]:
        from studai.celery import generate_descriptions

        images = [
            self.model(**image, user=user, description=None) for image in self.images
        ]
        created_images = self.model.objects.bulk_create(images)
        contents = self._create_contents(
            created_images=created_images, chat=chat, batch_id=batch_id
        )
        created_contents = Content.objects.bulk_create(contents)

        def send_celery():
            logger.info("Starting celery task")
            generate_descriptions.delay(user_id=user.id, chat_id=chat.id)

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
