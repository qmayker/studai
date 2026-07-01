import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

# TODO - remake with asyncio


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.room_name}"
        logger.info(f"group name: {self.room_group_name} chanel {self.channel_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"channel_id": self.channel_name}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, event: dict):
        logger.info(f"{event}")
        await self.send(
            text_data=json.dumps(
                {key: value for key, value in event.items() if key != "type"}
            )
        )
