from celery.signals import worker_ready
from celery.utils.log import get_logger
from django.conf import settings
from redis_lock import Lock
from core.redis import RedisService


logger = get_logger(__name__)


@worker_ready.connect
def restore_unfinished_tasks(sender=None, **kwargs):
    from chat.services.celery import CelerySignalServices

    redis = RedisService(settings.CELERY_BROKER_URL)
    signal_service = CelerySignalServices()
    with Lock(**redis.task_restoring_kwargs(), blocking=False):
        res = signal_service.restore_tasks()
        logger.info(f"{res}")
