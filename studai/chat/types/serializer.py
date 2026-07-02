from typing import NamedTuple, Any
from chat.services.serializer_fields import SerializerField


class SerializerFields(NamedTuple):
    field: SerializerField
    data: Any
