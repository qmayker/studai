from redis.asyncio import Redis
from pyrate_limiter import RedisBucket, Rate, Duration, Limiter

# TODO


class LimiterClient:
    RATES = [Rate(10, Duration.MINUTE)]

    def __init__(self, r: Redis):
        self.r = r

    @staticmethod
    def get_key(user_id: int):
        return f"ai-requests:{user_id}"

    def _get_bucket(self, key: str):
        return RedisBucket.init(redis=self.r, rates=self.RATES, bucket_key=key)

    def get_limiter(self, key: str):
        bucket = self._get_bucket(key=key)
        return Limiter(bucket)
