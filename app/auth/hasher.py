from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Hasher:
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def is_correct_password(password, hash_password):
        return pwd_context.verify(password, hash_password)