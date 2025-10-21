import datetime
from biosero.datamodels.events import (
    Event,
    EventMessage,
    ModuleStatusUpdateEvent,
    ModuleStatus
)
from biosero.datamodels.restclients import EventClient
# from identity_demo.types import ReagentTypes, LabwareTypes
from typing import Optional, TypeVar

T = TypeVar("T")

def publish_event(event_item: T, actor_id: Optional[str] = None, operator_id: Optional[str] = None) -> None:

    transfer_event = Event(event_item)

    transfer_msg = EventMessage.from_event(transfer_event)

    transfer_msg.ActorId = actor_id
    transfer_msg.OperatorId = operator_id

    event_client = EventClient("http://10.0.0.234:30081")

    event_client.publish_event(transfer_msg)



module_update_event = ModuleStatusUpdateEvent(Id=0, 
                                              ModuleIdentifier="MOMENTUM-1",
                                              ModuleName="Momentum 1",
                                              Status=ModuleStatus.Ready)


publish_event(module_update_event, "Python Script", "Python Operator")

