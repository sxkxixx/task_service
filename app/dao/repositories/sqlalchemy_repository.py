from typing import List
from core.database import async_session
from sqlalchemy import select, update
from .irepository import BaseRepository


class SQLAlchemyRepository(BaseRepository):
    _model = None
    _async_session = async_session()

    @classmethod
    async def add(cls, **kwargs):
        async with cls._async_session as session:
            obj = cls._model(**kwargs)
            session.add(obj)
            await session.commit()
            return obj

    @classmethod
    async def get(cls, *args):
        async with cls._async_session as session:
            statement = select(cls._model).where(*args)
            res = await session.scalar(statement)
            return res

    @classmethod
    async def delete(cls, obj):
        async with cls._async_session as session:
            await session.delete(obj)
            await session.commit()

    @classmethod
    async def update(cls, *args, **kwargs):
        async with cls._async_session as session:
            statement = update(cls._model).where(*args).values(**kwargs).returning(cls._model)
            res = await session.scalar(statement)
            await session.commit()
            return res

    @classmethod
    async def select(cls, *args):
        async with cls._async_session as session:
            statement = select(cls._model).where(*args)
            res = await session.execute(statement)
            return res.scalars().all()

    @classmethod
    async def get_with_options(cls, load_options, *args):
        async with cls._async_session as session:
            statement = select(cls._model).where(*args).options(*load_options)
            res = await session.scalar(statement)
            return res

    @classmethod
    async def select_with_options(cls, load_options, *args):
        async with cls._async_session as session:
            statement = select(cls._model).where(*args).options(*load_options)
            res = await session.execute(statement)
            return res.scalars().all()

    @classmethod
    async def select_join(cls, join_models: List, *filters):
        async with cls._async_session as session:
            statement = select(cls._model, *[model.get('target') for model in join_models])
            for model in join_models:
                statement = statement.join(**model)
            statement = statement.where(*filters)
            res = await session.execute(statement)
        return [x[0] for x in res.fetchall()]
