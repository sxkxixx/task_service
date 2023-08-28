from pydantic import BaseModel, field_validator, FieldValidationInfo
from datetime import datetime
from typing import Optional


class OfferSchema(BaseModel):
    title: str = 'Order\'s name'
    description: str = 'Order\'s description'
    category_id: str = 'Order\'s category id'
    type_id: str = 'Order\'s type id'
    deadline: Optional[datetime]
    is_anonymous: bool = False


class OfferUpdate(BaseModel):
    title: Optional[str] = 'Order\'s name'
    description: Optional[str] = 'Order\'s description'
    category_id: Optional[str] = 'Order\'s category'
    type_id: Optional[str] = 'Order\'s type'
    is_anonymous: Optional[bool] = False


class FileSchema(BaseModel):
    description: Optional[str]
    link: str

    @classmethod
    @field_validator('description')
    def validate_description(cls, field: str, info: FieldValidationInfo) -> str:
        if len(field) > 255:
            raise ValueError(f'{info.field_name} must\' be less than 256 symbols')
        return field

    @classmethod
    @field_validator('link')
    def validate_link(cls, field: str, info: FieldValidationInfo) -> str:
        return field


class FileRead(FileSchema):
    id: str
    offer_id: str
