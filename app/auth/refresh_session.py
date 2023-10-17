from core.config import REFRESH_TOKEN_TTL_DAYS, REFRESH_SESSION_KEY
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Annotated, Optional
from core.redis import RedisService
from uuid import uuid4, UUID
import json


class RefreshSession(RedisService):
    def __init__(
            self,
            _id: Optional[str],
            user_id: Annotated[UUID, str],
            user_agent: str,
            created_at: Optional[datetime],
    ):
        super().__init__()
        self.__id = uuid4().__str__() if not _id else _id
        self.__user_id = user_id.__str__()
        self.__user_agent = user_agent
        self.__created_at = datetime.utcnow() if not created_at else created_at
        self.__ttl = timedelta(days=REFRESH_TOKEN_TTL_DAYS)

    def __to_json_string(self):
        return json.dumps({
            '_id': self.__id,
            'user_id': self.__user_id,
            'user_agent': self.__user_agent,
            'created_at': self.__created_at,
        }, default=str)

    async def push(self):
        json_str = self.__to_json_string()
        await self.redis.setex(f'{REFRESH_SESSION_KEY}_{self.__id}', self.__ttl, json_str)
        # refresh_session_a8349eaa-8d75-4db0-bc98-598deb6dbff6
        return self

    async def delete(self):
        await self.redis.delete(f'{REFRESH_SESSION_KEY}_{self.__id}')

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
    async def get(cls, refresh_session_id: str, user_agent: str):
        rs_json = await cls.redis.get(f'{REFRESH_SESSION_KEY}_{refresh_session_id}')
        if rs_json is None:
            raise HTTPException(
                status_code=401,
                detail={
                    'status': 'error',
                    'detail': 'Refresh Session has expired'
                }
            )
        refresh_session = cls(**json.loads(rs_json))
        if refresh_session.ua != user_agent:
            raise HTTPException(
                status_code=401,
                detail={
                    'status': 'error',
                    'detail': 'Incorrect User-Agent'
                }
            )
        return refresh_session
