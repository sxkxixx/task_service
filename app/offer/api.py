from repositories.dependencies import offer_service, category_service, offer_type_service
from offer.schemas import OfferSchema, OfferUpdate
from offer.validators import check_file_signature
from fastapi import APIRouter, UploadFile, File
from repositories.s3_service import S3Service
from repositories.services import Service
from auth.hasher import auth_dependency
from fastapi import Depends, Response
from offer.models import OfferType
from auth.models import User

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
    offer = await _offer_session.get_by_filter(id=offer_id)
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
        offer_type: str,
        skip: int = 0,
        limit: int = 20,
        _offer_service: Service = Depends(offer_service)
):
    res = await _offer_service.select(OfferType, type=offer_type)
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
    offer = await _offer_service.get_by_filter(id=offer_id)
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
