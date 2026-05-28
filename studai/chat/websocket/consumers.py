import json
import logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.room_name}"
        logger.info(f"group name: {self.room_group_name}")
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        logger.info(f"RECIEVED {text_data}")
        text_data_json = json.loads(text_data)
        is_ready = text_data_json["ready"]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "is_ready": is_ready}
        )

    def chat_message(self, event):
        logger.info(f"{event}")
        is_ready = event["is_ready"]
        self.send(text_data=json.dumps({"is_ready": is_ready}))
