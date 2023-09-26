from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from offer.models import Offer
from datetime import datetime
from typing import List
import sqlalchemy


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    chat_name: Mapped[str] = mapped_column(sqlalchemy.String(255))
    offer_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('offers.id', ondelete='CASCADE'))
    executor_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('executors.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.utcnow)

    offer: Mapped['Offer'] = relationship('Offer', backref='chats')
    messages: Mapped[List['Message']] = relationship('Message', back_populates='chat')


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    recipient_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    chat_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('chats.id', ondelete='CASCADE'))
    content: Mapped[str] = mapped_column(sqlalchemy.String(255))
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, default=datetime.utcnow)

    chat: Mapped['Chat'] = relationship('Chat', back_populates='messages')

