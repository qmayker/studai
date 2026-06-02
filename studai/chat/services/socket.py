import channels
from celery import shared_task
from asgiref.sync import async_to_sync


class WebSocketServices:
    @staticmethod
    def get_group_name(chat_id: int | str) -> str:
        return f"chat_{chat_id}"


@shared_task()
def send_callback(result, chat_id: int | str):
    group_name = WebSocketServices.get_group_name(chat_id)
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name, {"type": "chat.message", "is_ready": True}
    )
