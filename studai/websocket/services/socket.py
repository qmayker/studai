from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..types.socket import ChannelMessage
from core.decorators import channel_send


class SocketGroupServices:
    @staticmethod
    def group_name(chat_id: int) -> str:
        return f"chat_{chat_id}"


class WebSocketServices:
    def __init__(self, channel_id: str):
        self.layer = get_channel_layer()
        self.channel_id = channel_id

    @channel_send()
    def send_callback(self, url: str):
        message = {"type": "chat.message", "is-ready": True, "redirect-url": url}
        return ChannelMessage(channel_id=self.channel_id, message=message)

    @channel_send()
    def button_locked(self) -> ChannelMessage:
        message = {"type": "chat.message", "button-locked": True}
        return ChannelMessage(channel_id=self.channel_id, message=message)

    @channel_send()
    def button_running(self) -> ChannelMessage:
        message = {"type": "chat.message", "button-locked": False}
        return ChannelMessage(channel_id=self.channel_id, message=message)

    @channel_send()
    def button_finished(self) -> ChannelMessage:
        message = {"type": "chat.message", "button-finished": True}
        return ChannelMessage(channel_id=self.channel_id, message=message)

    @channel_send()
    def image_error(self, image_id: int) -> ChannelMessage:
        message = {"type": "chat.message", "error": str(image_id)}
        return ChannelMessage(channel_id=self.channel_id, message=message)

    def _send_to_channel(self, channel_message: ChannelMessage):
        if not channel_message.channel_id:
            return
        async_to_sync(self.layer.send)(
            channel=channel_message.channel_id, message=channel_message.message
        )
