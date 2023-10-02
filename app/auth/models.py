from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from uuid import uuid4
import sqlalchemy


class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(sqlalchemy.String(length=100), unique=True)
    password: Mapped[str] = mapped_column(sqlalchemy.String(length=150))
    is_verified: Mapped[bool] = mapped_column(sqlalchemy.Boolean, default=False)

    personal_data: Mapped['PersonalData'] = relationship('PersonalData', backref='personal_data')
    offer_executor = relationship('Executor', back_populates='user')

    def __repr__(self):
        return f'User(id={self.id}, email={self.email})'


class PersonalData(Base):
    __tablename__ = 'personal_data'

    id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    first_name: Mapped[str] = mapped_column(sqlalchemy.String(50), default='Unmarked', nullable=False)
    patronymic: Mapped[str] = mapped_column(sqlalchemy.String(50), default='Unmarked', nullable=True)
    surname: Mapped[str] = mapped_column(sqlalchemy.String(50), default='Unmarked', nullable=False)
    sex: Mapped[str] = mapped_column(sqlalchemy.String(6), nullable=True)
    birthday: Mapped[date] = mapped_column(sqlalchemy.Date, nullable=True)
    bio: Mapped[str] = mapped_column(sqlalchemy.String(500), nullable=True)
    phone_number: Mapped[str] = mapped_column(sqlalchemy.String(16), nullable=True)
    tg_nickname: Mapped[str] = mapped_column(sqlalchemy.String(40), nullable=True)

    def is_correct_data(self):
        return self.first_name is not None and self.surname is not None and self.tg_nickname is not None


class PasswordUpdate(Base):
    __tablename__ = 'password_upd_token'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid4,  primary_key=True)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'))
    previous_password: Mapped[str] = mapped_column(sqlalchemy.String(length=150), nullable=False)
    current_password: Mapped[str] = mapped_column(sqlalchemy.String(length=150), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, nullable=True)


class UserVerifyInfo(Base):
    __tablename__ = 'user_verify_info'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(sqlalchemy.ForeignKey('users.id', ondelete='NO ACTION'), unique=True)
    verified_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, nullable=True)

