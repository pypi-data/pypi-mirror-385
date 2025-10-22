from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from biosero.datamodels.ordering import Order, ModuleRestrictionStrategy, SchedulingStrategy, OrderPriority
from biosero.datamodels.parameters import ParameterCollection
from enum import Enum

@dataclass
class OrderDto:
    Identifier: Optional[str] = None
    ParentIdentifier: Optional[str] = None
    RunAfterIdentifier: Optional[str] = None
    RestrictToModuleIds: Optional[str] = None
    ModuleRestrictionStrategy: Optional[ModuleRestrictionStrategy] = None
    CreatedBy: Optional[str] = None
    Notes: Optional[str] = None
    ScheduledStartTime: Optional[datetime] = None
    EstimatedDurationInMinutes: Optional[float] = None
    TemplateName: Optional[str] = None
    InputParameters: Optional[ParameterCollection] = None
    OutputParameters: Optional[ParameterCollection] = None
    SchedulingStrategy: Optional[SchedulingStrategy] = None
    Priority: Optional[OrderPriority] = None

    @staticmethod
    def from_order(order: Order) -> 'OrderDto':
        return OrderDto(
            Identifier=order.identifier,
            ParentIdentifier=order.parentIdentifier ,
            RunAfterIdentifier=order.runAfterIdentifier,
            RestrictToModuleIds=order.restrictToModuleIds,
            ModuleRestrictionStrategy=order.moduleRestrictionStrategy,
            CreatedBy=order.createdBy,
            Notes=order.notes,
            ScheduledStartTime=order.scheduledStartTime,
            EstimatedDurationInMinutes=order.estimatedDuration.total_seconds() / 60 if order.estimatedDuration else None,
            TemplateName=order.templateName,
            InputParameters=order.inputParameters,
            OutputParameters=order.outputParameters,
            SchedulingStrategy=order.schedulingStrategy,
            Priority=order.priority
        )
    def to_dict(self):
        result = {}
        for key, value in self.__dict__.items():
            if value is None:
                continue
            if isinstance(value, ParameterCollection):
                result[key] = value.to_dict() if value else None
            elif isinstance(value, Enum):
                result[key] = value.value  # Convert Enum to its value
            elif isinstance(value, datetime):
                result[key] = value.isoformat()  # Convert datetime to ISO string
            else:
                result[key] = value
        return result
    
    