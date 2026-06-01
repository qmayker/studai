import os
import channels.layers
from asgiref.sync import async_to_sync
from celery import Celery
from celery.app.log import get_logger
from chat.services.gemini import GeminiAgent, GeminiConfig
from chat.services.socket import WebSocketServices

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studai.settings")

app = Celery("studai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = get_logger(__name__)


@app.task()
def generate_questions(chat_id: int):
    group_name = WebSocketServices.get_group_name(chat_id)
    channel_layer = channels.layers.get_channel_layer()
    agent = GeminiAgent(
        config=GeminiConfig.get_config(), logger=logger, key=GeminiConfig.api_key()
    )
    async_to_sync(channel_layer.group_send)(
        group_name, {"type": "chat.message", "is_ready": True}
    )
