import aioredis
from core.config import REDIS_HOST, REDIS_PORT
from abc import ABC, abstractmethod

redis = aioredis.from_url(
    f'redis://{REDIS_HOST}:{REDIS_PORT}', encoding='utf-8',
)


def redis_session() -> aioredis.Redis:
    return redis


class RedisService(ABC):
    # TODO: Переделать message_token & refresh_session под абстрактный класс
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def push_redis(self, *args, **kwargs):
        pass
