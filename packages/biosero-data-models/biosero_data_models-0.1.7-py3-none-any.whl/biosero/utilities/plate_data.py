from biosero.dataservices.restclient import QueryClient, AccessioningClient
from biosero.datamodels.restclients import EventClient
from biosero.datamodels.measurement import Coordinates
from biosero.datamodels.resources import Identity, CommonTypeIdentifiers
from biosero.datamodels.parameters import Parameter, ParameterCollection, ParameterValueType
from biosero.datamodels.events import LocationChangedEvent, IEvent, EventMessage, EventContext
import json
import jsonpickle
import httpx

import asyncio

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class Well:
    def __init__(self, identifier: str, location: Coordinates):
        self.identifier = identifier
        self.location = json.loads(location)  # Parse coordinates once and store as a dictionary

class PlateData:
    def __init__(self, url: str):
        """Initialize PlateData with a URL."""
        self.url = url
        self.barcode = None  # Store the barcode after building plate data
        self.wells = []  # List of Well objects
        self.query_client = QueryClient(url)
        self.accessioning_client = AccessioningClient(url)
        self.event_client = EventClient(url)
        self._built = False

    def add_well(self, identifier: str, location: Coordinates):
        """Add a well to the wells list."""
        well = Well(identifier, location)
        self.wells.append(well)

    def get_wells(self):
        """Return a list of all wells."""
        return self.wells

    def get_well_identifier(self, row: int, column: int) -> str:
        """Return the identifier of the well at the specified row and column."""
        if not self._built:
            raise RuntimeError("Plate data has not been built. Call `build_plate_data(barcode)` or `build_plate_data_for(barcode)` first.")
        for well in self.wells:
            if well.location.get('Row') == row and well.location.get('Column') == column:
                return well.identifier
        return None

    async def register_plate_and_wells(self, barcode: str, name: str, rows: int = 8, columns: int = 12, typeIdentifier: str = CommonTypeIdentifiers.MicrotitierPlate, parameters: ParameterCollection = None):
        """
        Asynchronously register the plate and its wells as identities in a batch,
        update their locations concurrently using event_client.publish_async.
        """

        if parameters is None:
            parameters = ParameterCollection()

        event_context = EventContext()

        plate_identity = Identity()
        plate_identity.identifier = barcode
        plate_identity.typeIdentifier = typeIdentifier
        plate_identity.name = name
        plate_identity.isInstance = True
        plate_identity.inheritProperties = True
        plate_identity.properties = parameters

        identities_to_register = [plate_identity]
        well_identities = []

        self.wells.clear()
        self.barcode = barcode

        for row in range(1, rows + 1):
            for column in range(1, columns + 1):
                well_identifier = f'[{barcode}][{row}][{column}]'

                well_identity = Identity()
                well_identity.identifier = well_identifier
                well_identity.typeIdentifier = CommonTypeIdentifiers.Well
                well_identity.isInstance = True
                well_identity.inheritProperties = True

                well_identities.append(well_identity)
                identities_to_register.append(well_identity)

        self.accessioning_client.register_many(identities_to_register, event_context)

        timeout = httpx.Timeout(30.0, connect=10.0)
        semaphore = asyncio.Semaphore(10)

        async with httpx.AsyncClient(timeout=timeout) as client:
            async def limited_publish(transfer_message):
                async with semaphore:
                    return await self.event_client.publish_async(transfer_message, client)

            publish_tasks = []

            for well_identity in well_identities:
                row = int(well_identity.identifier.split('][')[1])
                column = int(well_identity.identifier.split('][')[2].strip(']'))

                coordinates = Coordinates(row=row, column=column)
                location_changed_event = LocationChangedEvent(
                    ParentIdentifier=plate_identity.identifier,
                    ItemIdentifier=well_identity.identifier,
                    Coordinates=coordinates
                )

                transfer_event = IEvent(context=event_context, data=location_changed_event)
                transfer_message = EventMessage.from_event(transfer_event)

                self.add_well(well_identity.identifier, coordinates)

                publish_tasks.append(limited_publish(transfer_message))

            await asyncio.gather(*publish_tasks)

        self._built = True


    def build_plate_data(self, barcode: str):
        """Build the PlateData instance by querying items at the specified location."""
        self.wells.clear()
        self.barcode = barcode  # Store the barcode for reference
        items = self.query_client.get_items_at_location(barcode, 10000, 0)
        for item in items:
            location = self.query_client.get_location(item.identifier)
            self.add_well(item.identifier, location.coordinates)
        self._built = True

    def build_plate_data_for(self, barcode: str):
        """Alias for build_plate_data to be called explicitly when needed before registration."""
        self.build_plate_data(barcode)
