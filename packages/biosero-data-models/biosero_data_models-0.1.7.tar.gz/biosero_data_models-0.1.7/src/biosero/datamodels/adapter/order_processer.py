import requests
import time
import json
import logging
import threading
import inspect
import asyncio
import importlib
from rich.logging import RichHandler
from biosero.datamodels.events import (
    Event,
    EventMessage,
    ModuleStatusUpdateEvent,
    ModuleStatus,

)
from typing import Optional, TypeVar

T = TypeVar("T")

from biosero.datamodels.restclients import EventClient

#Clear existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup the logger
FORMAT = "%(message)s"
# logging.basicConfig(
#     level="INFO",
#     format=FORMAT,
#     handlers=[RichHandler(markup=True)]
# )

# logger = logging.getLogger("rich")

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    handlers=[RichHandler(markup=True, rich_tracebacks=True)]
)

# Always use the root logger
logger = logging.getLogger()



class OrderProcessor():
    def __init__(self, url, action_templates, actions_instance, adapter_id=None, adapter_name= None):
        # self.config = configparser.ConfigParser()
        # self.config.read(config_path)
        self.data_services_url = url#self.config["DATA SERVICES"]["url"]()

        self.action_mapping = self.generate_action_mapping(action_templates, actions_instance)
        self.adapter_id = adapter_id
        self.adapter_name = adapter_name
        module_update_event = ModuleStatusUpdateEvent(
            Id=0,
            ModuleIdentifier=self.adapter_id,
            ModuleName=self.adapter_name,
            Status=ModuleStatus.Ready
            )
        self.publish_event(module_update_event,"Python Script", "Python Operator")

        

    def update_order_status(self, order_id, order_status):
        url = f'{self.data_services_url}/api/v2.0/OrderService/UpdateOrderStatus?orderId={order_id}&status={order_status}'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data='"string"')

        if response.status_code == 200:
            logger.info(f"[i][grey7] - Order {order_id} status updated successfully[/grey7][/i]", extra={"markup": True})
        else:
            logger.error(f'Error updating order {order_id}: {response.status_code}')
            logger.info(response.text)

    def update_output_param(self, order, parameters):
        order_id = order['identifier']
        url = f'{self.data_services_url}/api/v2.0/OrderService/SetOutputParameters?orderId={order_id}'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        parameters = self.convert_values_to_string(parameters)
        payload = json.dumps(parameters)
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            logger.info(f"[i][grey7] - Order {order_id} parameters updated successfully[/grey7][/i]", extra={"markup": True})
        else:
            logger.error(f'Error updating order {order_id}: {response.status_code}')
            logger.info(response.text)


    def process_order(self, order):
        template_name = order['templateName']
        action_tuple = self.action_mapping.get(template_name)

        if action_tuple:
            if self.try_assign_order(order['identifier']):
                action_function, input_mapping, output_mapping = action_tuple
                input_parameters_dict = self.get_input_parameters_dict(order)
                mapped_inputs = self.map_input_parameters(input_parameters_dict, input_mapping)

                self.update_order_status(order['identifier'], "Running")
                order["parentIdentifier"] = order.get('parentIdentifier', 'None')

                logger.info(f'{order["parentIdentifier"]} --> {order["identifier"]} updated to Running')

                module_update_event = ModuleStatusUpdateEvent(
                    Id=0,
                    ModuleIdentifier=self.adapter_id,
                    ModuleName=self.adapter_name,
                    Status=ModuleStatus.Busy
                )
                self.publish_event(module_update_event,
                    "Python Script", "Python Operator")

                
                logger.info(f'{order["parentIdentifier"]} --> {order["identifier"]}: Setting Action Parameters {mapped_inputs}')

                try:
                    logger.debug(f"Detected async action: {action_function.__name__} — running in event loop")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    outputs = loop.run_until_complete(action_function(order, **mapped_inputs))
                    output_parameters = self.map_output_parameters(outputs, output_mapping)
                    self.update_output_param(order, output_parameters)
                    logger.info(f'{order["parentIdentifier"]} --> {order["identifier"]}: Setting Output Parameters {output_parameters}')
                    self.update_order_status(order['identifier'], "Complete")

                    module_update_event = ModuleStatusUpdateEvent(
                        Id=0,
                        ModuleIdentifier=self.adapter_id,
                        ModuleName=self.adapter_name,
                        Status=ModuleStatus.Ready
                        )
                    self.publish_event(module_update_event,
                        "Python Script", "Python Operator")

                except Exception as e:
                    logger.error(f'Error processing order {order["identifier"]}: {str(e)}')
                    self.update_order_status(order['identifier'], "Error")
                    logger.info(f'{order["parentIdentifier"]} --> {order["identifier"]}: Error Details {str(e)}')
                    module_update_event = ModuleStatusUpdateEvent(
                        Id=0,
                        ModuleIdentifier=self.adapter_id,
                        ModuleName=self.adapter_name,
                        Status=ModuleStatus.Error
                        )
                    self.publish_event(module_update_event,
                        "Python Script", "Python Operator")

            else:
                logger.warning(f"Order {order['identifier']} already assigned to another worker")
    def poll_endpoint(self):
        url = f'{self.data_services_url}/api/v2.0/OrderService/UnassignedOrders'
        headers = {'Accept': 'application/json'}
        connected = False

        while True:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                if not connected:
                    logger.info(f"[bold green]Connected to Biosero Data Services @ {url}[/bold green]", extra={"markup": True})
                    connected = True

                if response.status_code == 200:
                    orders = response.json()
                    for order in orders:
                        order_thread = threading.Thread(target=self.process_order, args=(order,))
                        order_thread.start()

                time.sleep(1)

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to poll {url}: {e}")
                connected = False
                time.sleep(3)
    def publish_event(self, event_item: T, actor_id: Optional[str] = None, operator_id: Optional[str] = None) -> None:

        transfer_event = Event(event_item)

        transfer_msg = EventMessage.from_event(transfer_event)

        transfer_msg.ActorId = actor_id
        transfer_msg.OperatorId = operator_id

        event_client = EventClient(self.data_services_url)

        event_client.publish_event(transfer_msg)
    def get_input_parameters_dict(self, order):
        input_parameters_dict = {}
        for param in order.get("inputParameters", []):
            if param["valueType"] == "Double":
                input_parameters_dict[param["name"]] = float(param["value"])
            elif param["valueType"] == "Boolean":
                input_parameters_dict[param["name"]] = param["value"].lower() == 'true'
            else:
                input_parameters_dict[param["name"]] = str(param["value"])
        return input_parameters_dict

    def try_assign_order(self, order_id):
        url = f'{self.data_services_url}/api/v3.0/orders/{order_id}/try-assign'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        payload = {"to": "Conductor Adapter"}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("orderAssigned") is True:
                logger.info(f"[i][grey7] - Order {order_id} assigned successfully[/grey7][/i]", extra={"markup": True})
                return True
            else:
                logger.error(f'Order {order_id} not assigned: {response_data}')
                return False
        else:
            logger.error(f'Error assigning order {order_id}: {response.status_code}')
            logger.info(response.text)
            return False
    
    def generate_action_mapping(self, action_templates=None, actions_instance=None):
        action_mapping = {}

        # If action_templates is not provided, try to dynamically import it
        if action_templates is None:
            try:
                action_templates = importlib.import_module("action_templates.action_templates")
            except ModuleNotFoundError as e:
                print(f"Error: Unable to load action_templates. Ensure it is installed and accessible. {e}")
                return {}

        # If actions_instance is not provided, try to import and instantiate Actions
        if actions_instance is None:
            try:
                actions_module = importlib.import_module("actions")
                actions_instance = actions_module.Actions()
            except (ModuleNotFoundError, AttributeError) as e:
                print(f"Error: Unable to load Actions class. Ensure it is available and accessible. {e}")
                return {}

        # Get all functions from action_templates that have _parameter_decorator
        stub_functions = [
            obj for name, obj in inspect.getmembers(action_templates)
            if inspect.isfunction(obj) and hasattr(obj, '_parameter_decorator')
        ]

        # Get all methods from the Actions class
        action_methods = {
            name: obj for name, obj in inspect.getmembers(actions_instance, predicate=inspect.ismethod)
            if name != '__init__'
        }

        # Create a mapping from the 'name' parameter in the @parameter decorator to the corresponding method in Actions
        for stub_function in stub_functions:
            decorator_name = stub_function._parameter_decorator['name']
            inputs = stub_function._parameter_decorator['inputs']
            outputs = stub_function._parameter_decorator['outputs']
            action_method = action_methods.get(stub_function.__name__)

            if action_method:
                # Create a dictionary mapping input names from the decorator to the method argument names
                stub_arg_names = inspect.signature(stub_function).parameters.keys()
                action_arg_names = inspect.signature(action_method).parameters.keys()
                input_mapping = dict(zip(inputs, stub_arg_names))
                output_mapping = outputs
                action_mapping[decorator_name] = (action_method, input_mapping, output_mapping)
            else:
                print(f"No matching method found in Actions for {stub_function.__name__}")

        return action_mapping

    @staticmethod
    def map_input_parameters(input_parameters_dict, input_mapping):
        return {actual_name: input_parameters_dict.get(decorator_name) for decorator_name, actual_name in input_mapping.items() if decorator_name in input_parameters_dict}

    @staticmethod
    def map_output_parameters(outputs, output_mapping):
        if not isinstance(outputs, tuple):
            outputs = (outputs,)
        return {name: value for name, value in zip(output_mapping, outputs)}

    @staticmethod
    def convert_values_to_string(payload):
        return {key: str(value) if not isinstance(value, str) else value for key, value in payload.items()}