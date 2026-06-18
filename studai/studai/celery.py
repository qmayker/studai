import os

from celery import Celery
from celery.app.log import get_logger
from redis_lock import Lock
from core.gemini import Gemini
from core.redis import RedisService
from core.socket import WebSocketServices

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studai.settings")

app = Celery("studai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = get_logger(__name__)
redis_service = RedisService()


@app.task()
def generate_questions(chat_id: int, user_id: int):
    from chat.services.chat import ChatServices

    agent = Gemini.get_agent(logger=logger)
    socket_service = WebSocketServices(chat_id=chat_id)

    chunks = agent.divide_into_chunks(
        "LLM models are large language models that can understand and generate human-like text based on the input they receive. They are trained on vast amounts of data and use deep learning techniques to learn patterns in language. LLMs can be used for various applications, such as chatbots, content generation, and language translation."
    )
    with Lock(
        **redis_service.question_generating_kwargs(chat_id=chat_id, user_id=user_id)
    ):
        logger.info(f"Chat {chat_id} User {user_id} started generating questions")
        ChatServices.delete_chat_questions(chat_id=chat_id)
        agent.generate_tasks(chunks, chat_id=chat_id)
        logger.info(f"Chat {chat_id} User {user_id} finished generating questions")
        socket_service.send_callback()
