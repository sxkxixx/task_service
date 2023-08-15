from abc import ABC, abstractmethod
from core.database import async_session, Base
from sqlalchemy import select, update


class BaseRepository(ABC):
    @abstractmethod
    async def add(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def select(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_with_options(self, *args, **kwargs):
        pass


class DatabaseRepository(BaseRepository):
    _model: Base = None

    @classmethod
    async def add(cls, **kwargs):
        async with async_session() as session:
            obj = cls._model(**kwargs)
            session.add(obj)
            await session.commit()
            return obj

    @classmethod
    async def get(cls, load_option=None, **kwargs):
        async with async_session() as session:
            statement = select(cls._model).filter_by(**kwargs)
            res = await session.scalar(statement)
            return res

    @classmethod
    async def delete(cls, obj):
        async with async_session() as session:
            await session.delete(obj)
            await session.commit()

    @classmethod
    async def update(cls, obj_id, **kwargs):
        async with async_session() as session:
            statement = update(cls._model).filter_by(id=obj_id).values(**kwargs).returning(cls._model)
            res = await session.scalar(statement)
            await session.commit()
            return res

    @classmethod
    async def select(cls, *join_models, **kwargs):
        async with async_session() as session:
            statement = select(cls._model)
            if join_models:
                for model in join_models:
                    statement = statement.join(model)
            statement = statement.filter_by(**kwargs)
            res = await session.execute(statement)
            return [x[0] for x in res.fetchall()]

    @classmethod
    async def get_with_options(cls, load_option=None, **kwargs):
        async with async_session() as session:
            statement = select(cls._model).filter_by(**kwargs).options(load_option)
            res = await session.scalar(statement)
            return res