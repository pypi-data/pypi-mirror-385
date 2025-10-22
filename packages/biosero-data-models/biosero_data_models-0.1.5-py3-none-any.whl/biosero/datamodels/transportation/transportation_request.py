import json
from enum import Enum
from datetime import datetime

class UnknownStringEnumConverter(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TransportationRequestStatus):
            return obj.name
        return super().default(obj)

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
    def __init__(self, requestIdentifier: str, requestGroupIdentifier: str, orderIdentifier: str,
                 vehicleIdentifier: str, assignedToIdentifier: str, status: TransportationRequestStatus,
                 previousStatus: TransportationRequestStatus = None, statusDetails: str = "",
                 itemIdentifier: str = "", itemMetadata: str = "", sourceStationIdentifier: str = "",
                 destinationStationIdentifier: str = "", locationAtSource: str = "", 
                 locationAtDestination: str = "", createdBy: str = "", createdTime: datetime = None,
                 startedTime: datetime = None, pickupTime: datetime = None, dropoffTime: datetime = None,
                 completeTime: datetime = None, errorTime: datetime = None):
        self.requestIdentifier = requestIdentifier
        self.requestGroupIdentifier = requestGroupIdentifier
        self.orderIdentifier = orderIdentifier
        self.vehicleIdentifier = vehicleIdentifier
        self.assignedToIdentifier = assignedToIdentifier
        self.status = status
        self.previousStatus = previousStatus
        self.statusDetails = statusDetails
        self.itemIdentifier = itemIdentifier
        self.itemMetadata = itemMetadata
        self.sourceStationIdentifier = sourceStationIdentifier
        self.destinationStationIdentifier = destinationStationIdentifier
        self.locationAtSource = locationAtSource
        self.locationAtDestination = locationAtDestination
        self.createdBy = createdBy
        self.createdTime = createdTime or datetime.now()
        self.startedTime = startedTime
        self.pickupTime = pickupTime
        self.dropoffTime = dropoffTime
        self.completeTime = completeTime
        self.errorTime = errorTime

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4, cls=UnknownStringEnumConverter)
