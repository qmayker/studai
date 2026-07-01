from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class WebSocketServices:
    def __init__(self, chat_id: int | str):
        self.chat_id = chat_id
        self.layer = get_channel_layer()

    @property
    def group_name(self) -> str:
        return f"chat_{self.chat_id}"

    def send_callback(self):
        group_name = self.group_name
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "chat.message", "is_ready": True}
        )

    def button_locked(self, channel_id: str):
        async_to_sync(self.layer.send)(
            channel=channel_id, message={"type": "chat.message", "button-locked": True}
        )

    def button_running(self, channel_id: str):
        async_to_sync(self.layer.send)(
            channel=channel_id, message={"type": "chat.message", "button-locked": False}
        )

    def button_finished(self, channel_id: str):
        async_to_sync(self.layer.send)(
            channel=channel_id,
            message={"type": "chat.message", "button-finished": True},
        )

    def image_error(self, image_id: int):
        async_to_sync(self.layer.group_send)(
            self.group_name, {"type": "chat.message", "error": str(image_id)}
        )
