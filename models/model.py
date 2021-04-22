from abc import ABC
from datetime import datetime

from api.rest import Rest


class AbstractModel(ABC):

    resource_name: str = ''

    created: datetime = datetime.now()
    rest: Rest
    relations: {}

    def __init__(self, **kwargs):
        self.rest = Rest()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def filter_keys(self, data: dict):
        return {k: v for k, v in data.items() if k not in {'rest', 'relations', 'resource_name'}}

    def serialise(self, data: dict):
        normalised_data = self.filter_keys({**self.__dict__, **data})
        # Populate IRI for object relations
        for key, value in normalised_data.items():
            if key in self.relations:
                normalised_data[key] = '/' + self.rest.api_uri + self.relations[key].resource_name + '/' + value.lower()
        print(normalised_data)
        
        return normalised_data

    def persist(self, data: dict = {}):
        response = self.rest.post(resource=self.resource_name, data=self.serialize(data))
        return response.json()

    def persist(self, data: dict):
        rest = Rest()
        response = rest.post(resource=self.get_resource_name(), data=self.serialise(data))

        return response.json()
