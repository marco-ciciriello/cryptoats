import datetime
import json
import logging
import requests
import sys

from abc import ABC
from decouple import config

from api.utils import filter_keys


# Requests abstraction layer
class Rest(ABC):

    uuid: str = None
    created: datetime = datetime.datetime.now()
    resource_name: str = ''
    relations: dict = {}
    api_root: str = config('API_ROOT')
    api_uri: str = config('API_URI')
    client: requests = requests
    headers: dict = {'Content-type': 'application/json', 'Accept': 'application/json'}

    def query(self, method: str = 'get', data=None, headers=None, iri: str = None):
        if headers is None:
            headers = {}
        if data is None:
            data = {}

        http_method = getattr(self.client, method)

        try:
            response = http_method(self.build_url(self.resource_name, iri), data=data, headers=headers)
            data = response.json()
            
            if 'hydra:member' in data:
                return data['hydra:member']

            return data
        except:
            print(sys.exc_info()[0])
            logging.error(sys.exc_info()[0])
            pass

    def get(self, data=None, headers=None):
        if headers is None:
            headers = {}
        if data is None:
            data = {}

        return self.query(method='get', data=json.dumps(self.serialise(data)), headers=self.build_headers(headers))

    def post(self, data=None, headers=None):
        if headers is None:
            headers = {}
        if data is None:
            data = {}

        return self.query(method='post', data=json.dumps(self.serialise(data)), headers=self.build_headers(headers))

    def put(self, data=None, headers=None):
        if data is None:
            data = {}
        if headers is None:
            headers = {}

        return self.query(method='put', data=json.dumps(self.serialise(data)), headers=self.build_headers(headers))

    def delete(self, data=None, headers=None):
        if headers is None:
            headers = {}
        if data is None:
            data = {}
        return self.query(method='delete', data=json.dumps(self.serialise(data)), headers=self.build_headers(headers))

    def create(self, data=None):
        if data is None:
            data = {}
        response = self.post(self.serialise(data))
        print('response', response)
        return self.populate(data=[response])

    def read(self, data=None):
        if data is None:
            data = {}

        resource = self.get(data=data)

        return self.populate(data=[resource])

    def update(self, data=None):
        if data is None:
            data = {}

        resource = self.put(data=data)

        return self.populate(data=[resource])

    def remove(self, data=None):
        if data is None:
            data = {}

        resource = self.delete(data=data)

        return resource

    def build_url(self, resource: str, iri: str = None):
        endpoint = self.api_root + self.api_uri + resource

        if iri is not None:
            return iri
        if self.uuid is None:
            return endpoint

        return endpoint + '/' + self.uuid

    def build_headers(self, headers: dict):
        return {
            **self.headers,
            **headers
        }
    
    def get_relation(self, model, iri: str, headers=None):
        if headers is None:
            headers = {}

        resource = self.query(method='get', data=json.dumps(self.serialise()), headers=self.build_headers(headers),
                              iri=iri)

        return model().populate(data=resource)

        def serialise(self, data=None, filters=None):
        if filters is None:
            filters = {"rest", "relations", "resource_name"}
        if data is None:
            data = {}

        filtered_data = filter_keys(data={**self.__dict__, **data}, keys=filters)

        # Populate IRI for object relations
        for key, value in filtered_data.items():
            if key in self.relations and type(value) == str and '/' not in value:
                filtered_data[key] = '/' + self.api_uri + self.relations[key].resource_name + '/' + value.lower()
            elif key in self.relations and type(value) == dict:
                filtered_data[key] = value['@id']
            elif isinstance(value, datetime.datetime):
                filtered_data[key] = value.strftime('%m/%d/%Y, %H:%M:%S')
            else:
                filtered_data[key] = value

        return filtered_data

    def populate(self, data=None, filters=None) -> 'Rest':
        if type(data) is list:
            data = data[0]

        if type(data) is None or None in data:
            return self

        if filters is None:
            filters = {}

        filtered_data = filter_keys(data=data, keys=filters)
        
        for [key, value] in filtered_data.items():
            setattr(self, key, value)

        return self
