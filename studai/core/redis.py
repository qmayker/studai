import redis
from django.conf import settings


class RedisClient:
    r = redis.from_url(settings.CELERY_BROKER_URL)

    def test_result_key(self, user_id: int, attempt_related_id: int):
        return f"testresult:{user_id}:{attempt_related_id}"

    @property
    def _redis_kwargs(self):
        return {"redis_client": self.r}

    def test_result_kwargs(self, user_id: int, attempt_related_id: int):
        kwargs = self._redis_kwargs
        kwargs["name"] = self.test_result_key(
            user_id=user_id, attempt_related_id=attempt_related_id
        )
        return kwargs
