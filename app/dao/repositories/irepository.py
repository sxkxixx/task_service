from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    async def add(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def select(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_with_options(self, *args, **kwargs):
        pass

    @abstractmethod
    def select_join(self, *args, **kwargs):
        pass

    @abstractmethod
    def select_with_options(self, *args, **kwargs):
        pass
