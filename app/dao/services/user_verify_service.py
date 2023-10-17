from sqlalchemy.exc import IntegrityError

from .iservice import BaseService
from fastapi import HTTPException


class UserVerifyService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add_verify_info(self, **kwargs):
        try:
            info = await self.add(**kwargs)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail={'error': 'User already verified'}
            )
        return info

    async def get_verify_info(self, *filters):
        info = await self.get(*filters)
        if not info:
            raise HTTPException(
                status_code=404,
                detail={'error': 'No Verify Info by current user'}
            )
        return info
