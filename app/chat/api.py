from repositories.dependencies import chat_service, executor_service, message_service
from repositories.services import ExecutorService, ChatService, MessageService
from chat.schemas import ChatSchema, MessageSchema, Notification
from fastapi import APIRouter, Depends, Response, Request
from core.config import REDIS_MESSAGE_CHANNEL
from chat.message_token import MessageToken
from offer.models import Offer, Executor
from sqlalchemy.orm import selectinload
from auth.hasher import AuthDependency
from core.redis import redis_session
from auth.models import User
from chat.models import Chat
from aioredis import Redis
import sse_starlette
import async_timeout

chat_api = APIRouter(prefix='/api/v1')


@chat_api.post('/chat')
async def create_chat(
        _chat: ChatSchema,
        user: User = Depends(AuthDependency()),
        _executor_service: ExecutorService = Depends(executor_service),
        _chat_service: ChatService = Depends(chat_service)
):
    executor = await _executor_service.get_with_options(
        selectinload(Executor.offer),
        Executor.id == _chat.executor_id,
        Offer.user_id == user.id,
        Offer.id == _chat.offer_id,
        Executor.offer_id == _chat.offer_id
    )
    if not executor:
        return Response('Not found', status_code=404)
    offer = executor.offer
    if user.id != offer.user_id:
        return Response('Forbidden', status_code=403)
    chat = await _chat_service.add(
        offer_id=offer.id,
        executor_id=executor.id
    )
    return chat


@chat_api.delete('/chat/{chat_id}/delete')
async def delete_chat(
        chat_id: str,
        user: User = Depends(AuthDependency()),
        _chat_service: ChatService = Depends(chat_service)
):
    chat = await _chat_service.get_with_options(selectinload(Chat.offer), Chat.id == chat_id)
    if not chat:
        return Response('Not Found', status_code=404)
    offer = chat.offer
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    await _chat_service.delete(chat)
    return {'id': chat.id, 'status': 'deleted'}


@chat_api.post('/chat/{chat_id}/message')
async def post_message(
        chat_id: str,
        _message: MessageSchema,
        user: User = Depends(AuthDependency()),
        _chat_service: ChatService = Depends(chat_service),
        _message_service: MessageService = Depends(message_service),
        redis: Redis = Depends(redis_session)
):
    chat = await _chat_service.get_with_options(
        selectinload(Chat.offer), Chat.id == chat_id
    )
    if not chat:
        return Response('Not found', status_code=404)
    if user.id not in [chat.offer.user_id, chat.executor_id]:
        return Response('Forbidden', status_code=403)
    recipient_id = chat.offer.user_id if user.id == chat.executor_id else chat.executor_id
    message = await _message_service.add(
        owner_id=user.id,
        resipient_id=recipient_id,
        chat_id=chat.id,
        content=_message.content
    )
    redis_message = Notification(
        event='message', user_id=recipient_id,
        source={'chat_id': chat.id}, description=f'New message from {user.email}'
    )
    await redis.publish(
        f'{REDIS_MESSAGE_CHANNEL}:{recipient_id}',
        str(redis_message),
    )
    return message


@chat_api.get('/notification/token')
async def get_message_token(
        user: User = Depends(AuthDependency())
):
    message_token: MessageToken = MessageToken(user_id=user.id.__str__())
    await message_token.push()
    return {'message_token': message_token.id}


@chat_api.get('/notification/stream')
async def sse_notification(
        token: str,
        request: Request,
        redis: Redis = Depends(redis_session),
):
    try:
        message_token: MessageToken = await MessageToken.get(token)
    except ValueError:
        return Response('Message Token has expired', status_code=400)
    user: User = await message_token.user
    pb = redis.pubsub()
    await pb.subscribe(f'{REDIS_MESSAGE_CHANNEL}:{user.id}')

    async def event_stream():
        while True:
            if await request.is_disconnected():
                await pb.unsubscribe(f'{REDIS_MESSAGE_CHANNEL}:{user.id}')
                break
            async with async_timeout.timeout(10):
                message: dict = await pb.get_message(ignore_subscribe_messages=True)
                if message:
                    yield message.get('data')

    return sse_starlette.EventSourceResponse(event_stream())
