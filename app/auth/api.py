from repositories.dependencies import user_service, session_service, user_account_service
from repositories.services import UserService, SessionService, UserAccountService
from fastapi import APIRouter, Depends, HTTPException, Response, Header, Cookie
from auth.schemas import UserCreateSchema, UserLogin, Error, UserAccountInfo
from auth.hasher import Token, Hasher, AuthDependency
from auth.models import RefreshSession, UserAccount
from sqlalchemy.orm import selectinload
from datetime import datetime
from auth.models import User
from typing import Annotated

auth = APIRouter(prefix='/api/v1/auth')


@auth.post('/create_user', tags=['USER'])
async def create_user(user: UserCreateSchema, service: UserService = Depends(user_service)) -> dict | Error:
    user: User = await service.add(
        UserLogin(email=user.email, password=Hasher.get_password_hash(user.password)))
    if isinstance(user, Error):
        return user
    return {'email': user.email, 'status': 'created'}


@auth.post('/token', tags=['AUTH'])
async def get_token(
        _user: UserLogin,
        response: Response,
        user_agent: Annotated[str, Header()],
        _user_service: UserService = Depends(user_service),
        _session_service: SessionService = Depends(session_service)
):
    user: User = await _user_service.get(User.email == _user.email)
    if not user:
        raise HTTPException(status_code=404, detail='User does not found by this email')
    if not Hasher.is_correct_password(_user.password, user.password):
        raise HTTPException(status_code=403, detail='Incorrect password for user')
    access = Token.get_access_token(user)
    db_token: RefreshSession = await _session_service.add(user, user_agent)
    response.set_cookie('refresh_token', db_token.id, httponly=True, path='/api/v1/auth/token', max_age=db_token.expires_in)
    return access


@auth.post('/token/refresh', tags=['AUTH'])
async def _refresh_token(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        _session_service: SessionService = Depends(session_service)
):
    refresh_session: RefreshSession = await _session_service.get_with_options(
        selectinload(RefreshSession.user), RefreshSession.id == refresh_token)
    if not refresh_session:
        return Response("Redirect to /login page", status_code=302)
    await _session_service.delete(refresh_session)
    if datetime.fromtimestamp(refresh_session.expires_in) < datetime.utcnow() or refresh_session.user_agent != user_agent:
        return Response("Redirect to /login page", status_code=302)
    user = refresh_session.user
    access = Token.get_access_token(user)
    db_token: RefreshSession = await _session_service.add(user, user_agent)
    response.set_cookie('refresh_token', db_token.id, httponly=True, path='/api/v1/auth', expires=db_token.expires_in)
    return access


@auth.post('/logout', tags=['AUTH'])
async def logout(
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        user: User = Depends(AuthDependency()),
        _session_service: SessionService = Depends(session_service)
):
    session = await _session_service.get(RefreshSession.user_id == user.id,
                                         RefreshSession.user_agent == user_agent,
                                         RefreshSession.id == refresh_token)
    await _session_service.delete(session)
    return {'user': user.id, 'status': 'logged out'}


@auth.post('/user_info', tags=['USER'])
async def append_user_info(
        info: UserAccountInfo,
        _user_account_service: UserAccountService = Depends(user_account_service),
        user: User = Depends(AuthDependency()),
):
    user_info = await _user_account_service.get(UserAccount.id == user.id)
    if user_info:
        return Response(f'{user.email}\'s account info already exists', status_code=400)
    user_info = await _user_account_service.add(id=user.id, **info.model_dump())
    return user_info


@auth.put('/user_info/update', tags=['USER'])
async def update_user_info(
        info: UserAccountInfo,
        _user_account_service: UserAccountService = Depends(user_account_service),
        user: User = Depends(AuthDependency()),
):
    user_info = await _user_account_service.update(user.id, **info.model_dump())
    return user_info


@auth.delete('/delete_user', tags=['USER'])
async def delete_user(
        user: User = Depends(AuthDependency()),
        _user_service: UserService = Depends(user_service)
):
    await _user_service.delete(user)
    return {'id': user.id, 'status': 'deleted'}
