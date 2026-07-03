from celery.signals import worker_ready
from celery.utils.log import get_logger
from django.conf import settings
from redis_lock import Lock
from core.redis import RedisService
from core.redis_lock import TaskRestoringKwargs


logger = get_logger(__name__)


@worker_ready.connect
def restore_unfinished_tasks(sender=None, **kwargs):
    from chat.services.image_item import ImageitemRestoreService

    redis = RedisService(settings.CELERY_BROKER_URL)
    signal_service = ImageitemRestoreService()

    lock_kwargs = TaskRestoringKwargs.get_kwargs(blocking=False)
    lock = Lock(redis_client=redis.redis, **lock_kwargs)
    if not lock.acquire(blocking=False):
        return
    res = signal_service.restore(lock_kwargs=lock_kwargs, lock_id=lock.id)
    logger.info(f"{res}")
