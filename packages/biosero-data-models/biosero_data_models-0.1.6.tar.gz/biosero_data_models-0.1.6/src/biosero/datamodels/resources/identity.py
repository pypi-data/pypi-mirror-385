# import dataclasses
# import json

# from biosero.datamodels.parameters.parameter_collection import ParameterCollection

# @dataclasses.dataclass
# class Identity:
#     identifier: str = ''
#     name: str = ''
#     typeIdentifier: str = ''
#     description: str = ''
#     #properties: dict = dataclasses.field(default_factory=dict)
#     properties: ParameterCollection = dataclasses.field(default_factory=ParameterCollection)
#     inheritProperties: bool = False
#     isInstance: bool = False

#     @classmethod
#     def from_identity(cls, identity):
#         obj = cls(**identity)
#         obj.properties = json.loads(json.dumps(obj.properties))
#         return obj

#     def to_identity(self):
#         id = Identity(**self.__dict__)
#         id.is_instance = True
#         id.properties = json.loads(json.dumps(id.properties))
#         return id
    
import dataclasses
import json
from biosero.datamodels.parameters.parameter_collection import ParameterCollection
from biosero.datamodels.parameters.parameter import Parameter

@dataclasses.dataclass
class Identity:
    identifier: str = ''
    name: str = ''
    typeIdentifier: str = ''
    description: str = ''
    properties: ParameterCollection = dataclasses.field(default_factory=ParameterCollection)
    inheritProperties: bool = False
    isInstance: bool = False

    @classmethod
    def from_identity(cls, identity):
        """
        Creates an Identity instance from a dictionary representation.
        Ensures 'properties' is always converted to a ParameterCollection.
        """
        # Create an Identity object using the dictionary
        obj = cls(**identity)

        # Check if 'properties' is a list of dictionaries (raw format)
        if isinstance(obj.properties, list):
            parameter_collection = ParameterCollection()
            for param_data in obj.properties:
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
                parameter_collection.append(parameter)

            # Replace the properties with a ParameterCollection
            obj.properties = parameter_collection

        # Ensure properties is a ParameterCollection even if empty
        elif obj.properties is None:
            obj.properties = ParameterCollection()

        return obj


    def to_identity(self):
        """
        Converts the Identity instance into a dictionary representation.
        Ensures 'properties' is serialized correctly.
        """
        # Create a copy of the current object's dictionary
        id_dict = dataclasses.asdict(self)

        # Convert properties to a list of dictionaries if it's a ParameterCollection
        if isinstance(self.properties, ParameterCollection):
            id_dict['properties'] = [
                {
                    'name': parameter.name,
                    'value': parameter.value,
                    'valueType': parameter.valueType,
                    'unit': parameter.unit,
                    'defaultValue': parameter.defaultValue,
                    'valueOptions': parameter.valueOptions,
                    'validationRules': parameter.validationRules,
                    'tags': parameter.tags,
                    'identity': parameter.identity,
                    'description': parameter.description
                }
                for parameter in self.properties
            ]
        
        return id_dict
