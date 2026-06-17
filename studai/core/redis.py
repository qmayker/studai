import redis
from studai.settings import CELERY_BROKER_URL


class RedisService:
    r = None

    @property
    def redis(self) -> redis.Redis:
        if not self.r:
            self.r = redis.from_url(CELERY_BROKER_URL)
        return self.r

    @property
    def test_result_key(self) -> str:
        return "quiz:result"

    @property
    def _default_kwargs(self) -> dict:
        return {"redis_client": self.redis, "expire": 30}

    def _get_kwargs(self, *args, name: str) -> dict:
        kwargs = self._default_kwargs
        kwargs["name"] = self._add_args(name, *args)
        return kwargs

    def test_result_kwargs(self, user_id: int, attempt_related_id: int) -> dict:
        return self._get_kwargs(user_id, attempt_related_id, name=self.test_result_key)

    @property
    def question_generating_key(self) -> str:
        return "question:generating"

    def question_generating_kwargs(self, user_id: int, chat_id: int) -> dict:
        return self._get_kwargs(user_id, chat_id, name=self.question_generating_key)

    def _add_args(self, name: str, *args):
        for arg in args:
            name = f"{name}:{arg}"
        return name
