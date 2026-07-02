import uuid
from django.db.transaction import atomic
from logging import getLogger
from chat.models import Content
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
    def validate_contents(data: dict):
        serializer = ContentsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
