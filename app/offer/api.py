from repositories.dependencies import offer_service, executor_service, file_service
from repositories.services import OfferService, ExecutorService, FileService
from offer.models import Offer, OfferType, Category, FileOffer, Executor
from offer.schemas import OfferSchema, OfferUpdate, FileSchema, OfferPublic, OfferPrivate
from sqlalchemy.orm import selectinload
from auth.hasher import AuthDependency
from fastapi import Depends, Response
from fastapi import APIRouter
from sqlalchemy import or_
from auth.models import User
from typing import List

offers_api = APIRouter(prefix='/api/v1')


@offers_api.post('/offer/create', tags=['OFFER'])
async def create_offer(
        _offer: OfferSchema,
        _offer_service: OfferService = Depends(offer_service),
        user: User = Depends(AuthDependency()),
):
    offer = await _offer_service.add(user_id=user.id, **_offer.model_dump())
    return offer


@offers_api.get('/offer/private/{offer_id}', tags=['OFFER'])
async def get_private_offer(
        offer_id: str,
        user: User = Depends(AuthDependency()),
        _offer_service: OfferService = Depends(offer_service),
):
    offer = await _offer_service.get_with_options(
        [selectinload(Offer.executors).selectinload(Executor.user).selectinload(User.personal_data)],
        Offer.id == offer_id, Offer.user_id == user.id
    )
    if not offer:
        return Response('Not found', status_code=404)
    return OfferPrivate.offer_private_view(offer)


@offers_api.get('/offer/public/{offer_id}', tags=['OFFER'])
async def get_public_offer(
        offer_id: str,
        _offer_service: OfferService = Depends(offer_service),
):
    _offer: Offer = await _offer_service.get_with_options(
        [selectinload(Offer.user).selectinload(User.personal_data)],
        Offer.id == offer_id
    )
    if not _offer:
        return Response('Not found', status_code=404)
    return OfferPublic.offer_public_view(_offer)


@offers_api.put('/offer/{offer_id}', tags=['OFFER'])
async def update_offer(
        offer_id: str,
        _offer_schema: OfferUpdate,
        _offer_service: OfferService = Depends(offer_service),
        user: User = Depends(AuthDependency())
):
    offer = await _offer_service.update(Offer.id == offer_id, Offer.user_id == user.id, **_offer_schema.model_dump())
    if not offer:
        return Response('Not found', status_code=404)
    return offer


@offers_api.delete('/offer/{offer_id}', tags=['OFFER'])
async def delete_offer(
        offer_id: str,
        user: User = Depends(AuthDependency()),
        _offer_service: OfferService = Depends(offer_service)
):
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    await _offer_service.delete(offer)
    return {'id': offer.id, 'status': 'deleted'}


@offers_api.get('/offers', tags=['OFFER'])
async def get_offers(
        types: List[str] = None,
        category: List[str] = None,
        skip: int = 0,
        limit: int = 20,
        _offer_service: OfferService = Depends(offer_service)
):
    join_models, filters = [], []

    if types:
        join_models.append(OfferType)
        for _type in types:
            filters.append(OfferType.type == _type)
    if category:
        join_models.append(Category)
        for _category in category:
            filters.append(Category.name == _category)

    res = await _offer_service.select(join_models, or_(*filters))
    return res[skip: skip + limit]


@offers_api.post('/offer/{offer_id}/file', tags=['FILE'])
async def create_file(
        offer_id: str,
        _file: FileSchema,
        user: User = Depends(AuthDependency()),
        _offer_service: OfferService = Depends(offer_service),
        _file_service: FileService = Depends(file_service),
):
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id != user.id:
        return Response('Must\'be offer owner', status_code=403)
    file = await _file_service.add(**_file.model_dump())
    return file


@offers_api.put('/file/{file_id}', tags=['FILE'])
async def update_file(
        file_id: str,
        _file: FileSchema,
        user: User = Depends(AuthDependency()),
        _file_service: FileService = Depends(file_service),
):
    file: FileOffer = await _file_service.get_with_options(selectinload(FileOffer.offer), FileOffer.id == file_id)
    if not file:
        return Response('Not found', status_code=404)
    offer: Offer = file.offer
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    file = await _file_service.update(file.id, **_file.model_dump())
    return file


@offers_api.delete('/file/{file_id}', tags=['FILE'])
async def delete_file(
        file_id: str,
        user: User = Depends(AuthDependency()),
        _file_service: FileService = Depends(file_service),
):
    file: FileOffer = await _file_service.get_with_options(selectinload(FileOffer.offer), FileOffer.id == file_id)
    if not file:
        return Response('Not found', status_code=404)
    offer: Offer = file.offer
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    await _file_service.delete(file)
    return {'id': file.id, 'status': 'deleted'}


@offers_api.post('/offer/{offer_id}/executor', tags=['EXECUTOR'])
async def become_executor(
        offer_id: str,
        user: User = Depends(AuthDependency()),
        _executor_service: ExecutorService = Depends(executor_service),
        _offer_service: OfferService = Depends(offer_service)
):
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id == user.id:
        return Response('Offer\'s owner can\'t be executor of its offer', status_code=400)
    executor = await _executor_service.add(user_id=user.id, offer_id=offer_id)
    return executor
