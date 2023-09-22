from repositories.dependencies import user_service, user_account_service
from repositories.services import UserService, UserAccountService
from fastapi import APIRouter, Depends, HTTPException, Response, Header, Cookie
from auth.schemas import UserCreateSchema, UserLogin, Error, UserAccountInfo
from auth.hasher import Token, Hasher, AuthDependency
from auth.models import UserAccount
from auth.models import User
from typing import Annotated
from auth.refresh_session import RefreshSession

auth = APIRouter(prefix='/api/v1')


@auth.post('/auth/token', tags=['AUTH'])
async def get_token(
        _user: UserLogin,
        response: Response,
        user_agent: Annotated[str, Header()],
        _user_service: UserService = Depends(user_service),
):
    user: User = await _user_service.get(User.email == _user.email)
    if not user:
        raise HTTPException(status_code=404, detail='User does not found by this email')
    if not Hasher.is_correct_password(_user.password, user.password):
        raise HTTPException(status_code=403, detail='Incorrect password for user')
    access = Token.get_access_token(user)
    refresh_session = RefreshSession(_id=None, user_id=user.id, user_agent=user_agent, created_at=None)
    await refresh_session.push()
    response.set_cookie(
        'refresh_token',
        refresh_session.get_refresh_id,
        httponly=True,
        path='/api/v1/auth',
        max_age=refresh_session.expires_in)
    return access


@auth.post('/auth/token/refresh', tags=['AUTH'])
async def _refresh_token(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        _user_service: UserService = Depends(user_service),
):
    refresh_session: RefreshSession = await RefreshSession.get(refresh_token)
    if not refresh_session or refresh_session.ua != user_agent:
        return Response("Redirect to /login page", status_code=302)
    await refresh_session.delete()
    user = await _user_service.get(User.id == refresh_session.user_id)
    access = Token.get_access_token(user)
    refresh_session: RefreshSession = RefreshSession(_id=None, user_id=user.id, user_agent=user_agent, created_at=None)
    await refresh_session.push()
    response.set_cookie(
        'refresh_token',
        refresh_session.get_refresh_id,
        httponly=True,
        path='/api/v1/auth',
        expires=refresh_session.expires_in
    )
    return access


@auth.post('/auth/logout', tags=['AUTH'])
async def logout(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        user: User = Depends(AuthDependency()),
):
    refresh_session: RefreshSession = await RefreshSession.get(refresh_token)
    if refresh_session.ua != user_agent or user.id != refresh_session.user_id:
        return Response('Bad User-Agent and User for Refresh Session', status_code=400)
    response.delete_cookie('refresh_token')
    await refresh_session.delete()
    return {'user': user.id, 'status': 'logged out'}


@auth.post('/user/create_user', tags=['USER'])
async def create_user(
        user: UserCreateSchema,
        _user_service: UserService = Depends(user_service),
        _user_info_service: UserAccountService = Depends(user_account_service)

) -> dict | Error:
    user: User = await _user_service.add(
        UserLogin(email=user.email, password=Hasher.get_password_hash(user.password)))
    if isinstance(user, Error):
        return user
    await _user_info_service.add(id=user.id)
    return {'email': user.email, 'status': 'created'}


@auth.put('/user/user_info/update', tags=['USER'])
async def update_user_info(
        info: UserAccountInfo,
        _user_account_service: UserAccountService = Depends(user_account_service),
        user: User = Depends(AuthDependency()),
):
    user_info: UserAccount = await _user_account_service.update(user.id, **info.model_dump())
    return user_info


@auth.delete('/user/delete_user', tags=['USER'])
async def delete_user(
        user: User = Depends(AuthDependency()),
        _user_service: UserService = Depends(user_service)
):
    await _user_service.delete(user)
    return {'id': user.id, 'status': 'deleted'}
