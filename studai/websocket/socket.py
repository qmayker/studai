from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .types.socket import ChannelMessage
from core.decorators import channel_send


class SocketGroupServices:
    @staticmethod
    def group_name(chat_id: int) -> str:
        return f"chat_{chat_id}"


class WebSocketServices:
    def __init__(self):
        self.layer = get_channel_layer()

    def send_callback(self, chat_id: int):
        group_name = self.group_name(chat_id=chat_id)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "chat.message", "is_ready": True}
        )

    @channel_send()
    def button_locked(self, channel_id: str) -> ChannelMessage:
        message = {"type": "chat.message", "button-locked": True}
        return ChannelMessage(channel_id=channel_id, message=message)

    @channel_send()
    def button_running(self, channel_id: str) -> ChannelMessage:
        message = {"type": "chat.message", "button-locked": False}
        return ChannelMessage(channel_id=channel_id, message=message)

    @channel_send()
    def button_finished(self, channel_id: str) -> ChannelMessage:
        message = {"type": "chat.message", "button-finished": True}
        return ChannelMessage(channel_id=channel_id, message=message)

    @channel_send()
    def image_error(self, image_id: int, channel_id: str) -> ChannelMessage:
        message = {"type": "chat.message", "error": str(image_id)}
        return ChannelMessage(channel_id=channel_id, message=message)

    def _send_to_channel(self, channel_message: ChannelMessage):
        if not channel_message.channel_id:
            return
        async_to_sync(self.layer.send)(
            channel=channel_message.channel_id, message=channel_message.message
        )
