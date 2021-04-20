from abc import ABC, abstractmethod
from datetime import datetime

from api.rest import Rest


class AbstractModel(ABC):

    created: datetime = datetime.now()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def get_resource_name(self):
        pass

    def serialise(self, data: dict):
        return {**self.__dict__, **data}

    def persist(self, data: dict):
        rest = Rest()
        response = rest.post(resource=self.get_resource_name(), data=self.serialise(data))

        return response.json()
