from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict
from django.db.transaction import atomic
from django.contrib.contenttypes.models import ContentType
from chat.models import ImageItem, Content, Chat


class ImageContentServices:
    def __init__(self, files: list[InMemoryUploadedFile]):
        self.files = files
        self.model = ImageItem
        self.content_type = ContentType.objects.get_for_model(self.model)

    @classmethod
    def get_service(cls, data: MultiValueDict):
        files = data.getlist("files")
        if not files:
            return
        return cls(files)

    @atomic
    def save_image_content(self, user, chat: Chat):
        images = [self.model(image_content=file, user=user) for file in self.files]
        created_images = self.model.objects.bulk_create(images)
        contents = [
            Content(chat=chat, content_type=self.content_type, object_id=image.id)
            for image in created_images
        ]
        Content.objects.bulk_create(contents)
