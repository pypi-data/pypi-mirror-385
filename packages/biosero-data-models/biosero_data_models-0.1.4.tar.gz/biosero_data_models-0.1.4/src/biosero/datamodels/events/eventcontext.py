from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class EventContext:
    Topic: str = None
    EventId: str = None
    Start: datetime = None
    End: datetime = None
    OrganizationId: str = None
    GroupId: str = None
    OwnerId: str = None
    AccessPolicy: str = None
    SharingPolicy: str = None
    RetentionPolicy: str = None
    AssociationId: str = None
    ActivityId: str = None
    ActorId: str = None
    Subjects: List[str] = None
    Tags: List[str] = None
    OrchestratorId: str = None
    OperatorId: str = None
    ModuleId: str = None
    SourceTraceIds: List[str] = None
    EncryptionProvider: str = None
    CreatedDateUtc: datetime = None
    ExpirationDateUtc: datetime = None

    # def __init__(self, associationId=None, actorId=None):
    #     self.ActorId = actorId
    #     self.AssociationId = associationId