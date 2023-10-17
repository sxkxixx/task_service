from .iservice import BaseService


class FileService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
