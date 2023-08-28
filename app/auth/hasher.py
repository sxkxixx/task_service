from core.config import ACCESS_TOKEN_TTL_MINUTES, REFRESH_TOKEN_TTL_DAYS
from fastapi import Header, Response, Depends, HTTPException
from repositories.services import Service, UserService
from repositories.dependencies import user_service
from core.config import SECRET_KEY, ALGORITHM
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Literal, Annotated
from jose import jwt, JWTError
from auth.models import User
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
    def get_access_token(cls, user):
        return cls._get_encode_token(user, 'access_token', timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES))

    @staticmethod
    def get_token_payload(token):
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload


class AuthDependency:
    def __init__(self, is_strict=True):
        self.is_strict = is_strict
        self.service: UserService = user_service()

    async def __call__(self, authorization: Annotated[str, Header()] = None):
        if self.is_strict:
            return await self.__strict_auth(authorization)
        return await self.__soft_auth(authorization)

    async def __strict_auth(self, authorization: str):
        if not authorization:
            raise HTTPException(status_code=401, detail='No access token')
        try:
            payload = Token.get_token_payload(authorization)
        except JWTError as e:
            raise HTTPException(status_code=401, detail=e.__str__())
        expires_in = datetime.fromtimestamp(float(payload.get('exp')))
        if expires_in < datetime.utcnow():
            raise HTTPException(status_code=401, detail='Access token has expired')
        user = await self.service.get(User.email == payload.get('email'))
        if not user:
            return Response('Unauthorized', status_code=401)
        return user

    async def __soft_auth(self, authorization: str):
        try:
            return await self.__strict_auth(authorization)
        except HTTPException:
            return None
