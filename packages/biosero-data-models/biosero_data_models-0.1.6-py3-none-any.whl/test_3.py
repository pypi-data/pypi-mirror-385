import json
from biosero.identities import (
    Resource,
    Vessel,
    Container,
    Device,
    Workcell,
    AssignmentAPI,
    Accessioning
)


accesioning_client = Accessioning(base_url="https://dataservices-edge.onrender.com")

api = AssignmentAPI(base_url="https://dataservices-edge.onrender.com")


workcell = Workcell(
    workcellRefId="WC456",
    name="the dude",
    workcellType="Hybrid",
    workcellState="Available",
    category="string",
    endpoint="string",
    positions=["default"],
    properties={
        "additionalProp1": "string",
        "additionalProp2": "dddd",
        "additionalProp3": "string",
        "additionalProp4": "string",
    },
)


workcell = api_create_workcell = accesioning_client.create_workcell(workcell)



device = Device(
    deviceRefId="DEV124",
    name="string",
    deviceType="Generic",
    deviceState="Available",
    manufacturer="string",
    model="string",
    serialNumber="string",
    positions=["string"],
    properties={
        "additionalProp1": "ssssss",
        "additionalProp2": "string",
        "additionalProp3": "string",
    },
)

device = accesioning_client.create_device(device)

api.assign_device_to_workcell(device_ref_id="DEV124", workcell_ref_id="WC456", workcell_position="default")

container = Container(
    containerRefId="CON123",
    name="string",
    containerType="Rack",
    containerState="Available",
    barcode="string",
    material="string",
    format="string",
    hasLid=True,
    rows=1,
    columns=1,
    positions=["string"],
    properties={
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string",
        "additionalProp4": "string"
    }
)

#accesioning_client.create_container(container)

#api.assign_container_to_device(container_ref_id="CON123", device_ref_id="DEV124", device_position="string")


v =""