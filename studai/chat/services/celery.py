from chat.models import ImageItem
from chat.types.db import Status


class CelerySignalServices:
    def __init__(self): ...

    def restore_tasks(self):
        images = ImageItem.objects.filter(status=Status.PROCESSING)
        return images.update(status=Status.PENDING)
