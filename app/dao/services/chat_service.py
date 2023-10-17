from .iservice import BaseService


class ChatService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
