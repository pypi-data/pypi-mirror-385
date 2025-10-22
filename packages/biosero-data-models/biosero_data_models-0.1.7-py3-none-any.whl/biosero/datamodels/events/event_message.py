from dataclasses import dataclass, field
from typing import List, Optional, TypeVar, Generic
import json
import uuid
from datetime import datetime
from biosero.datamodels.events import EventContext  # Ensure EventContext has all necessary fields

T = TypeVar('T')

@dataclass
class EventMessage(EventContext):
    Data: str = ""

    @staticmethod
    def build(context: EventContext, data: str) -> 'EventMessage':
        if not context.EventId:
            context.EventId = str(uuid.uuid4())
        return EventMessage(
            AccessPolicy=context.AccessPolicy,
            ActivityId=context.ActivityId,
            ActorId=context.ActorId,
            AssociationId=context.AssociationId,
            Data=data,  # Use raw data, not json.dumps(data)
            EncryptionProvider=context.EncryptionProvider,
            End=context.End,
            EventId=context.EventId,
            GroupId=context.GroupId,
            OrganizationId=context.OrganizationId,
            OwnerId=context.OwnerId,
            SharingPolicy=context.SharingPolicy,
            Start=context.Start,
            Tags=context.Tags,
            Topic=context.Topic,
            ModuleId=context.ModuleId,
            OrchestratorId=context.OrchestratorId,
            RetentionPolicy=context.RetentionPolicy,
            Subjects=context.Subjects,
            OperatorId=context.OperatorId,
            SourceTraceIds=context.SourceTraceIds,
            CreatedDateUtc=context.CreatedDateUtc,
            ExpirationDateUtc=context.ExpirationDateUtc,
        )

    def clone(self) -> 'EventMessage':
        return EventMessage(
            AccessPolicy=self.AccessPolicy,
            ActivityId=self.ActivityId,
            ActorId=self.ActorId,
            AssociationId=self.AssociationId,
            Data=self.Data,
            EncryptionProvider=self.EncryptionProvider,
            End=self.End,
            EventId=self.EventId,
            GroupId=self.GroupId,
            OrganizationId=self.OrganizationId,
            OwnerId=self.OwnerId,
            SharingPolicy=self.SharingPolicy,
            Subjects=self.Subjects,
            Start=self.Start,
            Tags=self.Tags,
            Topic=self.Topic,
            ModuleId=self.ModuleId,
            OrchestratorId=self.OrchestratorId,
            RetentionPolicy=self.RetentionPolicy,
            OperatorId=self.OperatorId,
            SourceTraceIds=self.SourceTraceIds,
            CreatedDateUtc=self.CreatedDateUtc,
            ExpirationDateUtc=self.ExpirationDateUtc,
        )

    def __str__(self) -> str:
        return f"{self.Start} {self.Topic} - {self.AssociationId} {self.ActorId} {self.Data}"

    @staticmethod
    def from_event(event: 'IEvent[T]') -> 'EventMessage':
        # Determine the topic name
        # if hasattr(event, 'ClassName'):
        #     topic_name = event.ClassName
        # elif hasattr(event, 'data') and hasattr(event.data, '__class__'):
        #     topic_name = event.data.__class__.__name__
        # else:
        #     topic_name = type(event).__name__

        topic_name = event.data.ClassName

        # Serialize data if it exists, otherwise pass an empty string
        data = json.dumps(event.data, cls=CustomJSONEncoder) if hasattr(event, 'data') else ""

        return EventMessage(
            AccessPolicy=event.context.AccessPolicy,
            ActivityId=event.context.ActivityId,
            ActorId=event.context.ActorId,
            AssociationId=event.context.AssociationId,
            Data=data,
            EncryptionProvider=event.context.EncryptionProvider,
            End=event.context.End,
            EventId=event.context.EventId,
            GroupId=event.context.GroupId,
            ModuleId=event.context.ModuleId,
            OrchestratorId=event.context.OrchestratorId,
            OrganizationId=event.context.OrganizationId,
            OwnerId=event.context.OwnerId,
            RetentionPolicy=event.context.RetentionPolicy,
            SharingPolicy=event.context.SharingPolicy,
            Start=event.context.Start,
            Subjects=event.context.Subjects,
            Tags=event.context.Tags,
            Topic=topic_name,
            OperatorId=event.context.OperatorId,
            SourceTraceIds=event.context.SourceTraceIds,
            CreatedDateUtc=event.context.CreatedDateUtc,
            ExpirationDateUtc=event.context.ExpirationDateUtc,
        )

@dataclass
class IEvent(Generic[T]):
    context: EventContext
    data: T

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)
