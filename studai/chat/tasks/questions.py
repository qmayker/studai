from django.conf import settings
from celery import shared_task
from django.urls import reverse
from redis_lock import Lock
from core.redis import RedisService
from core.gemini import Gemini
from core.redis_lock import QuestionGeneratingKwargs
from websocket.services.socket import WebSocketServices

redis_service = RedisService(url=settings.CELERY_BROKER_URL)


@shared_task
def generate_questions(
    chat_id: int, user_id: int, channel_id: str, chat_related_id: int
):
    from chat.services.chat import ChatServices
    from chat.services.content import ContentTextServices

    agent = Gemini.get_agent()
    socket = WebSocketServices(channel_id=channel_id)
    text_service = ContentTextServices(user_id=user_id, chat_id=chat_id)
    chunks = agent.divide_into_chunks(text_service.get_text())
    with Lock(
        redis_client=redis_service.redis,
        **QuestionGeneratingKwargs.get_kwargs(chat_id, user_id),
    ):
        ChatServices.delete_chat_questions(chat_id=chat_id)
        agent.generate_tasks(chunks, chat_id=chat_id)
        socket.send_callback(reverse("questions:questions", args=[chat_related_id]))
