import redis


class RedisService:
    def __init__(self, url: str):
        self.url = url

    @property
    def redis(self) -> redis.Redis:
        return redis.from_url(self.url)
