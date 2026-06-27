import os
import asyncio

from celery import Celery, chord
from celery.utils.log import get_task_logger
from redis_lock import Lock
from core.gemini import Gemini
from core.redis import RedisService
from core.socket import WebSocketServices
from core.limiter import LimiterClient


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studai.settings")

app = Celery("studai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from django.conf import settings

logger = get_task_logger(__name__)
redis_service = RedisService(url=settings.CELERY_BROKER_URL)
limiter_client = LimiterClient(redis_service.redis)


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


@app.task()
def generate_description(image_id: int, user_id: int):
    from chat.services.image_item import ImageDescriptionServices

    description = ImageDescriptionServices(
        image_id=image_id,
        user_id=user_id,
        limiter=limiter_client.get_limiter(limiter_client.get_key(user_id=user_id)),
    )
    logger.info(f"Starting description_generating for {image_id}")
    res = description.get_description()
    logger.info(f"Finished description_generating for {image_id}")
    return res


@app.task()
def send_description_callback(result, user_id: int, lock_id: str, chat_id: int):
    lock = Lock(**redis_service.description_kwargs(user_id=user_id), id=lock_id)
    socket = WebSocketServices(chat_id=chat_id)
    lock.release()
    logger.info(f"Descriptions generating finished {result}")


@app.task()
def generate_descriptions(image_ids: list[int], user_id: int, chat_id: int):
    # TODO - add chat_id
    lock = Lock(**redis_service.description_kwargs(user_id=user_id))
    lock.acquire()
    chord(
        (generate_description.s(image_id, user_id) for image_id in image_ids),
        send_description_callback.s(user_id=user_id, lock_id=lock.id, chat_id=chat_id),
    )()
