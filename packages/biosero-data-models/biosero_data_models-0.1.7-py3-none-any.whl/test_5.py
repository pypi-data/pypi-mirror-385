import asyncio
from biosero.datamodels.restclients import OrderScheduler
from biosero.dataservices.restclient import QueryClient
from biosero.datamodels.ordering import Order
from biosero.datamodels.resources import Identity
from biosero.datamodels.events import EventContext

#from biosero.utilities.plate_data import PlateData

from biosero.datamodels.parameters import ParameterCollection, Parameter, ParameterValueType
import datetime
import json
import sys
from typing import Optional, TypeVar, Generic
print("Is TTY:", sys.stderr.isatty())

T = TypeVar("T")


# from biosero.datamodels.events import EventSearchParameters, EventMessage
# from biosero.dataservices.restclient import QueryClient

# qc = QueryClient("http://10.0.0.234:30081")






# sp = EventSearchParameters(
#     Topic='Biosero.DataModels.Events.InventoryComplete',
#     ActorId='WORKCELL-REAGENT-DISPENSE',
# )

# events = qc.get_events(sp, 10000, 0)

query_client = QueryClient("http://localhost:8105")


async def main():


    order_scheduler = OrderScheduler("http://10.0.0.234:30081")  

    barcode = 'LDV13762'

    input_pc = ParameterCollection() 
    p1 = Parameter(name="Barcode",value=barcode, valueType=ParameterValueType.STRING)

    input_pc.append(p1)
    order = Order(templateName="Get Mosaic Plate Map", inputParameters=input_pc)
    
    order_response: Order = await order_scheduler.schedule_order(order=order, wait=True)

    plate_map: str = order_response.get_output_parameter_value("Plate Map")


    extraction_paramters = ParameterCollection()
    plate_map_paramter = Parameter(name="Plate Map", value=plate_map, valueType=ParameterValueType.STRING)

    extraction_paramters.append(plate_map_paramter)

    dna_extraction_order = Order(templateName="DNA Extraction", inputParameters=extraction_paramters)

    await order_scheduler.request_transfer(source_station_id="EXTRACTION-STATION", destination_station_id="SAMPLE-PREP-STATION",item_ids=barcode, created_by="Python", order_id="", metadata="", wait=True)


    library_prep_order = Order(templateName="Library Preperation")

    await order_scheduler.schedule_order(order=library_prep_order, wait=True)


    await order_scheduler.close()





asyncio.run(main())




#print(f"Order completed: {final_order.identifier}")


# from dataservices.adapter.actions import Actions


# action = Actions("http://10.0.0.234:30081")
    
# result_3, result_2, result_3 = action.get_items_at_location("SYSTEM-B-STORE-1")

from biosero.datamodels.adapter import OrderProcessor

#op = OrderProcessor(url= "https://dataservices-edge.onrender.com", action_templates="",actions_instance="")

from biosero.datamodels.events import (
    Event,
    EventMessage,
    ModuleStatusUpdateEvent,
    ModuleStatus
)
from biosero.datamodels.restclients import EventClient

def publish_event(event_item: T, actor_id: Optional[str] = None, operator_id: Optional[str] = None) -> None:

    transfer_event = Event(event_item)

    transfer_msg = EventMessage.from_event(transfer_event)

    transfer_msg.ActorId = actor_id
    transfer_msg.OperatorId = operator_id

    event_client = EventClient("http://localhost:8105")  

    event_client.publish_event(transfer_msg)


status_details = json.dumps({
    "Name": "",
    "PlatesStarted": 1,
    "PlatesComplete": 0,
    # "NotStarted": not_started,
    "TotalPlates": 10,
    "StatusDetails": "Not running"
})


module_update_event = ModuleStatusUpdateEvent(
    Id=0,
    ModuleIdentifier="MOMENTUM",
    ModuleName="Momentum",
    Status=ModuleStatus.Error,
    StatusDetails=status_details
)


publish_event(module_update_event, actor_id="MOMENTUM-1", operator_id="OPERATOR-1")


module_update_event = ModuleStatusUpdateEvent(
    Id=0,
    ModuleIdentifier="MOSAIC",
    ModuleName="Mosaic",
    Status=ModuleStatus.Busy,
    StatusDetails=status_details
)

publish_event(module_update_event, actor_id="MOSAIC-1", operator_id="OPERATOR-1")

publish_event(module_update_event, actor_id="MOMENTUM-1", operator_id="OPERATOR-1")


module_update_event = ModuleStatusUpdateEvent(
    Id=0,
    ModuleIdentifier="ANALYTICAL",
    ModuleName="Analytical",
    Status=ModuleStatus.Busy,
    StatusDetails=status_details
)

publish_event(module_update_event, actor_id="ANALYTICAL", operator_id="OPERATOR-1")




module_update_event = ModuleStatusUpdateEvent(
    Id=0,
    ModuleIdentifier="CELL-CULTURE",
    ModuleName="Cell Culture",
    Status=ModuleStatus.Busy,
    StatusDetails=status_details
)

publish_event(module_update_event, actor_id="CELL CULTURE", operator_id="OPERATOR-1")

module_update_event = ModuleStatusUpdateEvent(
    Id=0,
    ModuleIdentifier="SAMPLE-PREP",
    ModuleName="Sample Prep",
    Status=ModuleStatus.Busy,
    StatusDetails=status_details
)

publish_event(module_update_event, actor_id="Sample Prep", operator_id="OPERATOR-1")



# op.poll_endpoint()
