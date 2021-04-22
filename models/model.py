from abc import ABC
from datetime import datetime

from api.rest import Rest
from api.utils import filter_keys


class AbstractModel(ABC):

    resource_name: str = ''

    created: datetime = datetime.now()
    rest: Rest
    relations: {}

    def __init__(self, **kwargs):
        self.rest = Rest()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def serialise(self, data: dict):
        normalised_data = filter_keys(data={**self.__dict__, **data}, keys={'rest', 'relations', 'resource_name'})
        # Populate IRI for object relations
        for key, value in normalised_data.items():
            if key in self.relations:
                normalised_data[key] = '/' + self.rest.api_uri + self.relations[key].resource_name + '/' + value.lower()
        
        return normalised_data

    def populate(self, data):
        for key, value in data[0].items():
            setattr(self, key, value)

        print(self.__dict__)

        return self

    def create(self, data: dict = {}):
        return self.populate([self.rest.post(resource=self.resource_name, data=self.serialise(data)).json()])

    def read(self, data: dict):
        return self.populate(self.rest.get(resource=self.resource_name, data=self.serialise(data)).json())
