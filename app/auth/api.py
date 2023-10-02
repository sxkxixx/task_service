from repositories.dependencies import user_service, personal_data_service, user_verify_service
from auth.schemas import UserCreateSchema, UserLogin, Error, PersonalDataSchema, UserRead
from repositories.services import Service
from fastapi import APIRouter, Depends, Response, Header, Cookie, Body
from auth.models import PersonalData, UserVerifyInfo
from auth.hasher import Token, Hasher, AuthDependency
from auth.refresh_session import RefreshSession
from fastapi.responses import JSONResponse
from tasks.message_data import MessageData
from sqlalchemy.exc import IntegrityError
from tasks.celery import send_email_task
from typing import Annotated
from auth.models import User
import datetime

auth = APIRouter(prefix='/api/v1')


@auth.post('/auth/token', tags=['AUTH'])
async def get_token(
        _user: UserLogin,
        response: Response,
        user_agent: Annotated[str, Header()],
        _user_service: Service = Depends(user_service),
):
    user: User = await _user_service.get(User.email == _user.email)
    if not user:
        return Response('User does not found by this email', status_code=404)
    if not Hasher.is_correct_password(_user.password, user.password):
        return Response('Incorrect password for user', status_code=403)
    access = Token.get_access_token(user)
    refresh_session = RefreshSession(_id=None, user_id=user.id, user_agent=user_agent, created_at=None)
    await refresh_session.push()
    response.set_cookie(
        'refresh_token',
        refresh_session.get_refresh_id,
        httponly=True,
        path='/api/v1/auth',
        max_age=refresh_session.expires_in,
        expires=refresh_session.expires_in
    )
    return access


@auth.post('/auth/token/refresh', tags=['AUTH'])
async def _refresh_token(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        _user_service: Service = Depends(user_service),
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
        max_age=refresh_session.expires_in,
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

    if refresh_session.ua != user_agent or user.id.__str__() != refresh_session.user_id:
        return Response('Bad User-Agent and User for Refresh Session', status_code=400)
    response.delete_cookie('refresh_token')
    await refresh_session.delete()
    return {'user': user.id, 'status': 'logged out'}


@auth.post('/user', tags=['USER'], )
async def create_user(
        _user: UserCreateSchema,
        _user_service: Service = Depends(user_service),
        _personal_data_service: Service = Depends(personal_data_service)
):
    try:
        user: User = await _user_service.add(
            email=_user.email,
            password=Hasher.get_password_hash(_user.password))
    except IntegrityError:
        return JSONResponse(Error(field_name='email', exception='Email field must\'be unique for User').model_dump(),
                            status_code=400)
    await _personal_data_service.add(id=user.id)
    return UserRead(id=user.id, email=user.email, personal_data=None)


@auth.delete('/user', tags=['USER'])
async def delete_user(
        user: User = Depends(AuthDependency()),
        _user_service: Service = Depends(user_service)
):
    await _user_service.delete(user)
    return {'id': user.id, 'status': 'deleted'}


@auth.put('/user/personal_data', tags=['USER'])
async def update_personal_data(
        info: PersonalDataSchema,
        _personal_data_service: Service = Depends(personal_data_service),
        user: User = Depends(AuthDependency()),
):
    user_info: PersonalData = await _personal_data_service.update(User.id == user.id, **info.model_dump())
    return user_info


@auth.get('/email/verify', tags=['EMAILS'])
async def get_verify_mail(
        user: User = Depends(AuthDependency()),
        _personal_data_service: Service = Depends(personal_data_service),
        _user_verify_service: Service = Depends(user_verify_service)
):
    personal_data: PersonalData = await _personal_data_service.get(PersonalData.id == user.id)
    if not personal_data.is_correct_data():
        return JSONResponse({'detail': "Missing required fields 'first_name', 'surname', 'tg_nickname'"},
                            status_code=400)
    try:
        verify_info: UserVerifyInfo = await _user_verify_service.add(user_id=user.id)
    except IntegrityError:
        return JSONResponse({'error': 'User is verified'}, status_code=403)
    message_data = MessageData(
        subject='Подтверждение личного аккаунта',
        recipient_email=user.email,
        template_type='verify_email',
        token=verify_info.id
    )
    send_email_task(message_data)
    return JSONResponse({'detail': 'Verify Email is sent'})


@auth.post('/email/verify', tags=['EMAILS'])
async def verify_user(
        verify_token: str = Body(),
        user: User = Depends(AuthDependency()),
        _user_verify_service: Service = Depends(user_verify_service),
        _user_service: Service = Depends(user_service)
):
    verify_info: UserVerifyInfo = await _user_verify_service.get(
        UserVerifyInfo.id == verify_token,
        UserVerifyInfo.user_id == user.id
    )
    if not verify_info:
        return Response('Verify info not found', status_code=404)
    verify_info = await _user_verify_service.update(
        UserVerifyInfo.id == verify_info.id,
        UserVerifyInfo.user_id == user.id,
        verified_at=datetime.datetime.utcnow()
    )
    await _user_service.update(User.id == user.id, is_verified=True)
    return JSONResponse({'user': user.email, 'is_verified': True, 'verified_at': verify_info.verified_at})


