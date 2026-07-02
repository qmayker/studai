from django.core.files.uploadedfile import InMemoryUploadedFile
from logging import getLogger
from abc import ABC, abstractmethod

IMAGE_INPUT = list[InMemoryUploadedFile]
IMAGE_OUTPUT = list[dict[str, list]]

logger = getLogger(__name__)


class SerializerField[TI, TO](ABC):
    @staticmethod
    @abstractmethod
    def get_data(data: TI) -> TO: ...


class SocketIdField(SerializerField[str, str]):
    @staticmethod
    def get_data(data):
        return data


class TextField(SerializerField[str, dict[str, str]]):
    @staticmethod
    def get_data(data):
        return {"text_content": data}


class ImageField(SerializerField[IMAGE_INPUT, IMAGE_OUTPUT]):
    @staticmethod
    def get_data(data):
        images = []
        for image in data:
            images.append({"image_content": image})
        return images
