from typing import Union

from dao.services import *
from dao.repositories.repositories import *

__all__ = [
    'user_service',
    'offer_service',
    'category_service',
    'offer_type_service',
    'personal_data_service',
    'executor_service',
    'file_service',
    'chat_service',
    'message_service',
    'user_verify_service',
    'password_upd_service',
]


def user_service() -> Union[UserService, BaseService]:
    return UserService(UserRepository)


def offer_service() -> Union[OfferService, BaseService]:
    return OfferService(OfferRepository)


def category_service() -> Union[CategoryService, BaseService]:
    return CategoryService(CategoryRepository)


def offer_type_service() -> Union[OfferTypeService, BaseService]:
    return OfferTypeService(OfferTypeRepository)


def personal_data_service() -> Union[PersonalDataService, BaseService]:
    return PersonalDataService(PersonalDataRepository)


def executor_service() -> Union[ExecutorService, BaseService]:
    return ExecutorService(ExecutorRepository)


def file_service() -> Union[FileService, BaseService]:
    return FileService(FileRepository)


def chat_service() -> Union[ChatService, BaseService]:
    return ChatService(ChatRepository)


def message_service() -> Union[MessageService, BaseService]:
    return MessageService(MessageRepository)


def user_verify_service() -> Union[UserVerifyService, BaseService]:
    return UserVerifyService(UserVerifyRepository)


def password_upd_service() -> Union[PasswordUpdateService, BaseService]:
    return PasswordUpdateService(PasswordUpdateRepository)
