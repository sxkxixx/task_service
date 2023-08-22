from auth.models import User
from core.config import ACCESS_TOKEN_TTL_MINUTES, REFRESH_TOKEN_TTL_DAYS
from repositories.dependencies import user_service
from fastapi import Header, Response, Depends, HTTPException
from core.config import SECRET_KEY, ALGORITHM
from repositories.services import Service
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Literal, Annotated
from jose import jwt, JWTError
from functools import wraps

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Hasher:
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def is_correct_password(password, hash_password):
        return pwd_context.verify(password, hash_password)


class Token:
    @staticmethod
    def _get_encode_token(user, token_type: Literal['access_token', 'refresh_token'], expires_in: timedelta):
        payload = {'email': user.email, 'sub': token_type}
        token_exp = datetime.utcnow() + expires_in
        payload.update({'exp': token_exp})
        return jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)

    @classmethod
    def get_tokens_pair(cls, user):
        return (
            cls._get_encode_token(user, 'access_token', timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)),
            cls._get_encode_token(user, 'refresh_token', timedelta(days=REFRESH_TOKEN_TTL_DAYS))
        )

    @staticmethod
    def get_token_payload(token):
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload


# TODO: не работает
def auth_required(func, service: Service = Depends(user_service)):
    @wraps(func)
    async def wrapper(authorization: Annotated[str, Header()] = None, *args, **kwargs):
        if not authorization:
            raise HTTPException(status_code=401, detail="Unauthorized")
        try:
            payload = Token.get_token_payload(authorization)
        except JWTError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        email = payload.get('email')
        user = await service.get_by_filter(email=email)
        if not user:
            return Response("Unauthorized", status_code=401)
        func_result = await func(*args, **kwargs)
        return func_result
    return wrapper


async def auth_dependency(authorization: Annotated[str, Header()] = None, service: Service = Depends(user_service)):
    if not authorization:
        raise HTTPException(status_code=401, detail='No access token token')
    try:
        payload = Token.get_token_payload(authorization)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=e.__str__())
    expires_in = datetime.fromtimestamp(float(payload.get('exp')))
    if expires_in < datetime.utcnow():
        raise HTTPException(status_code=401, detail='Access token has expired')
    user = await service.get_by_filter(User.email == payload.get('email'))
    if not user:
        return Response('Unauthorized', status_code=401)
    return user
