from repositories.services import Service
from repositories.repositories import (
    UserRepository,
    OfferRepository,
    CategoryRepository,
    OfferTypeRepository,
    PersonalDataRepository,
    ExecutorRepository,
    FileRepository,
    ChatRepository,
    MessageRepository, UserVerifyRepository
)


def user_service() -> Service:
    return Service(UserRepository)


def offer_service() -> Service:
    return Service(OfferRepository)


def category_service() -> Service:
    return Service(CategoryRepository)


def offer_type_service() -> Service:
    return Service(OfferTypeRepository)


def personal_data_service() -> Service:
    return Service(PersonalDataRepository)


def executor_service() -> Service:
    return Service(ExecutorRepository)


def file_service() -> Service:
    return Service(FileRepository)


def chat_service() -> Service:
    return Service(ChatRepository)


def message_service() -> Service:
    return Service(MessageRepository)


def user_verify_service() -> Service:
    return Service(UserVerifyRepository)
