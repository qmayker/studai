from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class WebSocketServices:
    def __init__(self, chat_id:int|str):
        self.chat_id = chat_id
    
    @property
    def group_name(self) -> str:
        return f"chat_{self.chat_id}"

    
    def send_callback(self):
        group_name = self.group_name
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "chat.message", "is_ready": True}
        )
