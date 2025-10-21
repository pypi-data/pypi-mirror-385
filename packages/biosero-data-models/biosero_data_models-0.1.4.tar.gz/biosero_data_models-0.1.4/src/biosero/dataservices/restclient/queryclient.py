from urllib.parse import quote
import requests
import json
from dataclasses import asdict
from biosero.datamodels.resources import Identity ,MaterialInContainerSearchResult, SampleInContainerSearchResult
from biosero.datamodels.events import EventMessage
from biosero.datamodels.measurement import Volume, Weight, Location
from biosero.datamodels.ordering import WorkflowProcess
from biosero.datamodels.parameters import Parameter, ParameterCollection


class QueryClient:
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

    def get(self, endpoint, params=None):
        return self._session.get(self._session.headers['base_url'] + endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._session.post(self._session.headers['base_url'] + endpoint, data=data)

    def put(self, endpoint, data=None):
        return self._session.put(self._session.headers['base_url'] + endpoint, data=data)

    def delete(self, endpoint):
        return self._session.delete(self._session.headers['base_url'] + endpoint)
    
    # def get_identity(self, item_id):
    #     """
    #     Retrieves the identity of an item by its Identifier.

    #     Parameters:
    #     item_id (str): The ID of the item to retrieve the identity for.

    #     Returns:
    #     Identity: The identity of the item.
    #     """

    #     item_id = quote(item_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/Identity?id={item_id}"
    #     response = self._session.get(path, headers={'Content-Type': 'application/json'})
    #     response_json = response.text
    #     return Identity.from_identity(json.loads(response_json))
    def get_identity(self, item_id):
        """
        Retrieves the identity of an item by its Identifier.

        Parameters:
        item_id (str): The ID of the item to retrieve the identity for.

        Returns:
        Identity: The identity of the item, with its properties as a ParameterCollection.
        """

        item_id = quote(item_id)
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/Identity?id={item_id}"
        response = self._session.get(path, headers={'Content-Type': 'application/json'})

        if response.status_code == 404:
            return None
        response_json = json.loads(response.text)

        # Extract the properties and convert to ParameterCollection
        properties = response_json.get('properties', [])
        parameters = ParameterCollection()
        for param_data in properties:
            parameter = Parameter(
                name=param_data.get('name', None),
                value=param_data.get('value', None),
                valueType=param_data.get('valueType', None),
                unit=param_data.get('unit', None),
                defaultValue=param_data.get('defaultValue', None),
                valueOptions=param_data.get('valueOptions', None),
                validationRules=param_data.get('validationRules', None),
                tags=param_data.get('tags', None),
                identity=param_data.get('identity', None),
                description=param_data.get('description', None)
            )
            parameters.append(parameter)

        # Create an Identity object and attach the ParameterCollection
        identity = Identity.from_identity(response_json)
        identity.properties = parameters

        return identity

    # def get_child_identities(self, parent_type_id, limit, offset):
    #     """
    #     Retrieves the child identities of a parent item by its Identifier

    #     Parameters:
    #     parent_type_id (str): The ID of the parent item to retrieve the child identities for.
    #     limit (int): The maximum number of child identities to retrieve.
    #     offset (int): The number of child identities to skip before starting to retrieve.

    #     Returns:
    #     List[Identity]: The list of child identities of the parent item.
    #     """

    #     parent_type_id = quote(parent_type_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/ChildIdentities?parentTypeId={parent_type_id}&limit={limit}&offset={offset}"
    #     response = self._session.get(path, headers={'Content-Type': 'application/json'})
    #     response_json = response.text
    #     return [Identity.from_identity(identity) for identity in json.loads(response_json)]
    # def get_child_identities(self, parent_type_id, limit, offset):
    #     """
    #     Retrieves the child identities of a parent item by its Identifier

    #     Parameters:
    #     parent_type_id (str): The ID of the parent item to retrieve the child identities for.
    #     limit (int): The maximum number of child identities to retrieve.
    #     offset (int): The number of child identities to skip before starting to retrieve.

    #     Returns:
    #     ParameterCollection: A collection of parameters for the child identities.
    #     """

    #     parent_type_id = quote(parent_type_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/ChildIdentities?parentTypeId={parent_type_id}&limit={limit}&offset={offset}"
    #     response = self._session.get(path, headers={'Content-Type': 'application/json'})
    #     response_json = json.loads(response.text)

    #     # Convert response to ParameterCollection
    #     parameters = ParameterCollection()
    #     for param_data in response_json:
    #         parameter = Parameter(
    #             name=param_data.get('name', None),  # Default to None if 'name' is not present
    #             value=param_data.get('value', None),
    #             valueType=param_data.get('valueType', None),
    #             unit=param_data.get('unit', None),
    #             defaultValue=param_data.get('defaultValue', None),
    #             valueOptions=param_data.get('valueOptions', None),
    #             validationRules=param_data.get('validationRules', None),
    #             tags=param_data.get('tags', None),
    #             identity=param_data.get('identity', None),
    #             description=param_data.get('description', None)
    #         )
    #         parameters.append(parameter)

    #     return parameters
    def get_child_identities(self, parent_type_id, limit, offset):
        """
        Retrieves the child identities of a parent item by its Identifier.

        Parameters:
        parent_type_id (str): The ID of the parent item to retrieve the child identities for.
        limit (int): The maximum number of child identities to retrieve.
        offset (int): The number of child identities to skip before starting to retrieve.

        Returns:
        List[Identity]: A list of child identities where each identity's properties are a ParameterCollection.
        """

        parent_type_id = quote(parent_type_id)
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/ChildIdentities?parentTypeId={parent_type_id}&limit={limit}&offset={offset}"
        response = self._session.get(path, headers={'Content-Type': 'application/json'})
        response_json = json.loads(response.text)

        identities = []
        for identity_data in response_json:
            # Extract properties and convert them into a ParameterCollection
            properties = identity_data.get('properties', [])
            parameters = ParameterCollection()
            for param_data in properties:
                parameter = Parameter(
                    name=param_data.get('name', None),
                    value=param_data.get('value', None),
                    valueType=param_data.get('valueType', None),
                    unit=param_data.get('unit', None),
                    defaultValue=param_data.get('defaultValue', None),
                    valueOptions=param_data.get('valueOptions', None),
                    validationRules=param_data.get('validationRules', None),
                    tags=param_data.get('tags', None),
                    identity=param_data.get('identity', None),
                    description=param_data.get('description', None)
                )
                parameters.append(parameter)

            # Create an Identity object and attach the ParameterCollection
            identity = Identity.from_identity(identity_data)
            identity.properties = parameters
            identities.append(identity)

        return identities

    def remove_identity(self, item_id):

        item_id = quote(item_id)
        path = f"{self._session.headers['base_url']}/api/v3.0/identities/{item_id}"
        response = self._session.delete(path, headers={'Content-Type': 'application/json'})
        response.raise_for_status()

        return True
    
    def get_workflow_process(self, workflow_process_id):
        """
        Retrieves a workflow process by its Identifier.

        Parameters:
        workflow_process_id (int): The ID of the workflow process to retrieve.

        Returns:
        WorkflowProcess: The workflow process.
        """

        path = f"{self._session.headers['base_url']}/api/v3.0/orders/{workflow_process_id}/workflow-processes"
        response = self._session.get(path, headers={'Content-Type': 'application/json'})
        response_json = response.text
        
        return WorkflowProcess.from_workflow_process(json.loads(response_json))


    def get_parameter_value_from_identity(self, identity: Identity, parameter_name: str):
        """
        Retrieves the value of a parameter by name from an Identity object.

        Parameters:
        identity (Identity): The Identity object containing the parameters.
        parameter_name (str): The name of the parameter to retrieve the value for.

        Returns:
        Any: The value of the parameter if found, otherwise None.
        """
        if not identity or not hasattr(identity, 'properties'):
            return None

        for param in identity.properties:
            if param.name == parameter_name:
                return param.value

        return None
    # async def find_material_async(self, search_parameters, limit, offset):
    #     path = f"QueryService/FindMaterial?limit={limit}&offset={offset}"
    #     json_data = json.dumps(search_parameters)
    #     content = {"Content-Type": "application/json"}
    #     response = await self._session.post(path, data=json_data, headers=content)
    #     response.raise_for_status()
    #     if response.status_code == 204:
    #         return None
    #     return [MaterialInContainerSearchResult(**item) for item in response.json()]

    # def find_material(self, search_parameters, limit, offset):
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/FindMaterial?limit={limit}&offset={offset}"
    #     json_data = json.dumps(search_parameters)
    #     response = requests.post(path, data=json_data, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     if response.status_code == 204:
    #         return None
    #     return [MaterialInContainerSearchResult(**item) for item in response.json()]

    # async def find_sample_async(self, search_parameters, limit, offset):
    #     path = f"QueryService/FindSample?limit={limit}&offset={offset}"
    #     json_data = json.dumps(search_parameters)
    #     content = {"Content-Type": "application/json"}
    #     response = await self._session.post(path, data=json_data, headers=content)
    #     response.raise_for_status()
    #     if response.status_code == 204:
    #         return None
    #     return [SampleInContainerSearchResult(**item) for item in response.json()]

    # def find_sample(self, search_parameters, limit, offset):
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/FindSample?limit={limit}&offset={offset}"
    #     json_data = json.dumps(search_parameters)
    #     response = requests.post(path, data=json_data, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     if response.status_code == 204:
    #         return None
    #     return [SampleInContainerSearchResult(**item) for item in response.json()]

    # async def get_child_identities_async(self, parent_type_id, limit, offset):
    #     parent_type_id = quote(parent_type_id)
    #     path = f"QueryService/ChildIdentities?parentTypeId={parent_type_id}&limit={limit}&offset={offset}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return [Identity(**item) for item in response.json()]

    def get_events(self, search_parameters, limit, offset):
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/Events?limit={limit}&offset={offset}"
        # Convert search_parameters to a dictionary and filter out None values
        filtered_parameters = {k: v for k, v in asdict(search_parameters).items() if v is not None}
        json_data = json.dumps(filtered_parameters, default=str)
        response = requests.post(path, data=json_data, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        if response.status_code == 204:
            return None
        # Convert response keys from camelCase to PascalCase
        response_data = response.json()
        for item in response_data:
            camel_case_mapping = {
                'eventId': 'EventId',
                'accessPolicy': 'AccessPolicy',
                'sharingPolicy': 'SharingPolicy',
                'retentionPolicy': 'RetentionPolicy',
                'subjects': 'Subjects',
                'sourceTraceIds': 'SourceTraceIds',
                'tags': 'Tags',
                'data': 'Data',
                'start': 'Start',
                'end': 'End',
                'encryptionProvider': 'EncryptionProvider',
                'topic': 'Topic',
                'organizationId': 'OrganizationId',
                'groupId': 'GroupId',
                'ownerId': 'OwnerId',
                'associationId': 'AssociationId',
                'activityId': 'ActivityId',
                'actorId': 'ActorId',
                'subjectsContains': 'SubjectsContains',
                'orchestratorId': 'OrchestratorId',
                'operatorId': 'OperatorId',
                'moduleId': 'ModuleId',
                'createdDateUtc': 'CreatedDateUtc',
                'expirationDateUtc': 'ExpirationDateUtc',
            }
            for key in list(item.keys()):
                if key in camel_case_mapping:
                    item[camel_case_mapping[key]] = item.pop(key)
        return [EventMessage(**item) for item in response_data]


   

        
    def get_items_at_location(self, location_id, limit, offset):
        location_id = quote(location_id)
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/ItemsAtLocation?locationId={location_id}&limit={limit}&offset={offset}"
        response = requests.get(path, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return [Identity(**item) for item in response.json()]

    async def get_items_at_location_async(self, location_id, limit, offset):
        location_id = quote(location_id)
        path = f"QueryService/ItemsAtLocation?locationId={location_id}&limit={limit}&offset={offset}"
        response = await self._session.get(path)
        response.raise_for_status()
        return [Identity(**item) for item in response.json()]

    def get_location(self, item_id):
        item_id = quote(item_id)
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/Location?itemId={item_id}"
        response = requests.get(path, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return Location(**response.json())

    # async def get_location_async(self, item_id):
    #     item_id = quote(item_id)
    #     path = f"QueryService/Location?itemId={item_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return Location(**response.json())


    # The end point in this method does not work
    # def get_location_path(self, item_id):
    #     item_id = quote(item_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/LocationPath?itemId={item_id}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return response.json()

    # async def get_location_path_async(self, item_id):
    #     item_id = quote(item_id)
    #     path = f"QueryService/LocationPath?itemId={item_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return response.json()

    def get_materials_in_container(self, container_id):
        container_id = quote(container_id)
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/MaterialsInContainer?containerId={container_id}"
        response = requests.get(path, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return [MaterialInContainerSearchResult(**item) for item in response.json()]

    async def get_materials_in_container_async(self, container_id):
        container_id = quote(container_id)
        path = f"QueryService/MaterialsInContainer?containerId={container_id}"
        response = await self._session.get(path)
        response.raise_for_status()
        return [MaterialInContainerSearchResult(**item) for item in response.json()]

    def get_net_volume(self, container_id):
        container_id = quote(container_id)
        path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/NetVolume?containerId={container_id}"
        response = requests.get(path, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return Volume(**response.json())

    # async def get_net_volume_async(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"QueryService/NetVolume?containerId={container_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return Volume(**response.json())

    # def get_net_weight_from_transfers(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/NetWeightFromTransfers?containerId={container_id}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return Weight(**response.json())

    # async def get_net_weight_from_transfers_async(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"QueryService/NetWeightFromTransfers?containerId={container_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return Weight(**response.json())

    # def get_tare_weight_measurement(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/TareWeightMeasurment?containerId={container_id}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return Weight(**response.json())

    # async def get_tare_weight_measurement_async(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"QueryService/TareWeightMeasurment?containerId={container_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return Weight(**response.json())

    # def get_gross_weight_measurement(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/GrossWeightMeasurment?containerId={container_id}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return Weight(**response.json())

    # async def get_gross_weight_measurement_async(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"QueryService/GrossWeightMeasurment?containerId={container_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return Weight(**response.json())

    # def get_samples_in_container(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/SamplesInContainer?containerId={container_id}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return [SampleInContainerSearchResult(**item) for item in response.json()]

    # async def get_samples_in_container_async(self, container_id):
    #     container_id = quote(container_id)
    #     path = f"QueryService/SamplesInContainer?containerId={container_id}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return [SampleInContainerSearchResult(**item) for item in response.json()]

    # def get_samples_in_containers(self, container_ids):
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/SamplesInContainers"
    #     json_data = json.dumps(container_ids)
    #     response = requests.post(path, data=json_data, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return [SampleInContainerSearchResult(**item) for item in response.json()]

    # async def get_samples_in_containers_async(self, container_ids):
    #     path = f"QueryService/SamplesInContainers"
    #     json_data = json.dumps(container_ids)
    #     content = {"Content-Type": "application/json"}
    #     response = await self._session.post(path, data=json_data, headers=content)
    #     response.raise_for_status()
    #     return [SampleInContainerSearchResult(**item) for item in response.json()]

    # def get_identity_by_name(self, item_name):
    #     item_name = quote(item_name)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/IdentityByName?name={item_name}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return Identity(**response.json())

    # async def get_identity_by_name_async(self, item_name):
    #     item_name = quote(item_name)
    #     path = f"QueryService/IdentityByName?name={item_name}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return Identity(**response.json())

    # def get_well_identifier(self, plate_id, alpha_numeric_well_location):
    #     plate_id = quote(plate_id)
    #     alpha_numeric_well_location = quote(alpha_numeric_well_location)
    #     path = f"{self._session.headers['base_url']}/api/v2.0/QueryService/WellIdentifier?plateId={plate_id}&well={alpha_numeric_well_location}"
    #     response = requests.get(path, headers={'Content-Type': 'application/json'})
    #     response.raise_for_status()
    #     return response.json()

    # async def get_well_identifier_async(self, plate_id, alpha_numeric_well_location):
    #     plate_id = quote(plate_id)
    #     alpha_numeric_well_location = quote(alpha_numeric_well_location)
    #     path = f"QueryService/WellIdentifier?plateId={plate_id}&well={alpha_numeric_well_location}"
    #     response = await self._session.get(path)
    #     response.raise_for_status()
    #     return response.json()
