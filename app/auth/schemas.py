from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, model_validator, field_validator, FieldValidationInfo
import re


class UserLogin(BaseModel):
    email: EmailStr
    password: str


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
    first_name: str
    patronymic: str
    surname: str
    phone_number: Optional[str] = None
    tg_nickname: Optional[str] = None

    @classmethod
    @field_validator('phone_number')
    def validate_phone_number(cls, phone: str, info: FieldValidationInfo):
        if re.match('^\\+?[1-9][0-9]{7,14}$', phone):
            return phone
        raise ValueError(f'{info.field_name} must be a correct phone number')
