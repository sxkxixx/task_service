from typing import Annotated, Optional
from core.config import REFRESH_TOKEN_TTL_DAYS
from datetime import datetime, timedelta
from core.redis import redis_session
from aioredis import Redis
from uuid import uuid4, UUID
import json


class RefreshSession:
    def __init__(
            self,
            id: Optional[str],
            user_id: Annotated[UUID, str],
            user_agent: str,
            created_at: Optional[datetime],
    ):
        self.__id = uuid4().__str__() if not id else id
        self.__user_id = user_id.__str__()
        self.__user_agent = user_agent
        self.__created_at = datetime.utcnow() if not created_at else created_at
        self.__ttl = timedelta(days=REFRESH_TOKEN_TTL_DAYS)

    def __to_json_string(self):
        return json.dumps({
            'id': self.__id,
            'user_id': self.__user_id,
            'user_agent': self.__user_agent,
            'created_at': self.__created_at,
        }, default=str)

    async def push_redis(self, redis: Redis = redis_session()):
        json_str = self.__to_json_string()
        await redis.setex(f'refresh_session_{self.__id}', self.__ttl, json_str)
        # refresh_session_0ee91329-6473-42b9-93c9-231a22d8790d
        return self

    async def delete(self, redis: Redis = redis_session()):
        await redis.delete(f'refresh_session_{self.__id}')

    @property
    def get_refresh_id(self):
        return self.__id

    @property
    def expires_in(self) -> int:
        return int((self.__created_at + self.__ttl).timestamp())

    @property
    def ua(self) -> str:
        return self.__user_agent

    @property
    def user_id(self) -> str:
        return self.__user_id

    @classmethod
    async def get_session(cls, refresh_session_id: str, redis: Redis = redis_session()):
        rs_json = await redis.get(f'refresh_session_{refresh_session_id}')
        if rs_json is None:
            return None
        refresh_session = json.loads(rs_json)
        return cls(**refresh_session)
