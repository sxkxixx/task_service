from repositories.base import DatabaseRepository
from auth.models import User, RefreshSession, UserAccount
from offer.models import Offer, Category, OfferType, Executor, FileOffer


class UserRepository(DatabaseRepository):
    _model = User


class RefreshSessionRepository(DatabaseRepository):
    _model = RefreshSession


class OfferRepository(DatabaseRepository):
    _model = Offer


class CategoryRepository(DatabaseRepository):
    _model = Category


class OfferTypeRepository(DatabaseRepository):
    _model = OfferType


class UserAccountRepository(DatabaseRepository):
    _model = UserAccount


class ExecutorRepository(DatabaseRepository):
    _model = Executor


class FileRepository(DatabaseRepository):
    _model = FileOffer

