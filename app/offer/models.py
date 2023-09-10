from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
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
    category_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('categories.id'))
    type_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offer_type.id'))
    is_anonymous: Mapped[bool] = mapped_column(sqlalchemy.Boolean)
    is_closed: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)
    deadline: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.utcnow)

    category: Mapped['Category'] = relationship('Category', back_populates='category_offers')
    type: Mapped['OfferType'] = relationship('OfferType', back_populates='type_offers')
    executors: Mapped[List['Executor']] = relationship('Executor', back_populates='offer')
    user: Mapped['User'] = relationship('User', backref='offers')

    def __repr__(self):
        return f'Offer(id={self.id})'


class FileOffer(Base):
    __tablename__ = 'offer_files'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    offer_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offers.id', ondelete='CASCADE'))
    link: Mapped[str] = mapped_column(sqlalchemy.String(150), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.String(255), nullable=True)

    offer: Mapped['Offer'] = relationship('Offer', backref='files')


class Executor(Base):
    __tablename__ = 'executors'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    offer_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offers.id', ondelete='CASCADE'))
    is_approved: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)

    user: Mapped['User'] = relationship('User', back_populates='offer_executor')
    offer: Mapped['Offer'] = relationship('Offer', back_populates='executors')
