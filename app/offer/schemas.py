from pydantic import BaseModel, field_validator, FieldValidationInfo
from datetime import datetime
from typing import Optional, List
from auth.schemas import UserRead, PersonalDataSchema
from uuid import UUID
from core.config import FILE_LINKS_DOMAIN


class OfferSchema(BaseModel):
    title: str = 'Offer\'s name'
    description: str = 'Offer\'s description'
    category_id: str = 'Offer\'s category id'
    type_id: str = 'Offer\'s type id'
    deadline: Optional[datetime]
    is_anonymous: bool = False


class OfferUpdate(BaseModel):
    title: Optional[str] = 'Order\'s name'
    description: Optional[str] = 'Order\'s description'
    category_id: Optional[str] = 'Order\'s category'
    type_id: Optional[str] = 'Order\'s type'
    is_anonymous: Optional[bool] = False


class OfferInternal(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    title: str
    description: str
    category_id: UUID
    type_id: UUID
    is_anonymous: bool
    is_closed: bool
    deadline: datetime
    created_at: datetime

    files: Optional[List['FileRead']]


class OfferPublic(OfferInternal):
    user: Optional[UserRead]

    @classmethod
    def offer_public_view(cls, offer):
        return cls(
            id=offer.id,
            user_id=None if offer.is_anonymous else offer.user_id,
            title=offer.title,
            description=offer.description,
            category_id=offer.category_id,
            type_id=offer.type_id,
            is_anonymous=offer.is_anonymous,
            is_closed=offer.is_closed,
            deadline=offer.deadline,
            created_at=offer.created_at,
            user=UserRead(
                id=offer.user.id,
                email=offer.user.email,
                personal_data=PersonalDataSchema(
                    first_name=offer.user.personal_data.first_name,
                    patronymic=offer.user.personal_data.patronymic,
                    surname=offer.user.personal_data.surname,
                    tg_nickname=offer.user.personal_data.tg_nickname
                ) if offer.user.personal_data else None
            ) if not offer.is_anonymous else None,
            files=[FileRead.file_view(file) for file in offer.files]
        )


class OfferPrivate(OfferInternal):
    executors: List['ExecutorInternal']

    @classmethod
    def offer_private_view(cls, offer):
        return cls(
            id=offer.id,
            user_id=offer.user_id,
            title=offer.title,
            description=offer.description,
            category_id=offer.category_id,
            type_id=offer.type_id,
            is_anonymous=offer.is_anonymous,
            is_closed=offer.is_closed,
            deadline=offer.deadline,
            created_at=offer.created_at,
            files=[FileRead.file_view(file) for file in offer.files],
            executors=[
                ExecutorInternal(
                    id=executor.id,
                    user_id=executor.user_id,
                    offer_id=executor.offer_id,
                    is_approved=executor.is_approved,
                    user=UserRead(
                        id=executor.user.id,
                        email=executor.user.email,
                        personal_data=PersonalDataSchema(
                            first_name=executor.user.personal_data.first_name,
                            patronymic=executor.user.personal_data.patronymic,
                            surname=executor.user.personal_data.surname,
                            bio=executor.user.personal_data.bio,
                            tg_nickname=executor.user.personal_data.tg_nickname
                        ) if executor.user.personal_data else None,
                    )
                ) for executor in offer.executors
            ]
        )


class ExecutorInternal(BaseModel):
    id: UUID
    user_id: UUID
    offer_id: UUID
    is_approved: bool
    user: Optional[UserRead]


class FileSchema(BaseModel):
    description: Optional[str]
    link: Optional[str]

    @classmethod
    @field_validator('description')
    def validate_description(cls, field: str, info: FieldValidationInfo) -> str:
        if len(field) > 255:
            raise ValueError(f'{info.field_name} must be less than 256 symbols')
        return field

    @classmethod
    @field_validator('link')
    def validate_link(cls, field: str, info: FieldValidationInfo) -> str:
        for link in FILE_LINKS_DOMAIN:
            if field.startswith(link):
                return field
        raise ValueError(f'{info.field_name} must be in available domain list')


class FileRead(FileSchema):
    id: UUID
    offer_id: UUID

    @classmethod
    def file_view(cls, file):
        return cls(
            id=file.id,
            offer_id=file.offer_id,
            link=file.link,
            description=file.description
        )
