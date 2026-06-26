from chat.models import ImageItem


class ImageItemServices:
    model = ImageItem

    def __init__(self, user_id: int, image_id: int):
        self.user_id = user_id
        self.id = image_id

    @property
    def path(self) -> str:
        image_obj = self.model.objects.get(user_id=self.user_id, pk=self.image_id)
        return image_obj.image_content.path

    def add_description(self, description: str):
        return self.model.objects.filter(id=self.image_id, user_id=self.user_id).update(
            description=description
        )
