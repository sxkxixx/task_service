from pydantic import BaseModel
from auth.schemas import Error
from repositories.base import BaseRepository
from abc import ABC, abstractmethod
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from core.config import REFRESH_TOKEN_TTL_DAYS


class Service(ABC):
    def __init__(self, repository: BaseRepository):
        self.repository: BaseRepository = repository

    @abstractmethod
    def add(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_by_filter(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass

    @abstractmethod
    async def select(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass


class UserService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def select(self, *args, **kwargs):
        raise NotImplementedError()

    async def add(self, model: BaseModel):
        try:
            user = await self.repository.add(**model.model_dump())
        except IntegrityError:
            return Error(field_name='email', exception='User with current email already exists')
        return user

    async def get_by_filter(self, option=None, **kwargs):
        if option:
            return await self.repository.get_with_options(option, **kwargs)
        return await self.repository.get(**kwargs)

    async def delete(self, obj):
        await self.repository.delete(obj)

    async def update(self, *args, **kwargs):
        raise NotImplementedError()


class SessionService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(self, user, user_agent, refresh_token):
        expires_in = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
        token = await self.repository.add(
            user_id=user.id,
            user_agent=user_agent,
            expires_in=expires_in.timestamp(),
            refresh_token=refresh_token
        )
        return token

    async def get_by_filter(self, option=None, **kwargs):
        if option:
            return await self.repository.get_with_options(option, **kwargs)
        return await self.repository.get(**kwargs)

    async def delete(self, refresh_session):
        await self.repository.delete(refresh_session)

    async def update(self, *args, **kwargs):
        raise NotImplementedError()

    async def select(self, *args, **kwargs):
        raise NotImplementedError()


class OfferService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def select(self, *args):
        return await self.repository.select(*args)

    async def add(self, **kwargs):
        res = await self.repository.add(**kwargs)
        return res

    async def get_by_filter(self, *args):
        return await self.repository.get(*args)

    async def delete(self, *args, **kwargs):
        raise NotImplementedError()

    async def update(self, obj_id, **updating_fields):
        res = await self.repository.update(obj_id, **updating_fields)
        return res


class ReadOnlyService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_by_filter(self, **kwargs):
        res = await self.repository.get(**kwargs)
        return res

    async def add(self, *args, **kwargs):
        raise NotImplementedError()

    async def delete(self, *args, **kwargs):
        raise NotImplementedError()

    async def update(self, *args, **kwargs):
        raise NotImplementedError()

    async def select(self, *args, **kwargs):
        raise NotImplementedError()


class UserAccountService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(self, *args, **kwargs):
        res = await self.repository.add(**kwargs)
        return res

    async def get_by_filter(self, **kwargs):
        res = await self.repository.get(**kwargs)
        return res

    async def delete(self, *args, **kwargs):
        raise NotImplementedError()

    async def update(self, obj_id, **kwargs):
        res = await self.repository.update(obj_id, **kwargs)
        return res

    async def select(self, *args, **kwargs):
        raise NotImplementedError()


class ExecutorService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(self, user_id, offer_id):
        res = await self.repository.add(
            user_id=user_id,
            offer_id=offer_id,
        )
        return res

    async def delete(self, obj):
        await self.repository.delete(obj)

    async def get_by_filter(self, **kwargs):
        return await self.repository.get(**kwargs)

    async def select(self, *args, **kwargs):
        raise NotImplemented()

    async def update(self, obj_id, **kwargs):
        res = await self.repository.update(obj_id, **kwargs)
        return res
