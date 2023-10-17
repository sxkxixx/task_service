from .iservice import BaseService


class PasswordUpdateService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add_update_info(self,):
        info = await self.update(

        )

