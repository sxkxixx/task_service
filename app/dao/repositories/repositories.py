from .sqlalchemy_repository import SQLAlchemyRepository
from auth.models import User, PersonalData, UserVerifyInfo, PasswordUpdate
from offer.models import Offer, Category, OfferType, Executor, FileOffer
from chat.models import Chat, Message

__all__ = [
    'UserRepository',
    'OfferRepository',
    'CategoryRepository',
    'OfferTypeRepository',
    'PersonalDataRepository',
    'ExecutorRepository',
    'FileRepository',
    'ChatRepository',
    'MessageRepository',
    'UserVerifyRepository',
    'PasswordUpdateRepository',
]


class UserRepository(SQLAlchemyRepository):
    _model = User


class OfferRepository(SQLAlchemyRepository):
    _model = Offer


class CategoryRepository(SQLAlchemyRepository):
    _model = Category


class OfferTypeRepository(SQLAlchemyRepository):
    _model = OfferType


class PersonalDataRepository(SQLAlchemyRepository):
    _model = PersonalData


class ExecutorRepository(SQLAlchemyRepository):
    _model = Executor


class FileRepository(SQLAlchemyRepository):
    _model = FileOffer


class ChatRepository(SQLAlchemyRepository):
    _model = Chat


class MessageRepository(SQLAlchemyRepository):
    _model = Message


class UserVerifyRepository(SQLAlchemyRepository):
    _model = UserVerifyInfo


class PasswordUpdateRepository(SQLAlchemyRepository):
    _model = PasswordUpdate
