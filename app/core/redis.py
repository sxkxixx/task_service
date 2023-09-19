import aioredis
from core.config import REDIS_HOST, REDIS_PORT

redis = aioredis.from_url(
    f'redis://{REDIS_HOST}:{REDIS_PORT}', encoding='utf-8',
)


def redis_session() -> aioredis.Redis:
    return redis
