from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from datetime import datetime
from uuid import uuid4
import sqlalchemy


class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(sqlalchemy.String(length=100), unique=True)
    password: Mapped[str] = mapped_column(sqlalchemy.String(length=150))
    is_verified: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)

    refresh_session = relationship('RefreshSession', back_populates='user')
    personal_data = relationship('UserAccount', backref='personal_data')

    def __repr__(self):
        return f'User(id={self.id}, email={self.email})'


class UserAccount(Base):
    __tablename__ = 'user_account'

    id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    first_name: Mapped[str] = mapped_column(sqlalchemy.String(50))
    patronymic: Mapped[str] = mapped_column(sqlalchemy.String(50))
    surname: Mapped[str] = mapped_column(sqlalchemy.String(50))
    phone_number: Mapped[str] = mapped_column(sqlalchemy.String(16), nullable=True)
    tg_nickname: Mapped[str] = mapped_column(sqlalchemy.String(40), nullable=True)


class RefreshSession(Base):
    __tablename__ = 'refresh_session'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    user_agent: Mapped[str] = mapped_column(sqlalchemy.String(200))
    refresh_token: Mapped[str] = mapped_column(sqlalchemy.String(200))
    expires_in: Mapped[int] = mapped_column(sqlalchemy.BigInteger)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime(timezone=True), default=datetime.now)

    user = relationship('User', back_populates='refresh_session')

    def __repr__(self):
        return f'RefreshSession(id={self.id}, user_id={self.user_id})'
