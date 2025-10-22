import json
from enum import Enum
from typing import Type

class ParameterValueType(Enum):
    BOOLEAN = "boolean"
    DOUBLE = "double"
    INTEGER = "integer"
    STRING = "string"
    OTHER = "other"

class JsonParameterValueTypeConverter:
    @staticmethod
    def can_write() -> bool:
        return True

    @staticmethod
    def can_read() -> bool:
        return True

    @staticmethod
    def can_convert(object_type: Type) -> bool:
        return object_type == ParameterValueType

    @staticmethod
    def read_json(json_data: str) -> ParameterValueType:
        value = json.loads(json_data)
        if value is not None:
            value = value.lower()
            if value == "boolean":
                return ParameterValueType.BOOLEAN
            elif value == "double":
                return ParameterValueType.DOUBLE
            elif value == "integer":
                return ParameterValueType.INTEGER
            elif value == "string":
                return ParameterValueType.STRING
        return ParameterValueType.OTHER

    @staticmethod
    def write_json(value: ParameterValueType) -> str:
        if value == ParameterValueType.OTHER:
            json_value = "Other"
        else:
            json_value = value.value
        return json.dumps(json_value)

