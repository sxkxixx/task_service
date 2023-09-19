from pydantic import BaseModel, field_validator, FieldValidationInfo
from typing import Literal, Optional, Any
from datetime import datetime
from uuid import UUID
import json


class ChatSchema(BaseModel):
    offer_id: UUID
    executor_id: UUID
    chat_name: str


class ChatReadSchema(ChatSchema):
    id: UUID
    created_at: datetime


class MessageSchema(BaseModel):
    content: str
    recipient_id: UUID

    @classmethod
    @field_validator('content')
    def length_validate(cls, field: str, info: FieldValidationInfo) -> str:
        if len(field) > 255:
            raise ValueError(f'{info.field_name} length must be at least 255 characters')
        return field


class Notification:
    def __init__(self, **kwargs):
        self.event: Literal['message', 'service_notify'] = kwargs.get('event')
        self.user_id: UUID = kwargs.get('user_id')
        self.source: Optional[dict[str, Any]] = kwargs.get('source')
        self.description: str = kwargs.get('description')

    def __str__(self):
        return json.dumps(
            {
                'event': self.event,
                'user_id': self.user_id,
                'source': self.source,
                'description': self.description,
            }, default=str
        )
