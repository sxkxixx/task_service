from repositories.services import (
    UserService,
    OfferService,
    UserAccountService,
    ExecutorService,
    ReadOnlyService,
    FileService,
    ChatService,
    MessageService
)
from repositories.repositories import (
    UserRepository,
    OfferRepository,
    CategoryRepository,
    OfferTypeRepository,
    UserAccountRepository,
    ExecutorRepository,
    FileRepository,
    ChatRepository,
    MessageRepository
)


def user_service() -> UserService:
    return UserService(UserRepository)


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


def chat_service() -> ChatService:
    return ChatService(ChatRepository)


def message_service() -> MessageService:
    return MessageService(MessageRepository)