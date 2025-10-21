import json
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Resource:
    resourceRefId: str
    name: str
    resourceType: str
    resourceState: str
    batch: str
    lot: str
    barcode: str
    requiresRefrigeration: bool
    isHazardous: bool
    expirationDateUtc: str
    quantity: int
    quantityUnit: str
    concentration: float
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Merge properties directly into the instance attributes
        for key, value in self.properties.items():
            setattr(self, key, value)
        # Remove the properties dictionary to avoid duplication
        self.properties = None

    def __str__(self) -> str:
        # Convert the dataclass to a dictionary and remove 'properties' before serialization
        dict_repr = {k: v for k, v in self.__dict__.items() if k != 'properties'}
        return json.dumps(dict_repr, default=str, indent=4)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Resource object to a dictionary without the properties field."""
        return {k: v for k, v in self.__dict__.items() if k != 'properties'}
