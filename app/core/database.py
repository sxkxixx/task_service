from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import SQL_DATABASE, SQL_HOST, SQL_PORT, SQL_USER, SQL_PASSWORD
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from sqlalchemy import MetaData

DATABASE_URL = f'postgresql+asyncpg://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DATABASE}'

async_engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

metadata = MetaData()


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
