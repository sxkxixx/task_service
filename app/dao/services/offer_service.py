from .iservice import BaseService


class OfferService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add_offer(self, **kwargs):
        return await self.add(**kwargs)
