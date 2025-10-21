
from biosero.datamodels.events import LiquidTransferEvent, IEvent, EventMessage, EventContext
from biosero.datamodels.restclients import EventClient
from biosero.datamodels.measurement import Volume, VolumeUnit
import datetime
import httpx



class Liquid:
    def __init__(self, url: str):
        """Initialize Liquid with a URL."""
        self.url = url
        self.event_client = EventClient(url)
    

    def Transfer(self,source_identifier:str, destination_identifier:str, volume:Volume, transferError:int=0, transferErrorDescription: str = None):
        """Transfer liquid from source to destination."""


        if transferErrorDescription is not None:

            
            liquid_transfer_event = LiquidTransferEvent(
                SourceIdentifier=source_identifier,
                DestinationIdentifier=destination_identifier,
                ActualTransferVolume=volume,
                TransferError=transferError,

                TimeStamp=datetime.datetime.utcnow(),
                TransferErrorDescription=transferErrorDescription
        )

        else:

            liquid_transfer_event = LiquidTransferEvent(
                SourceIdentifier=source_identifier,
                DestinationIdentifier=destination_identifier,
                ActualTransferVolume=volume,
                TransferError=transferError,

                TimeStamp=datetime.datetime.utcnow()
        )
        
        event_context = EventContext()
        
        transfer_event = IEvent(context=event_context, data=liquid_transfer_event)
        
        transfer_message = EventMessage.from_event(transfer_event)
        
        self.event_client.publish_event(transfer_message)

    # async def async_transfer(self, source_identifier: str, destination_identifier: str, volume: Volume, transfer_error: int = 0):
    #     """Asynchronously transfer liquid from source to destination."""
    #     liquid_transfer_event = LiquidTransferEvent(
    #         SourceIdentifier=source_identifier,
    #         DestinationIdentifier=destination_identifier,
    #         ActualTransferVolume=volume,
    #         TransferError=transfer_error,
    #         TimeStamp=datetime.datetime.utcnow()
    #     )

    #     event_context = EventContext()
    #     transfer_event = IEvent(context=event_context, data=liquid_transfer_event)
    #     transfer_message = EventMessage.from_event(transfer_event)

    #     await self.event_client.publish_async(transfer_message)
    async def async_transfer(self, source_identifier: str, destination_identifier: str, volume: Volume, transfer_error: int = 0, client: httpx.AsyncClient = None):
        """
        Asynchronously transfer liquid from source to destination using a shared client.
        """
        liquid_transfer_event = LiquidTransferEvent(
            SourceIdentifier=source_identifier,
            DestinationIdentifier=destination_identifier,
            ActualTransferVolume=volume,
            TransferError=transfer_error,
            TimeStamp=datetime.datetime.utcnow()
        )

        event_context = EventContext()
        transfer_event = IEvent(context=event_context, data=liquid_transfer_event)
        transfer_message = EventMessage.from_event(transfer_event)

        if client is None:
            timeout = httpx.Timeout(30.0, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as new_client:
                await self.event_client.publish_async(transfer_message, new_client)
        else:
            await self.event_client.publish_async(transfer_message, client)