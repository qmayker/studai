import asyncio
from time import sleep
from logging import getLogger
from pyrate_limiter import Limiter
from chat.services.gemini import GeminiAgent
from core.gemini import Gemini
from chat.models import ImageItem
from core.asyncio import AsyncioClient

logger = getLogger(__name__)


class ImageItemServices:
    model = ImageItem

    def __init__(self, user_id: int, image_id: int):
        self.user_id = user_id
        self.image_id = image_id

    @property
    def path(self) -> str:
        image = self.model.objects.get(id=self.image_id, user_id=self.user_id)
        return image.image_content.path

    def add_description(self, description: str):
        return self.model.objects.filter(id=self.image_id, user_id=self.user_id).update(
            description=description
        )


class ImageDescriptionServices:
    model = ImageItem

    def __init__(self, image_id: int, user_id: int, limiter: Limiter):
        self.image_id = image_id
        self.user_id = user_id
        self.limiter = limiter

    def _get_description(self, agent: GeminiAgent, image_item: ImageItemServices):
        logger.info(f"Get description for image with id={image_item.image_id}")
        # description = agent.generate_image_description(image_path=image_item.path)
        description = f"SOME TEXT {image_item.path}"  # temprorary
        image_item.add_description(description=description)
        sleep(5)
        return description

    def get_description(self) -> str:
        self.limiter.try_acquire(name="requests")
        agent = Gemini.get_agent(logger=logger)
        image_item = ImageItemServices(user_id=self.user_id, image_id=self.image_id)
        return self._get_description(agent=agent, image_item=image_item)
