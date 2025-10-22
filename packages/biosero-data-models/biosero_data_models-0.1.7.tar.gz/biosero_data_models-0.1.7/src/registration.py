
import configparser
import datetime


from biosero.datamodels.resources import Identity, CommonTypeIdentifiers
from biosero.dataservices.restclient import QueryClient, AccessioningClient

from biosero.datamodels.events import EventContext, Event, EventMessage, LiquidTransferEvent, LocationChangedEvent
from biosero.datamodels.restclients import EventClient
from biosero.datamodels.parameters import Parameter, ParameterCollection, ParameterValueType
from biosero.datamodels.measurement import Volume, VolumeUnit
from biosero.datamodels.adapter import TemplateRegistrar


#rom identity_demo.types import ReagentTypes, LabwareTypes
from typing import List, Any, Optional, TypeVar

T = TypeVar('T')


config = configparser.ConfigParser()
config.read('config.ini')
data_services_url: str = config["DATA SERVICES"]["url"]
query_client = QueryClient(data_services_url)

microplates = query_client.get_child_identities(
    CommonTypeIdentifiers.Generic96WellPlateType, 100, 0)


def register_reagent():

    reagent = Identity()
    reagent.identifier = 'REAGENT-PURPLE-STUFF'
    reagent.name = "Purple Stuff"
    reagent.typeIdentifier = CommonTypeIdentifiers.Reagent

    pc = ParameterCollection()

    p = Parameter()
    p.name = "color"
    p.value = "purple"
    p.valueType = ParameterValueType.STRING

    pc.append(p)

    reagent.properties = pc
    reagent.isInstance = True
    #assecioning_client = AccessioningClient(data_services_url)

    #event_context = EventContext()

    event_context = EventContext(
    ActorId ="lab_tech_1",
    Start=datetime.datetime.now().isoformat()
)

    # event_context.Start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # event_context.ActorId = "Python Script"
    # event_context.Start = event_context.Start = datetime.datetime.now().isoformat()

    #assecioning_client.register(reagent, event_context)

    with AccessioningClient(data_services_url) as accessioning_client:
        accessioning_client.register(reagent, event_context)

    print("Reagent registered")




def create_notebook_request(request_id: str, 
                            assay: str,
                            samples: int,
                            requestor: str, 
                            request_date: str, 
                            request_status: str, 
                            request_description: str) -> Identity:

    notebook_request = Identity()
    notebook_request.identifier = request_id
    notebook_request.name = request_id
    notebook_request.typeIdentifier = "SIGNALS-NOTEBOOK-REQUEST"

    pc = ParameterCollection()

    requested_by = Parameter()

    requested_by.name = "Requested By"
    requested_by.value = requestor
    requested_by.value_type = ParameterValueType.STRING

    pc.append(requested_by)

    samples_param = Parameter()
    samples_param.name = "Samples"
    samples_param.value_type = ParameterValueType.INTEGER
    samples_param.value = str(samples)

    pc.append(samples_param)

    date = Parameter()
    date.name = "Request Date"
    date.value = request_date
    date.value_type = ParameterValueType.STRING

    pc.append(date)

    status = Parameter()
    status.name = "Request Status"
    status.value = request_status
    status.value_type = ParameterValueType.STRING

    pc.append(status)

    batch_order = Parameter()
    batch_order.name = "Batch Order"
    batch_order.value = "None"
    batch_order.value_type = ParameterValueType.STRING

    pc.append(batch_order)

    assay_param = Parameter()
    assay_param.name = "Assay"
    assay_param.value = assay
    assay_param.value_type = ParameterValueType.STRING

    pc.append(assay_param)
    

    notebook_request.properties = pc

    notebook_request.isInstance = True

    accessioning_client = AccessioningClient(data_services_url)

    event_context = EventContext()

    event_context.Start = datetime.datetime.now().isoformat()
    event_context.ActorId = "Python Script"

    accessioning_client.register(notebook_request, event_context)





def register_reagent_types():

    for reagent in ReagentTypes.RegentTypes:

        reagent_type = Identity()

        reagent_type.identifier = reagent.identifier
        reagent_type.name = reagent.name
        reagent_type.typeIdentifier = reagent.typeIdentifier

        pc = ParameterCollection()

        # Create and append first parameter
        p1 = Parameter()
        p1.name = "production_material_id"
        p1.value = reagent.production_material_id
        p1.value_type = ParameterValueType.STRING
        pc.append(p1)

        # Create and append second parameter
        p2 = Parameter()
        p2.name = "dev_material_id"
        p2.value = reagent.dev_material_id
        p2.value_type = ParameterValueType.STRING
        pc.append(p2)

        # Create and append third parameter
        p3 = Parameter()
        p3.name = "thawed_expiration_date"
        p3.value = reagent.thawed_expiration_date
        p3.value_type = ParameterValueType.STRING
        pc.append(p3)

        reagent_type.properties = pc

        reagent_type.isInstance = False

        accessioning_client = AccessioningClient(data_services_url)

        event_context = EventContext()

        event_context.Start = datetime.datetime.now().isoformat()
        event_context.ActorId = "Python Script"

        accessioning_client.register(reagent_type, event_context)

        print(f"Reagent Type {reagent.name} registered")


def register_microplates():

    for microplate in LabwareTypes.LabwareTypes:

        microplate_type = Identity()

        microplate_type.identifier = microplate.identifier
        microplate_type.name = microplate.name
        microplate_type.typeIdentifier = microplate.typeIdentifier

        pc = ParameterCollection()

        p = Parameter()
        p.name = "dead_volume"
        p.value = microplate.dead_volume
        p.value_type = ParameterValueType.DOUBLE

        pc.append(p)

        p.name = "max_volume"
        p.value = microplate.max_volume
        p.value_type = ParameterValueType.DOUBLE

        microplate_type.properties = pc

        microplate_type.isInstance = True

        accessioning_client = AccessioningClient(data_services_url)

        event_context = EventContext()

        event_context.Start = datetime.datetime.now().isoformat()
        event_context.ActorId = "Python Script"

        accessioning_client.register(microplate_type, event_context)

        print(f"Microplate Type {microplate.name} registered")


def publish_event(event_item: T, actor_id: Optional[str] = None, operator_id: Optional[str] = None) -> None:

    transfer_event = Event(event_item)

    transfer_msg = EventMessage.from_event(transfer_event)

    transfer_msg.ActorId = actor_id
    transfer_msg.OperatorId = operator_id

    event_client = EventClient(data_services_url)

    event_client.publish_event(transfer_msg)





# create_notebook_request("REQ-0001","Peptide Stability", 10, "John Doe", "2021-09-01", "Pending", "Request for peptide stability testing")
# create_notebook_request("REQ-0002","Peptide Stability", 10, "John Doe", "2021-09-01", "Pending", "Request for peptide stability testing")
# create_notebook_request("REQ-0003","Peptide Stability", 10, "John Doe", "2021-09-01", "Pending", "Request for peptide stability testing")
# create_notebook_request("REQ-0004","Peptide Stability", 10, "John Doe", "2021-09-01", "Pending", "Request for peptide stability testing")
# create_notebook_request("REQ-0005","Peptide Stability", 10, "John Doe", "2021-09-01", "Pending", "Request for peptide stability testing")

register_reagent()











# query_client = QueryClient(data_services_url)

# ids = query_client.get_child_identities('TV-TMD-35034', 100, 0)
# b =[]

# liquidTransfer = LiquidTransferEvent(

#     SourceIdentifier="REAGENT-PURPLE-STUFF",
#     DestinationIdentifier="FG1001",
#     ActualTransferVolume=Volume(100, VolumeUnit.uL), #.to_dict(),
#     TimeStamp=datetime.datetime.now().isoformat(),

# )



# locationChangedEvent = LocationChangedEvent(

#     ParentIdentifier="STORAGE_RX",
#     ItemIdentifier="FG1001",
#     Coordinates=None

# )



# LocationChangedEvent = LocationChangedEvent(

#         ParentIdentifier = "WORKCELL-ANALYTICAL",
#         ItemIdentifier="Plate Storage"
#     )


#liquidTransfer.source_identifier = "REAGENT-PURPLE-STUFF"

#liquidTransfer.destination_identifier = "FG1001"

# This might not work
#liquidTransfer.actual_transfer_volume = Volume(100, VolumeUnit.uL)

#liquidTransfer.timestamp = datetime.datetime.now()

#publish_event(LocationChangedEvent, "Python Script", "Python Script")

#publish_event(locationChangedEvent, "Python Script", "Python Script")

# print("Event published")
# register_reagent_types()
# register_microplates()
# print(microplates)
