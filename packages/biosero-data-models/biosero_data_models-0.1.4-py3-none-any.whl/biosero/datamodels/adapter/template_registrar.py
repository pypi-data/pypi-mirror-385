import inspect
import sys
from typing import get_type_hints
import logging
import requests
import datetime
from rich.logging import RichHandler

from biosero.datamodels.resources import Identity, CommonTypeIdentifiers
from biosero.datamodels.parameters import (
    Parameter,
    ParameterCollection,
    ParameterValueType,
)
from biosero.datamodels.events import (
    EventContext,

)
logger = logging.getLogger("rich")
# Configure the logging module
logging.basicConfig(
    level=logging.INFO, 
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)


class TemplateRegistrar():
    def __init__(self, data_services_url, action_templates):
        """
        Initializes the TemplateRegistrar with a Data Services URL and action templates module.
        
        :param data_services_url: The base URL for Data Services.
        :param action_templates: The action templates module containing function stubs.
        """
        self.data_services_url = data_services_url
        self.action_templates = action_templates

    @staticmethod
    def type_to_value_type(py_type):
        """Maps a Python type to a valueType string for registration."""
        if py_type is str:
            return "String"
        elif py_type is float:
            return "Double"
        elif py_type is bool:
            return "Boolean"
        elif py_type is int:
            return "Integer"
        else:
            return "Other"  # Use "Other" or a default type for unrecognized types

    def extract_info_from_stub(self, func):
        """Extracts template metadata from a function decorated with @parameter."""
        parameter_decorator = getattr(func, '_parameter_decorator', None)
        if parameter_decorator is None:
            raise ValueError(f"No @parameter decorator found for {func.__name__}")

        # Retrieve type hints from the function signature
        type_hints = get_type_hints(func)
        signature_parameters = list(inspect.signature(func).parameters.values())

        # Process input parameters
        input_parameters = []
        for i, param_name in enumerate(parameter_decorator['inputs']):
            annotation = signature_parameters[i].annotation if i < len(signature_parameters) else str
            value_type = self.type_to_value_type(annotation)
            default_value = "False" if value_type == "Boolean" else ""
            value = "False" if default_value == "False" else ""
            input_parameters.append({
                "name": param_name,
                "value": value,
                "valueType": value_type,
                "defaultValue": default_value,
                "tags": [""]
            })

        # Process output parameters
        output_parameters = []
        return_type = type_hints.get('return', None)
        if return_type:
            if hasattr(return_type, '__args__'):  # Check if return_type is a tuple
                for i, output_name in enumerate(parameter_decorator['outputs']):
                    output_type = return_type.__args__[i] if i < len(return_type.__args__) else str
                    value_type = self.type_to_value_type(output_type)
                    default_value = "False" if value_type == "Boolean" else ""
                    value = "False" if default_value == "False" else ""
                    output_parameters.append({
                        "name": output_name,
                        "value": value,
                        "valueType": value_type,
                        "defaultValue": default_value,
                        "tags": [""]
                    })
            else:  # Single return type
                output_name = parameter_decorator['outputs'][0] if parameter_decorator['outputs'] else ""
                if return_type is not type(None):
                    value_type = self.type_to_value_type(return_type)
                    default_value = "False" if value_type == "Boolean" else ""
                    value = "False" if default_value == "False" else ""
                
                    output_parameters.append({
                        "name": output_name,
                        "value": value,
                        "valueType": value_type,
                        "defaultValue": default_value,
                        "tags": [""]
                    })

        # Construct the final dictionary
        info = {
            "name": parameter_decorator['name'],
            "inputParameters": input_parameters,
            "outputParameters": output_parameters,
            "icon": parameter_decorator['icon'],
            "category": parameter_decorator['category'],
            "color": parameter_decorator['color']
        }
        return info

    def register_template(self, info):
        """Registers a template with the Data Services API."""
        url = f'{self.data_services_url}/api/v2.0/OrderService/RegisterOrderTemplate'
        payload = {
            "category": info["category"],
            "description": "Python Action",
            "validationScriptLanguage": "C#",
            "defaultEstimatedDuration": "00:00:00",
            "durationEstimationScript": "string",
            "durationEstimationScriptLanguage": "C#",
            "schedulingStrategy": "ImmediateExecution",
            "isHidden": False,
            **info
        }
        response = requests.post(url, json=payload)
        return response

    def register_all_templates(self):
        """Registers all templates from the provided action_templates module."""
        for name, func in inspect.getmembers(self.action_templates, inspect.isfunction):
            if not hasattr(func, '_parameter_decorator'):
                continue   
            try:
                info = self.extract_info_from_stub(func)
                response = self.register_template(info)
                if response.status_code == 200:
                    print(f'Successfully registered template: {info["name"]}')
                else:
                    logger.warning(f'Failed to register template: {info["name"]}, status code: {response.status_code}, response: {response.text}')
            except ValueError as e:
                logger.error(f"Failed to extract info from {name}: {e}")

    def register_adapter(self, adapter_id, adapter_name):

        adapter = Identity()
        adapter.identifier = adapter_id
        adapter.name = adapter_name
        adapter.typeIdentifier = "C0311A0C-F8FB-4BE5-B578-8B45B4D45E0A"

        pc = ParameterCollection()
        p = Parameter()
        p.name = "Manufacturer"
        p.value = "Biosero"
        p.valueType = ParameterValueType.STRING
        p.identity = "4148704D-FAAC-46C3-9AB3-956165D65198"

        pc.append(p)

        p2 = Parameter()
        p2.name = "UI Color"
        p2.value = "#FF008080"
        p2.valueType = ParameterValueType.STRING

        pc.append(p2)

        pc = ParameterCollection()
        adapter.properties = pc
        adapter.isInstance = True
        from biosero.dataservices.restclient import AccessioningClient
        accessioning_client = AccessioningClient(self.data_services_url)

        event_context = EventContext()
        event_context.ActorId = "Python Script"
        event_context.Start = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        accessioning_client.register(adapter, event_context)
        return adapter

