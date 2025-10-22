from typing import Optional, List,  get_origin, get_args
from datetime import datetime
from dataclasses import dataclass

@dataclass
class OrderTemplate:

    Name: Optional[str] = None
    Category: Optional[str] = None
    Description: Optional[str] = None
    RequiredCapabilities: Optional[str] = None
    AvailableModuleIds: Optional[str] = None
    Icon: Optional[str] = None
    Color: Optional[str] = None
    InputParameters: Optional[List[dict]] = None
    OutputParameters: Optional[List[dict]] = None
    ValidationScript: Optional[str] = None
    ValidationScriptLanguage: Optional[str] = "C#"
    DefaultEstimatedDuration: Optional[str] = None
    DurationEstimationScript: Optional[str] = None
    DurationEstimationScriptLanguage: Optional[str] = "C#"
    SchedulingStrategy: Optional[str] = None
    Workflow: Optional[str] = None
    IsHidden: Optional[bool] = False
        
    @classmethod
    def from_dict(cls, data: dict):

        processed_data = {}

        for attr_name, attr_type in cls.__annotations__.items():
            att_first_lower = attr_name[0].lower() + attr_name[1:]
            if att_first_lower in data:
                
                value = data[att_first_lower]

                # Get the origin of the type (e.g., List, Optional) and its arguments
                origin = get_origin(attr_type)
                args = get_args(attr_type)

                # Check if the attribute is an Enum and convert the string to Enum
                if hasattr(attr_type, "__members__"):
                    processed_data[attr_name] = attr_type[value]
                # Check if the attribute is a datetime within an Optional
                elif origin == Optional and issubclass(args[0], datetime):
                    processed_data[attr_name] = datetime.fromisoformat(value) if value else None
                # Handle list of dicts (for InputParameters, OutputParameters, ValidationErrors)
                elif origin == Optional and issubclass(args[0], List) and args[0].__args__[0] == dict:
                    processed_data[attr_name] = value if isinstance(value, list) else [value] if value else None
                # Assign all other types directly
                else:
                    processed_data[attr_name] = value

        # Create an instance of the class with the processed data
        return cls(**processed_data)
    
    # def to_dict(self):
    #     return {attr_name: getattr(self, attr_name) for attr_name in self.__annotations__ if getattr(self, attr_name) is not None}
    def to_dict(self):
        return {attr_name[0].lower() + attr_name[1:]: getattr(self, attr_name) for attr_name in self.__annotations__ if getattr(self, attr_name) is not None}