from sqlalchemy.exc import IntegrityError
from .iservice import BaseService
from auth.hasher import Hasher
from fastapi import HTTPException


class UserService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def register_user(self, **kwargs):
        try:
            user = await self.add(
                email=kwargs.get('email'),
                password=Hasher.get_password_hash(kwargs.get('password'))
            )
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail={
                    'field_name': 'email',
                    'info': 'Email field must\'be unique for User'
                }
            )
        return user

    async def get_user(
            self,
            *args
    ):
        user = await self.get(*args)
        if not user:
            raise HTTPException(
                status_code=400,
                detail={'error': 'No user by this email'}
            )
        return user

    async def delete_user(self, user):
        await self.delete(user)

    async def verify_user(self, *filters):
        return await self.update(*filters, is_verified=True)
