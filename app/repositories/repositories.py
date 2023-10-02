from repositories.base import DatabaseRepository
from auth.models import User, PersonalData, UserVerifyInfo
from offer.models import Offer, Category, OfferType, Executor, FileOffer
from chat.models import Chat, Message


class UserRepository(DatabaseRepository):
    _model = User


class OfferRepository(DatabaseRepository):
    _model = Offer


class CategoryRepository(DatabaseRepository):
    _model = Category


class OfferTypeRepository(DatabaseRepository):
    _model = OfferType


class PersonalDataRepository(DatabaseRepository):
    _model = PersonalData


class ExecutorRepository(DatabaseRepository):
    _model = Executor


class FileRepository(DatabaseRepository):
    _model = FileOffer


class ChatRepository(DatabaseRepository):
    _model = Chat


class MessageRepository(DatabaseRepository):
    _model = Message


class UserVerifyRepository(DatabaseRepository):
    _model = UserVerifyInfo
