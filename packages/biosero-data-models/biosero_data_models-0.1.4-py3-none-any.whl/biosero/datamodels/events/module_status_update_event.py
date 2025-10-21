from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum

class ModuleStatus(Enum):
    Ready = 0
    Busy = 1
    Error = 2
    Offline = 3

@dataclass
class ModuleStatusUpdateEvent:
    Id: int
    ModuleIdentifier: str
    ModuleName: str
    Status: ModuleStatus
    StatusDetails: Optional[str] = None
    Image: Optional[str] = None
    OrdersBeingProcessed: Optional[List[str]] = None
    AllowSimultaneousExecution: Optional[bool] = False
    InstrumentIdentifiers: Optional[List[str]] = None
    Capabilities: Optional[List[str]] = None
    
    ClassName: str = "Biosero.DataModels.Events.ModuleStatusUpdateEvent"
    
    def to_dict(self):
        data = asdict(self)
        data["Status"] = self.Status.value  # Convert Enum to string
        return data
    
    def __str__(self):
        return (f"ModuleStatusUpdateEvent(" 
                f"Id={self.Id}, "
                f"ModuleIdentifier={self.ModuleIdentifier}, "
                f"ModuleName={self.ModuleName}, "
                f"Status={self.Status}, "
                f"StatusDetails={self.StatusDetails}, "
                f"Image={self.Image}, "
                f"OrdersBeingProcessed={self.OrdersBeingProcessed}, "
                f"AllowSimultaneousExecution={self.AllowSimultaneousExecution}, "
                f"InstrumentIdentifiers={self.InstrumentIdentifiers}, "
                f"Capabilities={self.Capabilities})")
