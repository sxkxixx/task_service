from pydantic import BaseModel
from auth.schemas import Error
from repositories.base import BaseRepository
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from core.config import REFRESH_TOKEN_TTL_DAYS


class Service:
    def __init__(self, repository: BaseRepository):
        self.repository: BaseRepository = repository


class UserService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(self, model: BaseModel):
        try:
            user = await self.repository.add(**model.model_dump())
        except IntegrityError:
            return Error(field_name='email', exception='User with current email already exists')
        return user

    async def get_with_options(self, option, *args):
        return await self.repository.get_with_options(option, *args)

    async def delete(self, obj):
        await self.repository.delete(obj)

    async def get(self, *args):
        return await self.repository.get(*args)


class SessionService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self, *args):
        return await self.repository.get(*args)

    async def add(self, user, user_agent):
        expires_in = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
        token = await self.repository.add(
            user_id=user.id,
            user_agent=user_agent,
            expires_in=expires_in.timestamp(),
        )
        return token

    async def get_with_options(self, option, *args):
        return await self.repository.get_with_options(option, *args)

    async def delete(self, refresh_session):
        await self.repository.delete(refresh_session)


class OfferService(Service):
    async def get(self, *args):
        return await self.repository.get(*args)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def select(self, *args):
        return await self.repository.select_join(*args)

    async def add(self, **kwargs):
        res = await self.repository.add(**kwargs)
        return res

    async def get_with_options(self, *args):
        return await self.repository.get(*args)

    async def delete(self, obj):
        await self.repository.delete(obj)

    async def update(self, *args, **kwargs):
        res = await self.repository.update(*args, **kwargs)
        return res

    async def lazyload_get(self, *load_fields, **filters):
        res = await self.repository.lazyload_get(*load_fields, **filters)
        return res


class ReadOnlyService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self, *args):
        return await self.repository.get(*args)

    async def get_with_options(self, *args):
        return await self.repository.get(*args)


class UserAccountService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self, *args):
        return self.repository.get(*args)

    async def add(self, *args, **kwargs):
        res = await self.repository.add(**kwargs)
        return res

    async def get_with_options(self, option, *args):
        return await self.repository.get(option, *args)

    async def update(self, *args, **kwargs):
        res = await self.repository.update(*args, **kwargs)
        return res


class ExecutorService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(self, user_id, offer_id):
        res = await self.repository.add(
            user_id=user_id,
            offer_id=offer_id,
        )
        return res

    async def get(self, *args):
        return self.repository.get(*args)

    async def delete(self, obj):
        await self.repository.delete(obj)

    async def get_with_options(self, option, *args):
        return await self.repository.get(option, *args)

    async def update(self, *args, **kwargs):
        res = await self.repository.update(*args, **kwargs)
        return res

    async def lazyload_get(self, *args, **kwargs):
        res = await self.repository.lazyload_get(*args, **kwargs)
        return res
