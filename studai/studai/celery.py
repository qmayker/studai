import os
import asyncio

from celery import Celery, chord
from celery.utils.log import get_task_logger
from redis_lock import Lock
from core.gemini import Gemini
from core.redis import RedisService
from core.socket import WebSocketServices
from core.limiter import LimiterClient
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studai.settings")

app = Celery("studai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


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
def generate_description(image_id: int, user_id: int, chat_id: int, lock_id: str):
    from chat.services.image_item import ImageDescriptionServices

    description = ImageDescriptionServices(
        image_id=image_id,
        user_id=user_id,
        limiter=limiter_client.get_limiter(limiter_client.get_key(user_id=user_id)),
    )
    try:
        description.add_description()
        return image_id
    except Exception:
        qs = description.get_processing(user_id=user_id, chat_id=chat_id).filter(
            id=image_id
        )
        qs.set_failed()
        socket = WebSocketServices(chat_id=chat_id)
        socket.image_error(image_id=image_id)
        return None


@app.task()
def send_description_callback(
    result: list[int], user_id: int, lock_id: str, chat_id: int
):
    # TODO - add generate-button lock for user
    from chat.services.image_item import ImageDescriptionServices

    lock = Lock(
        **redis_service.description_kwargs(user_id=user_id, chat_id=chat_id), id=lock_id
    )
    socket = WebSocketServices(chat_id=chat_id)
    qs = ImageDescriptionServices.get_processing(
        user_id=user_id, chat_id=chat_id
    ).filter(id__in=result)
    qs.set_finished()
    socket.button_finished()
    lock.release()


@app.task()
def generate_descriptions(user_id: int, chat_id: int):
    from chat.services.image_item import ImageDescriptionServices

    lock = Lock(**redis_service.description_kwargs(user_id=user_id, chat_id=chat_id))
    socket = WebSocketServices(chat_id=chat_id)
    if not lock.acquire(blocking=False):
        socket.button_locked()
        return
    socket.button_running()

    qs = ImageDescriptionServices.get_pending(user_id=user_id, chat_id=chat_id)
    image_ids = list(qs.values_list("id", flat=True))
    qs.set_processing()

    logger.info(
        f"User {user_id}, chat {chat_id} generating descriptions for images: {image_ids}"
    )

    workflow = chord(
        (
            generate_description.s(
                image_id=image_id, user_id=user_id, chat_id=chat_id, lock_id=lock.id
            )
            for image_id in image_ids
        ),
        send_description_callback.s(user_id=user_id, lock_id=lock.id, chat_id=chat_id),
    )
    workflow()
