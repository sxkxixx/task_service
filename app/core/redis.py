import aioredis
from core.config import REDIS_HOST, REDIS_PORT
from abc import ABC, abstractmethod

redis = aioredis.from_url(
    f'redis://{REDIS_HOST}:{REDIS_PORT}', encoding='utf-8',
)


def redis_session() -> aioredis.Redis:
    return redis


class RedisService(ABC):
    redis: aioredis.Redis = redis_session()

    @abstractmethod
    def push(self, *args, **kwargs):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        pass
