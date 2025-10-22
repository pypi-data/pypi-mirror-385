from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, get_origin, get_args


class ModuleRestrictionStrategy(Enum):
    NoRestriction = 1
    UnlessBusy = 2
    UnlessError = 3
    UnlessOffline = 4
    FullRestriction = 5


class OrderStatus(Enum):
    Created = 1
    Invalid = 2
    Validated = 3
    Scheduled = 4
    Running = 5
    Paused = 6
    Error = 7
    Complete = 8
    Canceled = 9
    Consolidated = 10
    Unknown = 11


class SchedulingStrategy(Enum):
    ImmediateExecution = 1
    FirstAvailableSlot = 2


class OrderPriority(Enum):
    Elevated = -1
    Standard = 0
    Unknown = 1


@dataclass
class Order:
    identifier: Optional[str] = None
    parentIdentifier: Optional[str] = None
    sourceIdentifier: Optional[str] = None
    runAfterIdentifier: Optional[str] = None
    restrictToModuleIds: Optional[str] = None
    moduleRestrictionStrategy: Optional[ModuleRestrictionStrategy] = None
    statusDetails: Optional[str] = None
    createdBy: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None
    creationTime: Optional[datetime] = None
    scheduledStartTime: Optional[datetime] = None
    actualStartTime: Optional[datetime] = None
    estimatedDuration: Optional[str] = None
    actualEndTime: Optional[datetime] = None
    templateName: Optional[str] = None
    templateVersion: Optional[str] = None
    templateLastModifiedDateUtc: Optional[datetime] = None
    inputParameters: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    outputParameters: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    assignedTo: Optional[str] = None
    validationErrors: Optional[List[str]] = field(default_factory=list)
    state: Optional[str] = None
    schedulingStrategy: Optional[SchedulingStrategy] = None
    log: Optional[str] = None
    priority: Optional[OrderPriority] = None

    @classmethod
    def from_dict(cls, data: dict):
        processed_data = {}

        for attr_name, attr_type in cls.__annotations__.items():
            att_first_lower = attr_name[0].lower() + attr_name[1:]
            if att_first_lower in data:
                value = data[att_first_lower]
                origin = get_origin(attr_type)
                args = get_args(attr_type)

                if hasattr(attr_type, "__members__"):
                    processed_data[attr_name] = attr_type[value]
                elif origin == Optional and args and issubclass(args[0], datetime):
                    processed_data[attr_name] = datetime.fromisoformat(value) if value else None
                elif origin == Optional and args and get_origin(args[0]) == list and get_args(args[0])[0] == dict:
                    processed_data[attr_name] = value if isinstance(value, list) else [value] if value else None
                else:
                    processed_data[attr_name] = value

        return cls(**processed_data)

    def get_input_parameter_value(self, key: str) -> Optional[Any]:
        return next(
            (item.get("value") for item in self.inputParameters if item.get("name") == key),
            None
        )

    def get_output_parameter_value(self, key: str) -> Optional[Any]:
        return next(
            (item.get("value") for item in self.outputParameters if item.get("name") == key),
            None
        )

    @staticmethod
    def _capitalize_key(key: str) -> str:
        parts = key.split('_')
        return ''.join(word.capitalize() for word in parts)
