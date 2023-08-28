from repositories.services import (
    UserService,
    SessionService,
    OfferService,
    UserAccountService,
    ExecutorService,
    ReadOnlyService,
    FileService
)
from repositories.repositories import (
    UserRepository,
    RefreshSessionRepository,
    OfferRepository,
    CategoryRepository,
    OfferTypeRepository,
    UserAccountRepository,
    ExecutorRepository,
    FileRepository
)


def user_service() -> UserService:
    return UserService(UserRepository)


def session_service() -> SessionService:
    return SessionService(RefreshSessionRepository)


def offer_service() -> OfferService:
    return OfferService(OfferRepository)


def category_service() -> ReadOnlyService:
    return ReadOnlyService(CategoryRepository)


def offer_type_service() -> ReadOnlyService:
    return ReadOnlyService(OfferTypeRepository)


def user_account_service() -> UserAccountService:
    return UserAccountService(UserAccountRepository)


def executor_service() -> ExecutorService:
    return ExecutorService(ExecutorRepository)


def file_service() -> FileService:
    return FileService(FileRepository)
