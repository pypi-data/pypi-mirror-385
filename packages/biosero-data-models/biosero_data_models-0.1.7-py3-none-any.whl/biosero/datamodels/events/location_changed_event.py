
from dataclasses import dataclass, asdict

from datetime import datetime
from typing import Optional

# @dataclass
# class LocationChangedEvent(Location):
#     ClassName: str = "Biosero.DataModels.Events.LocationChangedEvent"

#     def to_dict(self):
#         data = super().to_dict()
#         data["ClassName"] = self.ClassName
#         return data


@dataclass
class LocationChangedEvent():
    ParentIdentifier: str
    ItemIdentifier: str
    Coordinates: Optional[str] = None 
    TimeStamp: Optional[datetime] = None



    ClassName: str = "Biosero.DataModels.Events.LocationChangedEvent"

    # def to_dict(self):
    #     data = super().to_dict()
    #     data["ClassName"] = self.ClassName
    #     return data
    def to_dict(self):
        data = asdict(self)
        # data["Coordinates"] = self.Coordinates.to_dict() if isinstance(self.Coordinates, str) else self.Coordinates
        # data["TimeStamp"] = self.TimeStamp.isoformat() if isinstance(self.TimeStamp, datetime) else self.TimeStamp
        # data["AccessPolicy"] = self.AccessPolicy.to_dict() if hasattr(self, 'AccessPolicy') else None
        return data
    
    def __str__(self):
        return (f"LocationChangedEvent("
                f"ParentIdentifier={self.ParentIdentifier}, "
                f"ItemIdentifier={self.ItemIdentifier}, "
                f"Coordinates= {self.Coordinates}")
