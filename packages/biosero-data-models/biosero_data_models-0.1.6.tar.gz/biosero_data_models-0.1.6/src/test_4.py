import json
from biosero.identities import (
    Resource,
    Vessel,
    Container,
    Device,
    Workcell,
    AssignmentAPI,
    Accessioning,
    MetaData,
    Coordinates
)


accesioning_client = Accessioning(base_url="https://dataservices-edge.onrender.com")
api = AssignmentAPI(base_url="https://dataservices-edge.onrender.com")


def register_plate(barcode:str, rows:int=8, columns:int=12) -> None:


    container_ref_id = barcode

    container = Container(
        containerRefId=barcode,
        name=barcode,
        containerType="Rack",
        containerState="Available",
        barcode=barcode,
        material="string",
        format="96",
        hasLid=False,
        rows=rows,
        columns=columns,
        positions=MetaData.get_coordinates_strings(rows, columns),  # Generates positions like ['1,1', '1,2', ..., '8,12']
        properties={
            "Dead Volume": 50,
            "Well Shape": "Round"
        }
    )

    accesioning_client.create_container(container)
    for pos in container.positions:

        vessel_ref_id = f"[{container_ref_id}][{pos}]"

        # well_position  = Coordinates(positon_x, position_y).to_serialized_string()


        vessel = Vessel(
            vesselRefId=vessel_ref_id,  # This should match the container and position
            name=vessel_ref_id,
            vesselType="Well",
            vesselState="Available",
            format="96",
            capacity=1000,
            capacityUnit="Microliter",
            material="string",
            barcode=vessel_ref_id,
            hasLid=True,
            properties={
                "Dead Volume": 50,
            }
        )

        accesioning_client.create_vessel(vessel)

        api.assign_vessel_to_container(vessel_ref_id=vessel_ref_id, container_ref_id=container_ref_id, container_position=pos)

register_plate("Plate_1", 8, 12)  # Example usage with default rows and columns (8x12)