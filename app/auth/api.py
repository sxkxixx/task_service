from auth.hasher import Hasher
from dao import (
    user_service, personal_data_service, user_verify_service,
    password_upd_service, BaseService
)
from auth.schemas import (
    UserCreateSchema,
    UserLogin,
    PersonalDataSchema,
    UserRead,
    PasswordUpdateSchema, VerifyTokenSchema
)
from fastapi import APIRouter, Depends, Response, Header, Cookie, Body, \
    HTTPException
from auth.models import PersonalData, UserVerifyInfo, PasswordUpdate
from auth.auth_utils import Token, AuthDependency
from auth.refresh_session import RefreshSession
from fastapi.responses import JSONResponse
from tasks.message_data import MessageData
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
        _user_service: BaseService = Depends(user_service),
):
    user: User = await _user_service.get_user(User.email == _user.email)
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
    return {'access_token': access}


@auth.post('/auth/token/refresh', tags=['AUTH'])
async def _refresh_token(
        response: Response,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        _user_service: BaseService = Depends(user_service),
):
    refresh_session: RefreshSession = await RefreshSession.get(
        refresh_token, user_agent
    )
    await refresh_session.delete()
    user = await _user_service.get_user(User.id == refresh_session.user_id)
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
    refresh_session: RefreshSession = await RefreshSession.get(
        refresh_token, user_agent
    )
    response.delete_cookie('refresh_token')
    await refresh_session.delete()
    return {'user': user.id, 'status': 'logged out'}


@auth.post('/user', tags=['USER'])
async def create_user(
        _user: UserCreateSchema,
        _user_service: BaseService = Depends(user_service),
        _personal_data_service: BaseService = Depends(personal_data_service)
):
    user: User = await _user_service.register_user(**_user.model_dump())
    personal_data: PersonalData = await _personal_data_service.add_data(user_id=user.id)
    assert user.id == personal_data.user_id
    return UserRead(id=user.id, email=user.email, personal_data=None)


@auth.delete('/user', tags=['USER'])
async def delete_user(
        user: User = Depends(AuthDependency()),
        _user_service: BaseService = Depends(user_service)
):
    print(user)
    await _user_service.delete_user(user)
    return {'id': user.id, 'status': 'deleted'}


@auth.put('/user/personal_data', tags=['USER'])
async def update_personal_data(
        info: PersonalDataSchema,
        _personal_data_service: BaseService = Depends(personal_data_service),
        user: User = Depends(AuthDependency()),
):
    user_info: PersonalData = await _personal_data_service.update_data(
        PersonalData.user_id == user.id,
        **info.model_dump()
    )
    return user_info


@auth.get('/email/verify', tags=['EMAILS'])
async def get_verify_mail(
        user: User = Depends(AuthDependency()),
        _personal_data_service: BaseService = Depends(personal_data_service),
        _user_verify_service: BaseService = Depends(user_verify_service)
):
    personal_data: PersonalData = await _personal_data_service.get(PersonalData.user_id == user.id)
    if not personal_data.is_correct_data:
        raise HTTPException(
            status_code=400,
            detail={
                'detail': "Missing required fields 'first_name', 'surname', 'tg_nickname'"
            })
    verify_info: UserVerifyInfo = await _user_verify_service.add_verify_info(
        user_id=user.id
    )
    message_data = MessageData(
        subject='Подтверждение личного аккаунта',
        recipient_email=user.email,
        template_type='verify_email',
        token=verify_info.id
    )
    send_email_task(message_data)
    return JSONResponse({'detail': 'Verify Email is sent, please check your mail'})


@auth.post('/email/verify', tags=['EMAILS'])
async def verify_user(
        verify_token_schema: VerifyTokenSchema,
        user: User = Depends(AuthDependency()),
        _user_verify_service: BaseService = Depends(user_verify_service),
        _user_service: BaseService = Depends(user_service)
):
    verify_info: UserVerifyInfo = await _user_verify_service.get_verify_info(
        UserVerifyInfo.id == verify_token_schema.verify_token,
        UserVerifyInfo.user_id == user.id
    )

    verify_info = await _user_verify_service.update(
        UserVerifyInfo.id == verify_info.id,
        UserVerifyInfo.user_id == user.id,
        verified_at=datetime.datetime.utcnow()
    )
    await _user_service.verify_user(User.id == user.id)
    return JSONResponse({
        'user': user.email,
        'is_verified': True,
        'verified_at': verify_info.verified_at
    })


@auth.post('/email/password_update', tags=['EMAILS'])
async def token_update(
        response: Response,
        passwords: PasswordUpdateSchema,
        user_agent: Annotated[str, Header()],
        refresh_token: Annotated[str, Cookie()] = None,
        user: User = Depends(AuthDependency()),
        _password_upd_service: BaseService = Depends(password_upd_service),
        _user_service: BaseService = Depends(user_service)
):
    refresh_session: RefreshSession = await RefreshSession.get(refresh_token, user_agent)
    await refresh_session.delete()
    if not Hasher.is_correct_password(passwords.previous_password, user.password):
        raise HTTPException(
            status_code=400,
            detail={'status': 'error', 'detail': 'Incorrect current password'}
        )
    # По-хорошему здесь надо писать транзакцию, но есть куча вопросов к тому, как реализован паттерн UOW
    new_pwd_hash = Hasher.get_password_hash(passwords.current_password)
    pwd_upd_info: PasswordUpdate = await _password_upd_service.add(
        user_id=user.id,
        previous_password=user.password,
        current_password=new_pwd_hash,
        updated_at=datetime.datetime.utcnow(),
    )
    await _user_service.update(
        User.id == user.id,
        password=new_pwd_hash
    )
    return JSONResponse({
        'status': 'success',
        'detail': 'password is updated, login required',
        'updated_at': pwd_upd_info.updated_at,
    })
