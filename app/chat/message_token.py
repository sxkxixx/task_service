from auth.models import User
from core.redis import redis_session
from core.config import MESSAGE_TOKEN_KEY, MESSAGE_TOKEN_TTL_SECONDS
from aioredis import Redis
from repositories.dependencies import user_service
from uuid import uuid4


class MessageToken:
    def __init__(self, user_id: str):
        self.__id = uuid4().__str__()
        self.__user_id = user_id

    async def push_redis(self, redis: Redis = redis_session()):
        await redis.setex(f'{MESSAGE_TOKEN_KEY}_{self.__id}', MESSAGE_TOKEN_TTL_SECONDS, self.__user_id)

    async def delete(self, redis: Redis = redis_session()):
        await redis.delete(f'{MESSAGE_TOKEN_KEY}_{self.__id}')

    @classmethod
    async def get(cls, _id: str, redis: Redis = redis_session()):
        user_id = await redis.get(_id)
        if not user_id:
            return None
        service = user_service()
        return await service.get(User.id == user_id)

    @property
    def id(self):
        return self.__id
