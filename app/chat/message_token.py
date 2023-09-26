from auth.models import User
from core.redis import RedisService
from core.config import MESSAGE_TOKEN_KEY, MESSAGE_TOKEN_TTL_SECONDS
from repositories.dependencies import user_service
from uuid import uuid4


class MessageToken(RedisService):
    def __init__(self, user_id: str, _id: str = None):
        self.__id = uuid4().__str__() if not _id else _id
        self.__user_id = user_id.__str__()

    async def push(self):
        await self.redis.setex(f'{MESSAGE_TOKEN_KEY}_{self.__id}', MESSAGE_TOKEN_TTL_SECONDS, self.__user_id)

    async def delete(self):
        await self.redis.delete(f'{MESSAGE_TOKEN_KEY}_{self.__id}')

    @classmethod
    async def get(cls, _id: str) -> 'MessageToken':
        user_id = await cls.redis.get(f'{MESSAGE_TOKEN_KEY}_{_id}')
        if not user_id:
            # TODO: Сделать нормальную ошибку
            raise ValueError()
        return cls(user_id=user_id.decode(), _id=_id)

    @property
    async def user(self):
        return await user_service().get(User.id == self.__user_id)

    @property
    def id(self):
        return self.__id
