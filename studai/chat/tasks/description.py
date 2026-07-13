from django.conf import settings
from celery.utils.log import get_task_logger
from celery import chord, shared_task
from redis_lock import Lock
from core.limiter import LimiterClient
from core.redis import RedisService
from core.redis_lock import DescriptionGeneratingKwargs
from chat.types.db import Status
from websocket.services.socket import WebSocketServices

logger = get_task_logger(__name__)
redis_service = RedisService(url=settings.CELERY_BROKER_URL)
limiter_client = LimiterClient(redis_service.redis)


@shared_task
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


@shared_task
def send_description_callback(
    result: list[dict[int, dict]],
    lock_kwargs: dict,
    lock_id: str,
    channel_id: str | None = None,
):
    from chat.models import ImageItem

    lock = Lock(redis_client=redis_service.redis, id=lock_id, **lock_kwargs)
    socket = WebSocketServices(channel_id=channel_id)
    images = []
    for image_data in result:
        image_id, data = list(image_data.items())[0]
        if data["status"] == "failed":
            images.append(ImageItem(id=image_id, status=Status.FAILED))
            socket.image_error(image_id=image_id)
            continue
        images.append(
            ImageItem(
                id=image_id, description=data["description"], status=Status.FINISHED
            )
        )
    try:
        ImageItem.objects.bulk_update(images, fields=["description", "status"])
        socket.button_finished()
    except Exception as e:
        logger.error(f"Error occurred while sending description callback: {e}")
    finally:
        lock.release()


@shared_task
def generate_descriptions(
    image_ids: list[int], user_id: int, chat_id: int, channel_id: str
):
    from chat.services.image_item import ImageDescriptionServices

    lock_kwargs = DescriptionGeneratingKwargs.get_kwargs(user_id, chat_id)
    lock = Lock(redis_client=redis_service.redis, **lock_kwargs)
    socket = WebSocketServices(channel_id=channel_id)
    if not lock.acquire(blocking=False):
        socket.button_locked()
        return
    socket.button_running()

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
