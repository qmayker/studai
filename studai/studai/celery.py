import os
from django.conf import settings
from celery import Celery, chord
from celery.utils.log import get_task_logger
from redis_lock import Lock
from core.gemini import Gemini
from core.redis import RedisService
from websocket.socket import WebSocketServices
from core.limiter import LimiterClient
from core.redis_lock import QuestionGeneratingKwargs, DescriptionGeneratingKwargs
from chat.types.db import Status


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studai.settings")

app = Celery("studai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from . import celery_signals

logger = get_task_logger(__name__)
redis_service = RedisService(url=settings.CELERY_BROKER_URL)
limiter_client = LimiterClient(redis_service.redis)


@app.task()
def generate_questions(chat_id: int, user_id: int):
    from chat.services.chat import ChatServices
    from chat.services.content import ContentTextServices

    agent = Gemini.get_agent(logger=logger)
    socket_service = WebSocketServices()
    text_service = ContentTextServices(user_id=user_id, chat_id=chat_id)
    text = text_service.get_text()
    logger.info(f"{text}")
    chunks = agent.divide_into_chunks(text)
    with Lock(
        redis_client=redis_service.redis,
        **QuestionGeneratingKwargs.get_kwargs(chat_id, user_id),
    ):
        ChatServices.delete_chat_questions(chat_id=chat_id)
        agent.generate_tasks(chunks, chat_id=chat_id)
        socket_service.send_callback(chat_id=chat_id)


@app.task()
def generate_description(image_id: int, user_id: int):
    from chat.services.image_item import ImageDescriptionServices

    service = ImageDescriptionServices(
        image_id=image_id,
        user_id=user_id,
        limiter=limiter_client.get_limiter(limiter_client.get_key(user_id=user_id)),
    )
    try:
        description = service.get_description()
        return {
            image_id: {
                "description": description,
                "status": "success",
            }
        }
    except Exception:
        return {image_id: {"description": None, "status": "failed"}}


@app.task()
def send_description_callback(
    result: list[dict[int, dict]],
    lock_kwargs: dict,
    lock_id: str,
    channel_id: str | None = None,
):
    from chat.models import ImageItem

    lock = Lock(redis_client=redis_service.redis, id=lock_id, **lock_kwargs)
    socket = WebSocketServices()
    images = []
    logger.info(f"Result {result}")
    for image_data in result:
        image_id, data = list(image_data.items())[0]
        if data["status"] == "failed":
            images.append(ImageItem(id=image_id, status=Status.FAILED))
            socket.image_error(image_id=image_id, channel_id=channel_id)
            continue
        images.append(
            ImageItem(
                id=image_id, description=data["description"], status=Status.FINISHED
            )
        )
    try:
        ImageItem.objects.bulk_update(images, fields=["description", "status"])
        socket.button_finished(channel_id=channel_id)
    except Exception as e:
        logger.error(f"Error occurred while sending description callback: {e}")
    finally:
        lock.release()


@app.task()
def generate_descriptions(
    image_ids: list[int], user_id: int, chat_id: int, channel_id: str
):
    from chat.services.image_item import ImageDescriptionServices

    lock_kwargs = DescriptionGeneratingKwargs.get_kwargs(user_id, chat_id)
    logger.info(f"{lock_kwargs}")
    lock = Lock(redis_client=redis_service.redis, **lock_kwargs)
    socket = WebSocketServices()
    if not lock.acquire(blocking=False):
        socket.button_locked(channel_id=channel_id)
        return
    socket.button_running(channel_id=channel_id)

    qs = ImageDescriptionServices.get_pending(user_id=user_id, chat_id=chat_id).filter(
        id__in=image_ids
    )
    qs.set_processing()

    logger.info(
        f"User {user_id}, chat {chat_id} generating descriptions for images: {image_ids}"
    )

    workflow = chord(
        (
            generate_description.s(image_id=image_id, user_id=user_id)
            for image_id in image_ids
        ),
        send_description_callback.s(
            channel_id=channel_id,
            lock_kwargs=lock_kwargs,
            lock_id=lock.id,
        ),
    )
    workflow()
