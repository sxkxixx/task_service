from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from auth.models import User
from core.database import Base
from datetime import datetime
from uuid import uuid4
import sqlalchemy


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sqlalchemy.String(50), unique=True)

    category_offers: Mapped[List['Offer']] = relationship('Offer', back_populates='category')


class OfferStatus(Base):
    __tablename__ = 'offer_status'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    status: Mapped[str] = mapped_column(sqlalchemy.String(50), unique=True)

    status_offers: Mapped[List['Offer']] = relationship('Offer', back_populates='status')


class OfferType(Base):
    __tablename__ = 'offer_type'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(sqlalchemy.String(20), unique=True)

    type_offers: Mapped[List['Offer']] = relationship('Offer', back_populates='type')


class Offer(Base):
    __tablename__ = 'offers'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(sqlalchemy.String(80))
    description: Mapped[str] = mapped_column(sqlalchemy.String(256))
    s3_filename: Mapped[str] = mapped_column(sqlalchemy.String(256), unique=True, nullable=True)
    category_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('categories.id'))
    type_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offer_type.id'))
    is_anonymous: Mapped[bool] = mapped_column(sqlalchemy.Boolean)
    is_premium: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.utcnow)
    status_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offer_status.id'))

    status: Mapped['OfferStatus'] = relationship('OfferStatus', back_populates='status_offers')
    category: Mapped['Category'] = relationship('Category', back_populates='category_offers')
    type: Mapped['OfferType'] = relationship('OfferType', back_populates='type_offers')
    executors: Mapped[List['Executor']] = relationship('Executor', back_populates='offer')


class Executor(Base):
    __tablename__ = 'executors'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    offer_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offers.id', ondelete='CASCADE'))
    is_approved: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)

    user: Mapped['User'] = relationship('User', back_populates='offer_executor')
    offer: Mapped['Offer'] = relationship('Offer', back_populates='executors')
