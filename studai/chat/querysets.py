from django.db.models import QuerySet
from .types.db import Status


class ImageItemQuerySet(QuerySet):
    def pending(self, user_id: int, chat_id: int):
        return self.filter(
            user_id=user_id, content__chat=chat_id, status=Status.PENDING
        )

    def set_processing(self):
        return self.filter(status=Status.PENDING).update(status=Status.PROCESSING)

    def processing(self, user_id: int, chat_id: int):
        return self.filter(
            user_id=user_id, content__chat=chat_id, status=Status.PROCESSING
        )

    def set_finished(self):
        return self.filter(status=Status.PROCESSING).update(status=Status.FINISHED)

    def set_failed(self):
        return self.update(status=Status.FAILED)
