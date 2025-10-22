import enum
from typing import List, Type, TypeVar, Union

T = TypeVar('T', bound=enum.Enum)

class EnumHelper:
    @staticmethod
    def get_description(enum_obj: enum.Enum) -> str:
        """
        Get the description attribute of an enum member if it exists.
        """
        if not isinstance(enum_obj, enum.Enum):
            raise ValueError(f"{enum_obj} is not an instance of Enum")

        description = enum_obj.value
        if hasattr(enum_obj, 'description'):
            description = enum_obj.description
        return description

    @staticmethod
    def get_values(enum_type: Type[T]) -> List[T]:
        """
        Get all values of an enum type.
        """
        if not issubclass(enum_type, enum.Enum):
            raise ValueError(f"Type '{enum_type.__name__}' is not an enum")
        
        return list(enum_type)

    @staticmethod
    def get_values_as_objects(enum_type: Type[enum.Enum]) -> List[object]:
        """
        Get all values of an enum type as objects.
        """
        if not issubclass(enum_type, enum.Enum):
            raise ValueError(f"Type '{enum_type.__name__}' is not an enum")
        
        return [member.value for member in enum_type]

