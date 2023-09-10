from typing import Optional, Literal
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, model_validator, field_validator, FieldValidationInfo
import re


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: UUID
    email: Optional[EmailStr]
    personal_data: Optional['UserAccountInfo']


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    password_repeat: str

    @classmethod
    @field_validator('password', 'password_repeat')
    def validate_length(cls, field: str, info: FieldValidationInfo) -> str:
        if len(field) < 8:
            raise ValueError(f'{info.field_name} length must be at least 8 characters')
        return field

    @model_validator(mode='after')
    def validate_passwords(self) -> 'UserCreateSchema':
        if self.password != self.password_repeat:
            raise ValueError('passwords do not match')
        return self


class Error(BaseModel):
    field_name: str
    exception: str


class RefreshSessionSchema(BaseModel):
    user_id: str
    user_agent: str
    expires_in: int
    created_at: Optional[datetime]


class UserAccountInfo(BaseModel):
    first_name: Optional[str]
    patronymic: Optional[str]
    surname: Optional[str]
    sex: Optional[Literal['male', 'female']] = "'male' or 'female'"
    birthday: Optional[date]
    bio: Optional[str]
    phone_number: Optional[str]
    tg_nickname: Optional[str]

    @classmethod
    @field_validator('phone_number')
    def validate_phone_number(cls, phone: str, info: FieldValidationInfo):
        if re.match('^\\+?[1-9][0-9]{7,14}$', phone):
            return phone
        raise ValueError(f'{info.field_name} must be a correct phone number')
