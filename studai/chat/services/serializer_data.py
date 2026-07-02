from logging import getLogger
from chat.types.serializer import SerializerFields

logger = getLogger(__name__)


class SerializerDataService:
    def get_serializer_data(self, **kwargs: SerializerFields):
        data = {}
        for arg_name, field in kwargs.items():
            field_data = field.field.get_data(field.data)
            data[arg_name] = field_data
        return data
