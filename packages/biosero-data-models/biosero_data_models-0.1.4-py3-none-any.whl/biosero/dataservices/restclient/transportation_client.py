import json
import asyncio
from enum import Enum
from datetime import datetime
from urllib.parse import urlencode
import aiohttp
import requests

class TransportationRequestStatus(Enum):
    Created = "Created"
    Started = "Started"
    ItemNotAvailableAtSource = "ItemNotAvailableAtSource"
    SpaceNotAvailableAtDestination = "SpaceNotAvailableAtDestination"
    NoVehicleAvailable = "NoVehicleAvailable"
    VehicleAssigned = "VehicleAssigned"
    VehicleMovingToPickup = "VehicleMovingToPickup"
    VehicleAtPickup = "VehicleAtPickup"
    BeforePickup = "BeforePickup"
    PickupActive = "PickupActive"
    AfterPickup = "AfterPickup"
    ItemLoadedOnVehicle = "ItemLoadedOnVehicle"
    VehicleMovingToDropoff = "VehicleMovingToDropoff"
    VehicleAtDropoff = "VehicleAtDropoff"
    BeforeDropoff = "BeforeDropoff"
    DropoffActive = "DropoffActive"
    AfterDropoff = "AfterDropoff"
    DropoffComplete = "DropoffComplete"
    Reset = "Reset"
    Aborted = "Aborted"
    Complete = "Complete"
    Canceled = "Canceled"
    Error = "Error"
    Unknown = "Unknown"

class TransportationRequest:
    def __init__(self, **kwargs):
        self.requestIdentifier = kwargs.get("requestIdentifier")
        self.requestGroupIdentifier = kwargs.get("requestGroupIdentifier")
        self.orderIdentifier = kwargs.get("orderIdentifier")
        self.vehicleIdentifier = kwargs.get("vehicleIdentifier")
        self.assignedToIdentifier = kwargs.get("assignedToIdentifier")
        self.status = kwargs.get("status")
        self.previousStatus = kwargs.get("previousStatus")
        self.statusDetails = kwargs.get("statusDetails")
        self.itemIdentifier = kwargs.get("itemIdentifier")
        self.itemMetadata = kwargs.get("itemMetadata")
        self.sourceStationIdentifier = kwargs.get("sourceStationIdentifier")
        self.destinationStationIdentifier = kwargs.get("destinationStationIdentifier")
        self.locationAtSource = kwargs.get("locationAtSource")
        self.locationAtDestination = kwargs.get("locationAtDestination")
        self.createdBy = kwargs.get("createdBy")
        self.createdTime = kwargs.get("createdTime", datetime.now())
        self.startedTime = kwargs.get("startedTime")
        self.pickupTime = kwargs.get("pickupTime")
        self.dropoffTime = kwargs.get("dropoffTime")
        self.completeTime = kwargs.get("completeTime")
        self.errorTime = kwargs.get("errorTime")

class TransportationClient:
    def __init__(self, url=None, urlProvider=None, httpClient=None):
        if httpClient:
            self._httpClient = httpClient
            self._createdClient = False
        else:
            self._httpClient = aiohttp.ClientSession(base_url=url or urlProvider())
            self._createdClient = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._createdClient:
            await self._httpClient.close()

    # async def getActiveRequestsAsync(self, limit, offset):
    #     path = f"api/v2.0/TransportationService/ActiveRequests?limit={limit}&offset={offset}"
    #     async with self._httpClient.get(path) as response:
    #         if response.status == 404:
    #             return []
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut, object_hook=lambda d: TransportationRequest(**d))

    # def getActiveRequests(self, limit, offset):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/ActiveRequests?limit={limit}&offset={offset}"
    #     response = requests.get(path)
    #     if response.status_code == 404:
    #         return []
    #     response.raise_for_status()
    #     return json.loads(response.text, object_hook=lambda d: TransportationRequest(**d))

    # async def getAllStationsAsync(self):
    #     path = "api/v2.0/TransportationService/AllStations"
    #     async with self._httpClient.get(path) as response:
    #         if response.status == 404:
    #             return []
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut)

    # def getAllStations(self):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/AllStations"
    #     response = requests.get(path)
    #     if response.status_code == 404:
    #         return []
    #     response.raise_for_status()
    #     return json.loads(response.text)

    # async def getRequestAsync(self, requestId):
    #     path = f"api/v2.0/TransportationService/Request?requestId={urlencode(requestId)}"
    #     async with self._httpClient.get(path) as response:
    #         if response.status == 404:
    #             raise ValueError(f"Could not find a TransportationRequest with ID {requestId}")
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut, object_hook=lambda d: TransportationRequest(**d))

    # def getRequest(self, requestId):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/Request?requestId={urlencode(requestId)}"
    #     response = requests.get(path)
    #     if response.status_code == 404:
    #         raise ValueError(f"Could not find a TransportationRequest with ID {requestId}")
    #     response.raise_for_status()
    #     return json.loads(response.text, object_hook=lambda d: TransportationRequest(**d))

    # async def getArchivedRequestsAsync(self, start, end, limit, offset):
    #     startFormatted = urlencode(start.isoformat())
    #     endFormatted = urlencode(end.isoformat())
    #     path = f"api/v2.0/TransportationService/ArchivedRequests?start={startFormatted}&end={endFormatted}&limit={limit}&offset={offset}"
    #     async with self._httpClient.get(path) as response:
    #         if response.status == 404:
    #             return []
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut, object_hook=lambda d: TransportationRequest(**d))

    # def getArchivedRequests(self, start, end, limit, offset):
    #     startFormatted = urlencode(start.isoformat())
    #     endFormatted = urlencode(end.isoformat())
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/ArchivedRequests?start={startFormatted}&end={endFormatted}&limit={limit}&offset={offset}"
    #     response = requests.get(path)
    #     if response.status_code == 404:
    #         return []
    #     response.raise_for_status()
    #     return json.loads(response.text, object_hook=lambda d: TransportationRequest(**d))

    # async def getRequestsByGroupIdAsync(self, groupId):
    #     path = f"api/v2.0/TransportationService/RequestsByGroupId?groupId={urlencode(groupId)}"
    #     async with self._httpClient.get(path) as response:
    #         if response.status == 404:
    #             return []
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut, object_hook=lambda d: TransportationRequest(**d))

    # def getRequestsByGroupId(self, groupId):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/RequestsByGroupId?groupId={urlencode(groupId)}"
    #     response = requests.get(path)
    #     if response.status_code == 404:
    #         return []
    #     response.raise_for_status()
    #     return json.loads(response.text, object_hook=lambda d: TransportationRequest(**d))

    # async def getStatusAsync(self, transportationRequestId):
    #     path = f"api/v2.0/TransportationService/Status?requestId={urlencode(transportationRequestId)}"
    #     async with self._httpClient.get(path) as response:
    #         if response.status == 404:
    #             raise ValueError(f"Could not get status because a transportation request with the ID {transportationRequestId} could not be found")
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return TransportationRequestStatus[jsonOut]

    def getStatus(self, transportationRequestId):
        path = f"{self._httpClient._base_url}/api/v2.0/TransportationService/Status?requestId={transportationRequestId}"
        response = requests.get(path)
        if response.status_code == 404:
            raise ValueError(f"Could not get status because a transportation request with the ID {transportationRequestId} could not be found")
        response.raise_for_status()
        return TransportationRequestStatus[response.text.strip('"')]

    # def isComplete(self, requestId):
    #     return self.getStatus(requestId) == TransportationRequestStatus.Complete

    # def isGroupComplete(self, groupId):
    #     inGroup = self.getRequestsByGroupId(groupId)
    #     return all(r.status == TransportationRequestStatus.Complete for r in inGroup)

    # async def requestTransferAsync(self, sourceStationId, destinationStationId, itemIds, orderId, metadata, createdBy=None):
    #     path = "api/v2.0/TransportationService/RequestTransfer"
    #     jsonPayload = {
    #         "sourceStationId": sourceStationId,
    #         "destinationStationId": destinationStationId,
    #         "itemIds": itemIds,
    #         "orderId": orderId if orderId else None,
    #         "metadata": metadata,
    #         "createdBy": createdBy
    #     }
    #     async with self._httpClient.post(path, json=jsonPayload) as response:
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut)

    def requestTransfer(self, sourceStationId, destinationStationId, itemIds, orderId, metadata, createdBy=None):
        path = f"{self._httpClient._base_url}/api/v2.0/TransportationService/RequestTransfer"
        jsonPayload = {
                "sourceStationId": sourceStationId,
                "destinationStationId": destinationStationId,
                "itemIds": itemIds if isinstance(itemIds, list) else [itemIds],
                "metadata": metadata if isinstance(metadata, list) else [metadata],
                "orderId": orderId if orderId else None,
                "createdBy": createdBy
        }
    
        response = requests.post(path, json=jsonPayload)
        response.raise_for_status()
        return json.loads(response.text)
    
    async def close(self):
        if self._createdClient:
            await self._httpClient.close()


    # async def tryAssignRequestAsync(self, transportationRequestId, identifierToAssignTo):
    #     path = f"api/v2.0/TransportationService/TryAssignRequest?requestId={urlencode(transportationRequestId)}&assignTo={urlencode(identifierToAssignTo)}"
    #     async with self._httpClient.post(path) as response:
    #         if response.status == 404:
    #             raise ValueError(f"Could not get status because a transportation request with the ID {transportationRequestId} could not be found")
    #         response.raise_for_status()
    #         jsonOut = await response.text()
    #         return json.loads(jsonOut)

    # def tryAssignRequest(self, transportationRequestId, identifierToAssignTo):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/TryAssignRequest?requestId={urlencode(transportationRequestId)}&assignTo={urlencode(identifierToAssignTo)}"
    #     response = requests.post(path)
    #     if response.status_code == 404:
    #         raise ValueError(f"Could not get status because a transportation request with the ID {transportationRequestId} could not be found")
    #     response.raise_for_status()
    #     return json.loads(response.text)

    # async def updateStatusAsync(self, transportationRequestId, status, statusDetails):
    #     path = f"api/v2.0/TransportationService/UpdateStatus?requestId={urlencode(transportationRequestId)}&status={urlencode(status.name)}&details={urlencode(statusDetails)}"
    #     async with self._httpClient.post(path) as response:
    #         if response.status == 404:
    #             raise ValueError(f"Could not update status because a transportation request with the ID {transportationRequestId} could not be found")
    #         response.raise_for_status()

    # def updateStatus(self, transportationRequestId, status, statusDetails):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/UpdateStatus?requestId={urlencode(transportationRequestId)}&status={urlencode(status.name)}&details={urlencode(statusDetails)}"
    #     response = requests.post(path)
    #     if response.status_code == 404:
    #         raise ValueError(f"Could not update status because a transportation request with the ID {transportationRequestId} could not be found")
    #     response.raise_for_status()

    # async def updateVehicleIdentifierAsync(self, transportationRequestId, vehicleId):
    #     path = f"api/v2.0/TransportationService/UpdateVehicleIdentifier?requestId={urlencode(transportationRequestId)}&vehicleId={urlencode(vehicleId)}"
    #     async with self._httpClient.post(path) as response:
    #         if response.status == 404:
    #             raise ValueError(f"Could not update vehicle ID because a transportation request with the ID {transportationRequestId} could not be found")
    #         response.raise_for_status()

    # def updateVehicleIdentifier(self, transportationRequestId, vehicleId):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/UpdateVehicleIdentifier?requestId={urlencode(transportationRequestId)}&vehicleId={urlencode(vehicleId)}"
    #     response = requests.post(path)
    #     if response.status_code == 404:
    #         raise ValueError(f"Could not update vehicle ID because a transportation request with the ID {transportationRequestId} could not be found")
    #     response.raise_for_status()

    # async def updateItemIdentifierAsync(self, transportationRequestId, itemId):
    #     path = f"api/v2.0/TransportationService/UpdateItemIdentifier?requestId={urlencode(transportationRequestId)}&itemId={urlencode(itemId)}"
    #     async with self._httpClient.post(path) as response:
    #         if response.status == 404:
    #             raise ValueError(f"Could not update item ID because a transportation request with the ID {transportationRequestId} could not be found")
    #         response.raise_for_status()

    # def updateItemIdentifier(self, transportationRequestId, itemId):
    #     path = f"{self._httpClient._base_url}api/v2.0/TransportationService/UpdateItemIdentifier?requestId={urlencode(transportationRequestId)}&itemId={urlencode(itemId)}"
    #     response = requests.post(path)
    #     if response.status_code == 404:
    #         raise ValueError(f"Could not update item ID because a transportation request with the ID {transportationRequestId} could not be found")
    #     response.raise_for_status()
