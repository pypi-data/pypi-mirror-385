
from biosero.dataservices.restclient.accessioningclient import AccessioningClient
from biosero.dataservices.restclient.queryclient import QueryClient
from biosero.datamodels.parameters import Parameter, ParameterCollection
from biosero.datamodels.resources import Identity
from biosero.datamodels.events import EventContext

import uuid

import time
import datetime

import logging
from rich.logging import RichHandler
logger = logging.getLogger("rich")
# Configure the logging module
logging.basicConfig(
    level=logging.INFO, 
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

class FlowControl:

    def __init__(self, url: str):
        """Initialize Registration with a URL."""
        self.url = url
        self.accessioning_client = AccessioningClient(url)
        self.query_client = QueryClient(url)



    def register_pace_car_order(self, order_id: str, process_step: str) -> None:

       
        

        pace_car_orders = self.query_client.get_child_identities("PACE-CAR", 100, 0)

        pace_car_order = next((pco for pco in pace_car_orders if pco.name == order_id), None)

        p = Parameter()

        p.name = "Process Step"
        p.value = process_step

        pc = ParameterCollection()

        pc.append(p)

        if pace_car_order is None:

            pace_car_order = Identity(
                identifier=str(uuid.uuid4()),
                typeIdentifier="PACE-CAR",
                name=order_id,
                properties=pc
            )

            datetime

            event_context = EventContext(
                ActorId="Workflow Services",
                Start=datetime.datetime.now().isoformat(),
                End=datetime.datetime.now().isoformat()
            )

            self.accessioning_client.register(pace_car_order, event_context)

        else:
           
            properties = pc

            process_step_property = next((p for p in properties if p.name == "Process Step"), None)
            
            if process_step_property is not None:
                process_step_property.value = process_step
            else:
                # Handle the case where there is no property named "Process Step"
                pass
            new_pace_car_order = Identity(
                identifier=pace_car_order.identifier,
                typeIdentifier=pace_car_order.typeIdentifier,
                name=pace_car_order.name,
                properties=properties
            )
     
            event_context = EventContext(
                ActorId="Workflow Services",
                Start=datetime.datetime.now().isoformat(),
                End=datetime.datetime.now().isoformat()
            )
            self.accessioning_client.register(new_pace_car_order, event_context)
    def pace_car_status_check(self, order_id:str, process_step:str) -> bool:

        all_pace_car_orders = self.query_client.get_child_identities("PACE-CAR", 100, 0)

        pace_car_orders = [pco for pco in all_pace_car_orders if any(p.name == "Process Step" and p.value == process_step for p in pco.properties)]

        pace_car_orders = sorted(self.query_client.get_child_identities("PACE-CAR", 100, 0),key=lambda pco: pco.name)

        current_index = next((i for i, pco in enumerate(pace_car_orders) if pco.name == order_id),-1)

        if current_index > 0:
            # Check all previous pace car orders in reverse order
            for i in range(current_index - 1, -1, -1):
                previous_pace_car_order = pace_car_orders[i]
                process_step_property = next(
                    (p for p in previous_pace_car_order.properties if p.name == "Process Step"),
                    None
                )

                if process_step_property is not None and process_step_property.value == process_step:
                    logger.info(
                        "Order ID: %s is waiting for %s to complete process step %s",
                        order_id, previous_pace_car_order.name, process_step_property.value
                    )
                    return False  # Found a match, so not ready

            return True  # If no matching process step is found in previous orders

        if current_index == 0:
            return True  # First order, no previous orders to check
        if current_index == -1:
            logger.info("Order ID: %s not found in pace car orders", order_id)
            return True

        return False
    
    def wait_for_pace_car(self, order_id: str, process_step: str, time_to_wait: int) -> None:

        process_complete = False

        while process_complete == False:

            process_complete = self.pace_car_status_check(order_id, process_step)

            logger.info(f'Waiting for previous order  to complete process step {process_step}...')

            time.sleep(time_to_wait)
        
        logger.info(f'Process step {process_step} is complete for order {order_id}.')