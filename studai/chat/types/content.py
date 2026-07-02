from typing import NamedTuple
from chat.models import Content


class ImageContents(NamedTuple):
    contents: list[Content]
    image_ids: list[int]
