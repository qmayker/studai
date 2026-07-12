import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserSocket
from .socket import SocketGroupServices

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = SocketGroupServices.group_name(chat_id=self.chat_id)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        user_socket = await UserSocket.objects.acreate(
            user_id=self.user_id, socket_id=self.channel_name
        )
        self.socket_id = user_socket.id
        await self.send(text_data=json.dumps({"socket_id": self.socket_id}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Deleting UserSocket with id {self.socket_id}")
        await UserSocket.objects.filter(id=self.socket_id).adelete()

    async def chat_message(self, event: dict):
        await self.send(
            text_data=json.dumps(
                {key: value for key, value in event.items() if key != "type"}
            )
        )
