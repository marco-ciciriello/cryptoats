import json
import requests
import sys

from abc import ABC
from datetime import datetime
from decouple import config

from api.utils import filter_keys


# Requests/API abstraction layer
class Rest(ABC):

    uuid: str = None
    created: datetime = datetime.now()
    resource_name: str = ''
    relations: dict = {}
    api_root: str = config('API_ROOT')
    api_uri: str = config('API_URI')
    client: requests = requests
    headers: dict = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def query(self, method: str = 'get', data: object = {}, headers: object = {}) -> object:
        http_method = getattr(self.client, method)
        try:
            response = http_method(self.build_url(self.resource_name), data=data, headers=headers)
            data = response.json()
            return data['hydra:member']
        except:
            print(sys.exc_info()[0])
            pass

    def get(self, data={}, headers={}):
        return self.query(method='get', data=json.dumps(data), headers=self.build_headers(headers))

    def post(self, data={}, headers={}):
        return self.query(method='post', data=json.dumps(data), headers=self.build_headers(headers))

    def put(self, data={}, headers={}):
        return self.query(method='put', data=json.dumps(data), headers=self.build_headers(headers))

    def delete(self, data={}, headers={}):
        return self.query(method='delete', data=data, headers=self.build_headers(headers))

    def create(self, data={}):
        resource = self.post(data=self.serialise(data))

        return self.populate(data=[resource])

    def read(self, data: dict={}):
        resource = self.get(data=self.serialise(data))

        return self.populate(data=[resource])

    def update(self, data: dict={}):
        resource = self.put(data=self.serialise(data))

        return self.populate(data=[resource])

    def delete(self, data: dict={}):
        resource = self.delete(data=self.serialise(data))

        return self.populate(data=[resource])

    def build_url(self, resource: str):
        endpoint = self.api_root + self.api_uri + resource

        if self.uuid is None:
            return endpoint

        return endpoint + '/' + self.uuid

    def build_headers(self, headers: dict):
        return {
            **self.headers,
            **headers
        }
    
    def serialise(self, data: dict, filters={'rest', 'relations', 'resource_name'}):
        normalised_data = filter_keys(data={**self.__dict__, **data}, keys=filters)
        # Populate IRI for object relations
        for key, value in normalised_data.items():
            if key in self.relations:
                normalised_data[key] = '/' + self.api_uri + self.relations[key].resource_name + '/' + value.lower()

        return normalised_data

    def populate(self, data={}) -> object:
        for key, value in data[0].items():
            setattr(self, key, value)

        print(self.__dict__)

        return self
