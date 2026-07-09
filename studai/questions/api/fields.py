from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import RelatedField
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.db.models import QuerySet
from logging import getLogger

logger = getLogger()


class RelatedIdField(RelatedField):
    def __init__(self, field_name: str = "related_id", **kwargs):
        super().__init__(**kwargs)
        self.name = field_name

    def _get_payload(self, related_id: int):
        return {"queryset": self.get_queryset(), f"{self.name}": related_id}

    def to_internal_value(self, data):
        try:
            related_id = int(data)
        except Exception:
            raise ValidationError("Expected int type for related_id")
        return get_object_or_404(**self._get_payload(related_id=related_id))

    def to_representation(self, value):
        return getattr(value, self.field_name)
