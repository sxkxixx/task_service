from pydantic import BaseModel, field_validator, FieldValidationInfo
from typing import Optional, Literal


class OfferSchema(BaseModel):
    title: str = 'Order\'s name'
    description: str = 'Order\'s description'
    category_id: str = 'Order\'s category id'
    type_id: str = 'Order\'s type id'
    cost: Optional[float]
    is_anonymous: bool = False
    status_id: str = "Order\'s status id"

    @classmethod
    @field_validator('cost')
    def validate_cost(cls, cost: float, info: FieldValidationInfo):
        if cost < 0:
            raise ValueError(f'{info.field_name} must not be less than zero')
        return cost


class OfferUpdate(BaseModel):
    title: Optional[str] = 'Order\'s name'
    description: Optional[str] = 'Order\'s description'
    category_id: Optional[str] = 'Order\'s category'
    type_id: Optional[str] = 'Order\'s type'
    cost: Optional[float]
    is_anonymous: Optional[bool] = False
    status_id: str = "Order\'s status id"


    @classmethod
    @field_validator('cost')
    def validate_cost(cls, cost: float, info: FieldValidationInfo):
        if cost < 0:
            raise ValueError(f'{info.field_name} must not be less than zero')
        return cost
