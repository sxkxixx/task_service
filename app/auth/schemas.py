from pydantic import BaseModel, EmailStr, field_validator, FieldValidationInfo
from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID
import re


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: UUID
    email: Optional[EmailStr]
    personal_data: Optional['PersonalDataSchema']


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    @field_validator('password', 'password_repeat')
    def validate_length(cls, field: str, info: FieldValidationInfo) -> str:
        if len(field) < 8:
            raise ValueError(f'{info.field_name} length must be at least 8 characters')
        return field

    @classmethod
    @field_validator('email')
    def validate_email(cls, field: str, info: FieldValidationInfo):
        return field.strip().lower()


class Error(BaseModel):
    field_name: str
    exception: str


class RefreshSessionSchema(BaseModel):
    user_id: str
    user_agent: str
    expires_in: int
    created_at: Optional[datetime]


class PersonalDataSchema(BaseModel):
    first_name: Optional[str]
    patronymic: Optional[str]
    surname: Optional[str]
    sex: Optional[Literal['male', 'female']] = None
    birthday: Optional[date] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    tg_nickname: Optional[str]

    @classmethod
    @field_validator('phone_number')
    def validate_phone_number(cls, phone: str, info: FieldValidationInfo):
        if re.match('^\\+?[1-9][0-9]{7,14}$', phone):
            return phone
        raise ValueError(f'{info.field_name} must be a correct phone number')

    @classmethod
    @field_validator('tg_nickname')
    def validate_telegram_nickname(cls, field: str, info: FieldValidationInfo):
        if not field:
            return field
        if not field.startswith('@'):
            return ValueError(f'{info.field_name} must be starts with a "@"')
        return field
