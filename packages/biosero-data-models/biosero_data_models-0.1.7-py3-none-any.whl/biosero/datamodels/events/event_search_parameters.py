
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json

@dataclass
class EventSearchParameters:
    """
    Class representing the event search parameters.
    """
    # Lower time bounds of the event search
    EventId: Optional[str] = None
    Data: Optional[str] = None
    Start: Optional[datetime] = None
    
    # Upper time bounds of the event search
    End: Optional[datetime] = None
    
    # Topic
    Topic: Optional[str] = None
    
    # Organization identifier
    OrganizationId: Optional[str] = None
    
    # Group identifier
    GroupId: Optional[str] = None
    
    # Owner identifier
    OwnerId: Optional[str] = None
    
    # Association identifier
    AssociationId: Optional[str] = None
    
    # Activity identifier
    ActivityId: Optional[str] = None
    
    # Actor identifier
    ActorId: Optional[str] = None
    
    # Subjects contains value, will search for events containing this value in the subjects collection
    SubjectsContains: Optional[str] = None
    
    # Orchestrator identifier
    OrchestratorId: Optional[str] = None
    
    # Operator identifier
    OperatorId: Optional[str] = None
    
    # Module identifier
    ModuleId: Optional[str] = None