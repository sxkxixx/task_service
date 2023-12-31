from offer.schemas import OfferSchema, OfferUpdate, FileSchema, OfferPublic, OfferPrivate
from repositories.dependencies import offer_service, executor_service, file_service, category_service, \
    offer_type_service
from repositories.services import Service
from offer.models import Offer, FileOffer, Executor
from sqlalchemy.orm import selectinload
from auth.hasher import AuthDependency
from fastapi import Depends, Response
from fastapi import APIRouter
from auth.models import User

offers_api = APIRouter(prefix='/api/v1')


@offers_api.get('/init_app', tags=['OFFER'])
async def app_init_route(
        _category_service: Service = Depends(category_service),
        _offer_type_service: Service = Depends(offer_type_service)
):
    categories = await _category_service.select()
    types = await _offer_type_service.select()
    return {'categories': categories, 'types': types}


@offers_api.post('/offer/create', tags=['OFFER'])
async def create_offer(
        _offer: OfferSchema,
        _offer_service: Service = Depends(offer_service),
        user: User = Depends(AuthDependency()),
):
    if not user.is_verified:
        return Response('User has to be verified', status_code=400)
    offer = await _offer_service.add(user_id=user.id, **_offer.model_dump())
    return offer


@offers_api.get('/offer/private/{offer_id}', tags=['OFFER'])
async def get_private_offer(
        offer_id: str,
        user: User = Depends(AuthDependency()),
        _offer_service: Service = Depends(offer_service),
):
    """Returns private Offer view"""
    offer = await _offer_service.get_with_options(
        [
            selectinload(Offer.executors).selectinload(Executor.user).selectinload(User.personal_data),
            selectinload(Offer.files)
        ],
        Offer.id == offer_id, Offer.user_id == user.id
    )
    if not offer:
        return Response('Not found', status_code=404)
    if user.id != offer.user_id:
        return Response('Forbidden', status_code=403)
    return OfferPrivate.offer_private_view(offer)


@offers_api.get('/offer/public/{offer_id}', tags=['OFFER'])
async def get_public_offer(
        offer_id: str,
        _offer_service: Service = Depends(offer_service),
):
    """Returns public Offer view"""
    _offer: Offer = await _offer_service.get_with_options(
        [selectinload(Offer.user).selectinload(User.personal_data), selectinload(Offer.files)],
        Offer.id == offer_id
    )
    if not _offer:
        return Response('Not found', status_code=404)
    return OfferPublic.offer_public_view(_offer)


@offers_api.get('/offers/main', tags=['OFFER'])
async def get_offers(
        type_id: str = None,
        category_id: str = None,
        _offer_service: Service = Depends(offer_service)
):
    filters = []
    if type_id:
        filters.append(Offer.type_id == type_id)
    if category_id:
        filters.append(Offer.category_id == category_id)
    res = await _offer_service.select(*filters)
    return res


@offers_api.get('/offers/profile', tags=['OFFER'])
async def get_user_offers(
        _type_id: str = None,
        _offer_service: Service = Depends(offer_service),
        user: User = Depends(AuthDependency())
):
    # TODO: Возвращает Offers, которые создал USER
    res = await _offer_service.select(
        Offer.user_id == user.id, Offer.type_id == _type_id
    )
    return res


@offers_api.get('/offers/responses', tags=['OFFER'])
async def get_user_response_offers(
        _type_id: str = None,
        _offer_service: Service = Depends(offer_service),
        user: User = Depends(AuthDependency())
):
    # TODO: "Отклики" User'a
    res = await _offer_service.select_join(
        [
            {'target': Executor, 'onclause': Executor.offer_id == Offer.id}
        ],
        Executor.user_id == user.id
    )
    return res


@offers_api.put('/offer/{offer_id}', tags=['OFFER'])
async def update_offer(
        offer_id: str,
        _offer_schema: OfferUpdate,
        _offer_service: Service = Depends(offer_service),
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
        _offer_service: Service = Depends(offer_service)
):
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    await _offer_service.delete(offer)
    return {'id': offer.id, 'status': 'deleted'}


@offers_api.post('/offer/{offer_id}/file', tags=['FILE'])
async def create_file(
        offer_id: str,
        _file: FileSchema,
        user: User = Depends(AuthDependency()),
        _offer_service: Service = Depends(offer_service),
        _file_service: Service = Depends(file_service),
):
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id != user.id:
        return Response('Must\'be offer owner', status_code=403)
    file = await _file_service.add(offer_id=offer.id, **_file.model_dump())
    return file


@offers_api.put('/file/{file_id}', tags=['FILE'])
async def update_file(
        file_id: str,
        _file: FileSchema,
        user: User = Depends(AuthDependency()),
        _file_service: Service = Depends(file_service),
):
    file: FileOffer = await _file_service.get_with_options([selectinload(FileOffer.offer)], FileOffer.id == file_id)
    if not file:
        return Response('Not found', status_code=404)
    offer: Offer = file.offer
    if offer.user_id != user.id:
        return Response('Forbidden', status_code=403)
    file = await _file_service.update(FileOffer.id == file.id, **_file.model_dump())
    return file


@offers_api.delete('/file/{file_id}', tags=['FILE'])
async def delete_file(
        file_id: str,
        user: User = Depends(AuthDependency()),
        _file_service: Service = Depends(file_service),
):
    file: FileOffer = await _file_service.get_with_options([selectinload(FileOffer.offer)], FileOffer.id == file_id)
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
        _executor_service: Service = Depends(executor_service),
        _offer_service: Service = Depends(offer_service)
):
    if not user.is_verified:
        return Response('User has to be verified', status_code=400)
    offer = await _offer_service.get(Offer.id == offer_id)
    if not offer:
        return Response('Not found', status_code=404)
    if offer.user_id == user.id:
        return Response('Offer\'s owner can\'t be executor of its offer', status_code=400)
    executor = await _executor_service.add(user_id=user.id, offer_id=offer_id)
    return executor


@offers_api.delete('/offer/{offer_id}/executor/{executor_id}', tags=['EXECUTOR'])
async def delete_executor(
        offer_id: str,
        executor_id: str,
        user: User = Depends(AuthDependency()),
        _executor_service: Service = Depends(executor_service),
):
    """User can stop being executor itself + Offer owner can delete executor"""
    executor = await _executor_service.get_with_options(
        [selectinload(Executor.offer)],
        Executor.id == executor_id, Offer.id == offer_id
    )
    if not executor:
        return Response('Not Found', status_code=404)
    offer = executor.offer
    if not (offer.user_id == user.id or executor.user_id == user.id):
        return Response('Forbidden', status_code=403)
    await _executor_service.delete(executor)
    return {'id': executor.id, 'status': 'deleted'}
