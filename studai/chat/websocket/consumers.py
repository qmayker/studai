import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

# TODO - remake with asyncio


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.room_name}"
        logger.info(f"group name: {self.room_group_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.info(f"RECIEVED {text_data}")
        text_data_json = json.loads(text_data)
        is_ready = text_data_json["ready"]
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "is_ready": is_ready}
        )

    async def chat_message(self, event):
        is_ready = event["is_ready"]
        await self.send(text_data=json.dumps({"is_ready": is_ready}))
