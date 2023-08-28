from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship
from repositories.s3_service import S3Service
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from auth.models import User
from datetime import datetime
from typing import List
from uuid import uuid4
import sqlalchemy


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sqlalchemy.String(50), unique=True)

    category_offers: Mapped[List['Offer']] = relationship('Offer', back_populates='category')


class OfferType(Base):
    __tablename__ = 'offer_type'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(sqlalchemy.String(20), unique=True)

    type_offers: Mapped[List['Offer']] = relationship('Offer', back_populates='type')


class Offer(Base, AsyncAttrs):
    __tablename__ = 'offers'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(sqlalchemy.String(80))
    description: Mapped[str] = mapped_column(sqlalchemy.String(256))
    s3_filename: Mapped[str] = mapped_column(sqlalchemy.String(256), unique=True, nullable=True)
    category_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('categories.id'))
    type_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offer_type.id'))
    is_anonymous: Mapped[bool] = mapped_column(sqlalchemy.Boolean)
    is_closed: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.utcnow)

    category: Mapped['Category'] = relationship('Category', back_populates='category_offers')
    type: Mapped['OfferType'] = relationship('OfferType', back_populates='type_offers')
    executors: Mapped[List['Executor']] = relationship('Executor', back_populates='offer')

    @property
    async def s3_file(self):
        if self.s3_filename:
            return await S3Service.get_presigned_url(self.s3_filename)
        return None


class Executor(Base):
    __tablename__ = 'executors'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    offer_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offers.id', ondelete='CASCADE'))
    is_approved: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)

    user: Mapped['User'] = relationship('User', back_populates='offer_executor')
    offer: Mapped['Offer'] = relationship('Offer', back_populates='executors')
