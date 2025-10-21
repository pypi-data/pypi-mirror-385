import dataclasses
import requests
import json
from urllib.parse import quote
from typing import Any, List

from biosero.datamodels.parameters import ParameterCollection
from biosero.datamodels.resources import Identity  


class AccessioningClient:
    def __init__(self, url):
        if callable(url):
            url = url()
        self._session = requests.Session()
        self._session.headers.update({'base_url': url})
        self._created_client = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._created_client:
            self._session.close()

    def post(self, endpoint, data=None):
        headers = {'Content-Type': 'application/json'}
        return self._session.post(self._session.headers['base_url'] + endpoint, data=data, headers=headers)

    def delete(self, endpoint):
        return self._session.delete(self._session.headers['base_url'] + endpoint)



    def register(self, identity: Identity, event_context: Any):
        if not isinstance(identity, Identity):
            raise TypeError("identity must be an instance of Identity")

        # Convert Identity to the expected structure
        identity_dict = dataclasses.asdict(identity)
        # if isinstance(identity_dict['properties'], dict):
        #     identity_dict['properties'] = [{'name': k, 'value': v, 'valueType': 'String'} for k, v in identity_dict['properties'].items()]

        # Convert ParameterCollection to the expected list of dictionaries
        if isinstance(identity.properties, ParameterCollection):
            identity_dict['properties'] = [
                {'name': param.name, 'value': param.value, 'valueType': param.valueType.value}
                for param in identity.properties
            ]
        else:
            raise TypeError("identity.properties must be an instance of ParameterCollection")



        # Convert event_context to the expected structure
        event_context_dict = {k: v for k, v in dataclasses.asdict(event_context).items() if v is not None}

        # Create JSON payload
        json_data = json.dumps({'identity': identity_dict, 'eventContext': event_context_dict})

        # Post request to the specified API endpoint
        response = self.post("/api/v2.0/AccessioningService/RegisterIdentity", data=json_data)

        # Check for successful response
        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason}")

        return response.json()


    def remove(self, identifier):

        path = f"/api/v2.0/AccessioningService/RemoveIdentity?Identifier={quote(identifier)}"

        response = self.delete(path)

        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason}")



    def register_many(self, identities: List[Identity], event_context: Any):
        if not isinstance(identities, list):
            raise TypeError("identities must be a list of Identity instances")

        identity_dicts = []
        for identity in identities:
            if not isinstance(identity, Identity):
                raise TypeError("Each item in identities must be an instance of Identity")

            identity_dict = dataclasses.asdict(identity)

            if isinstance(identity.properties, ParameterCollection):
                identity_dict['properties'] = [
                    {'name': param.name, 'value': param.value, 'valueType': param.valueType.value}
                    for param in identity.properties
                ]
            else:
                raise TypeError("identity.properties must be an instance of ParameterCollection")

            identity_dicts.append(identity_dict)
        event_context_dict = {k: v for k, v in dataclasses.asdict(event_context).items() if v is not None}

        json_data = json.dumps({'Identities': identity_dicts, 'EventContext': event_context_dict})
        response = self.post("/api/v2.0/AccessioningService/RegisterIdentities", data=json_data)

        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason}")

        return response.json()
