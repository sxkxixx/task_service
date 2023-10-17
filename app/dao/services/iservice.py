from typing import Type
from dao.repositories import BaseRepository


class BaseService:
    def __init__(self, repository: Type[BaseRepository]):
        self.repository: Type[BaseRepository] = repository

    async def add(self, **kwargs):
        return await self.repository.add(**kwargs)

    async def get(self, *args):
        return await self.repository.get(*args)

    async def delete(self, obj):
        await self.repository.delete(obj)

    async def update(self, *filters, **kwargs):
        return await self.repository.update(*filters, **kwargs)

    async def select(self, *args):
        return await self.repository.select(*args)

    async def get_with_options(self, option, *args):
        return await self.repository.get_with_options(option, *args)

    async def select_join(self, join_models, *filters):
        return await self.repository.select_join(join_models, *filters)

    async def select_with_options(self, options, *args):
        return await self.repository.select_with_options(options, *args)