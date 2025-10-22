import inspect
from biosero.datamodels.adapter.decorators import parameter
from biosero.datamodels.parameters import Parameter, ParameterValueType, ParameterCollection
from biosero.datamodels.restclients import OrderClient
from biosero.datamodels.ordering import Order, OrderStatus
import time
from typing import Tuple, get_type_hints

class Helpers(object):

    def __init__(self, data_services_url: str):

        self.data_services_url = data_services_url
    
    def process_order(self):

        type_mapping = {
            str: ParameterValueType.STRING,
            bool: ParameterValueType.BOOLEAN,
            float: ParameterValueType.DOUBLE,
            int: ParameterValueType.INTEGER,
        }

        # Get the current function's frame
        frame = inspect.currentframe().f_back
        # Get the current function's arguments
        _, _, _, values = inspect.getargvalues(frame)
        values = {k: v for k, v in values.items() if k != 'self'}
        # Get the current function's name
        func_name = frame.f_code.co_name
        # Get the class object
        cls = frame.f_locals['self'].__class__
        # Get the function object from the class
        func = getattr(cls, func_name)
        # Access the decorator metadata
        template_name = func._parameter_decorator['name']
        inputs = func._parameter_decorator['inputs']
        outputs = func._parameter_decorator['outputs']

        type_hints = get_type_hints(func)

        input_parameters = ParameterCollection()

        for index, input_name in enumerate(inputs):
            param = Parameter()
            param.name = input_name
            # Get the value based on the current index
            param.value = list(values.values())[index]  # Assuming values is a dictionary
            # Set the parameter value type based on type hints
            param_type = type_hints.get(input_name.replace(" ", "_").lower(), str)
            param.value_type = type_mapping.get(param_type, ParameterValueType.OTHER)
            input_parameters.append(param)


        # output_parameters = ParameterCollection()

        # for index, output_name in enumerate(outputs):
        #     param = Parameter()
        #     param.name = output_name
        #     # Get the value based on the current index
        #     param.value = list(values.values())[index]  # Assuming values is a dictionary
        #     # Set the parameter value type based on type hints
        #     param_type = type_hints.get(output_name.replace(" ", "_").lower(), str)
        #     param.value_type = type_mapping.get(param_type, ParameterValueType.OTHER)
        #     output_parameters.append(param)
        output_parameters = ParameterCollection()

        for output_name in outputs:
            param = Parameter()
            param.name = output_name
            param.value = None 
            param_type = type_hints.get(output_name.replace(" ", "_").lower(), str)
            param.value_type = type_mapping.get(param_type, ParameterValueType.OTHER)
            output_parameters.append(param)

        order = Order()

        # Create the order
        order_client = OrderClient(self.data_services_url)
        order.moduleRestrictionStrategy = "NoRestriction"
        order.templateName = template_name
        order.createdBy = "data services action"
        order.inputParameters = input_parameters.to_dict()
        order.outputParameters = output_parameters.to_dict()

        response = order_client.create_order(order)
        return_order = order_client.get_order(response)

        while return_order.status != OrderStatus.Complete.name:
            print("Waiting for Order to Complete")
            time.sleep(2)
            return_order = order_client.get_order(response)

            if return_order.status == OrderStatus.Error.name:
                print("Order failed")
                break

        # Retrieve output parameters from the completed order
        extracted_output_params = {param['name']: param['value'] for param in return_order.outputParameters}

        tuple_output = ()

        for output_name in outputs:

            item = extracted_output_params.get(output_name)

            tuple_output += (item,)

        return tuple_output