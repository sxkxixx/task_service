from pydantic import BaseModel
from typing import Optional


class OfferSchema(BaseModel):
    title: str = 'Order\'s name'
    description: str = 'Order\'s description'
    category_id: str = 'Order\'s category id'
    type_id: str = 'Order\'s type id'
    is_anonymous: bool = False
    status_id: str = "Order\'s status id"


class OfferUpdate(BaseModel):
    title: Optional[str] = 'Order\'s name'
    description: Optional[str] = 'Order\'s description'
    category_id: Optional[str] = 'Order\'s category'
    type_id: Optional[str] = 'Order\'s type'
    is_anonymous: Optional[bool] = False
    status_id: str = "Order\'s status id"
