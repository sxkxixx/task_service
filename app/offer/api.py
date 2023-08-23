from typing import List
from repositories.dependencies import offer_service, category_service, offer_type_service, executor_service
from offer.schemas import OfferSchema, OfferUpdate
from offer.validators import check_file_signature
from fastapi import APIRouter, UploadFile, File, Body
from repositories.s3_service import S3Service
from repositories.services import Service
from auth.hasher import auth_dependency
from fastapi import Depends, Response
from offer.models import Offer, Executor, OfferType, Category
from auth.models import User
from sqlalchemy import or_

offers_api = APIRouter(prefix='/api/v1/offer', tags=['OFFER'])
s3_service = S3Service()


@offers_api.post('/create')
async def create_offer(
        _offer: OfferSchema,
        _offer_session: Service = Depends(offer_service),
        _category_service: Service = Depends(category_service),
        _offer_type_service: Service = Depends(offer_type_service),
        user: User = Depends(auth_dependency),
):
    offer = await _offer_session.add(user_id=user.id, **_offer.model_dump())
    return offer


@offers_api.get('/{offer_id}')
async def get_offer_by_id(
        offer_id: str,
        _offer_session: Service = Depends(offer_service)
):
    offer = await _offer_session.get_by_filter(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    return offer


@offers_api.put('/{offer_id}')
async def update_offer(
        offer_id: str,
        _offer_schema: OfferUpdate,
        _offer_service: Service = Depends(offer_service),
):
    offer = await _offer_service.update(offer_id, **_offer_schema.model_dump())
    if not offer:
        return Response('Not found', status_code=404)
    return offer


@offers_api.get('')
async def get_offers(
        offer_type: List[str] = None,
        category: List[str] = None,
        skip: int = 0,
        limit: int = 20,
        _offer_service: Service = Depends(offer_service)
):
    join_models, filters = [], []

    if offer_type:
        join_models.append(OfferType)
        for _type in offer_type:
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
        user: User = Depends(auth_dependency),
        _offer_service: Service = Depends(offer_service)
):
    if not check_file_signature(file):
        return Response('Bad file signature', status_code=400)
    offer = await _offer_service.get_by_filter(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    if offer.s3_filename:
        s3_filename = await s3_service.change_files(offer.s3_filename, file)
    else:
        s3_filename = await s3_service.upload_file(file)
    offer = await _offer_service.update(offer.id, s3_filename=s3_filename)
    return offer


@offers_api.post('/{offer_id}/executor/create')
async def create_executor(
        offer_id: str,
        user: User = Depends(auth_dependency),
        _executor_service: Service = Depends(executor_service),
        _offer_service: Service = Depends(offer_service)
):
    offer = await _offer_service.get_by_filter(Offer.id == offer_id)
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
        user: User = Depends(auth_dependency),
        _executor_service: Service = Depends(executor_service),
):
    executor = await _executor_service.get_by_filter(
        Executor.id == executor_id,
        Executor.offer_id == offer_id,
        Executor.user_id == user.id)
    if not executor:
        return Response('Not found', status_code=404)
    await _executor_service.delete(executor)
    return {'id': executor.id, 'status': 'deleted'}


@offers_api.patch('/{offer_id}/executor/{executor_id}/is_approved')
async def is_approved_executor(
        offer_id: str,
        executor_id: str,
        is_approved: bool = Body(...),
        user: User = Depends(auth_dependency),
        _executor_service: Service = Depends(executor_service),
        _offer_service: Service = Depends(offer_service)
):
    offer = await _offer_service.get_by_filter(Offer.id == offer_id, Offer.user_id == user.id)
    if not offer:
        return Response(f'Not found or {user.email} is not owner offer', status_code=404)
    executor = await _executor_service.update(executor_id, is_approved=is_approved)
    return executor
