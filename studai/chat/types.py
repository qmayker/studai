from typing import NamedTuple
from .models import Content


class Contents(NamedTuple):
    contents: list[Content]
    image_ids: list[int]
