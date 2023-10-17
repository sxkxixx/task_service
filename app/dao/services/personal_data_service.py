from .iservice import BaseService


class PersonalDataService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add_data(self, **kwargs):
        return await self.add(**kwargs)

    async def update_data(self, *filters, **upd_values):
        return await self.update(*filters, **upd_values)
