from repositories.dependencies import offer_service, category_service, offer_type_service, executor_service
from offer.models import Offer, Executor, OfferType, Category
from fastapi import APIRouter, UploadFile, File, Body
from offer.validators import is_valid_file_signature
from offer.schemas import OfferSchema, OfferUpdate
from repositories.s3_service import S3Service
from repositories.services import OfferService, ExecutorService
from auth.hasher import AuthDependency
from fastapi import Depends, Response
from auth.models import User
from sqlalchemy import or_
from typing import List

offers_api = APIRouter(prefix='/api/v1/offer', tags=['OFFER'])
s3_service = S3Service()


@offers_api.post('/create')
async def create_offer(
        _offer: OfferSchema,
        _offer_service: OfferService = Depends(offer_service),
        _category_service=Depends(category_service),
        _offer_type_service=Depends(offer_type_service),
        user: User = Depends(AuthDependency()),
):
    offer = await _offer_service.add(user_id=user.id, **_offer.model_dump())
    return offer


@offers_api.get('/{offer_id}')
async def get_offer_by_id(
        offer_id: str,
        _offer_session: OfferService = Depends(offer_service),
        user: User | None = Depends(AuthDependency(is_strict=False))
):
    offer = await _offer_session.lazyload_get(Offer.executors, id=offer_id)
    if not offer:
        return Response('Not found', status_code=404)

    return offer


@offers_api.put('/{offer_id}')
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


@offers_api.delete('/{offer_id}')
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


@offers_api.get('')
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


@offers_api.patch('/{offer_id}/file')
async def append_file(
        offer_id: str,
        file: UploadFile = File(...),
        user: User = Depends(AuthDependency()),
        _offer_service: OfferService = Depends(offer_service)
):
    if not is_valid_file_signature(file):
        return Response('Bad file signature', status_code=400)
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    if offer.s3_filename:
        s3_filename = await s3_service.change_files(offer.s3_filename, file)
    else:
        s3_filename = await s3_service.upload_file(file)
    offer = await _offer_service.update(Offer.id == offer.id, s3_filename=s3_filename)
    return offer


@offers_api.post('/{offer_id}/executor/create')
async def create_executor(
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


@offers_api.delete('/{offer_id}/executor/{executor_id}/delete')
async def delete_executor(
        offer_id: str,
        executor_id: str,
        user: User = Depends(AuthDependency()),
        _executor_service: ExecutorService = Depends(executor_service),
):
    executor = await _executor_service.lazyload_get(
        Executor.offer,
        id=executor_id, offer_id=offer_id)
    if not executor:
        return Response('Not found', status_code=404)
    if executor.user_id != user.id or executor.offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    await _executor_service.delete(executor)
    return {'id': executor.id, 'status': 'deleted'}


@offers_api.patch('/{offer_id}/executor/{executor_id}/is_approved')
async def is_approved_executor(
        offer_id: str,
        executor_id: str,
        is_approved: bool = Body(...),
        user: User = Depends(AuthDependency()),
        _executor_service: ExecutorService = Depends(executor_service),
        _offer_service: OfferService = Depends(offer_service)
):
    offer = await _offer_service.get(Offer.id == offer_id, Offer.user_id == user.id)
    if not offer:
        return Response(f'Not found or {user.email} is not owner offer', status_code=404)
    executor = await _executor_service.update(Executor.id == executor_id, is_approved=is_approved)
    return executor
