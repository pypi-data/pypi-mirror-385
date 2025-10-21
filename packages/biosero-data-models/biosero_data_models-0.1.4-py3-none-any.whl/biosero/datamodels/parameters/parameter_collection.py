import json
from typing import List, Type, TypeVar, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import UserList
from biosero.datamodels.parameters import Parameter
from biosero.datamodels.parameters.converters import JsonParameterValueTypeConverter, JsonParameterValidationRuleConverter

T = TypeVar('T')

class ParameterCollection(UserList):

    def to_dict(self):
        return [param.to_dict() if hasattr(param, 'to_dict') else param for param in self]

    def clone(self) -> 'ParameterCollection':
        return ParameterCollection(json.loads(json.dumps(self.data, default=lambda o: asdict(o))))

    def get_value(self, parameter_name: str, type_: Type[T]) -> T:
        parameter = next((p for p in self if p.name == parameter_name), None)
        if parameter is None:
            raise ValueError(f"Could not find parameter named {parameter_name}")
        
        if type_ == str:
            return type_(parameter.value)
        elif type_ == int:
            return type_(int(parameter.value))
        elif type_ == float:
            return type_(float(parameter.value))
        elif type_ == bool:
            return type_(parameter.value.lower() in ['true', '1'])
        else:
            raise ValueError("Invalid Type")

    def get_or_default_value(self, parameter_name: str, default_value: Optional[T] = None) -> T:
        parameter = next((p for p in self if p.name == parameter_name), None)
        if parameter is None:
            self.set_value(parameter_name, default_value)
            parameter = next((p for p in self if p.name == parameter_name), None)
        
        return self.get_value(parameter_name, type(default_value))

    def get(self, name: str) -> Optional[Parameter]:
        return next((p for p in self if p.name == name), None)

    def try_get_value(self, parameter_name: str, type_: Type[T]) -> Optional[T]:
        parameter = next((p for p in self if p.name == parameter_name), None)
        if parameter is None:
            return None
        return self.get_value(parameter_name, type_)

    def set_value(self, parameter_name: str, value: Any) -> None:
        parameter = next((p for p in self if p.name == parameter_name), None)
        if parameter is None:
            self.append(Parameter(name=parameter_name, value=str(value)))
        else:
            parameter.value = str(value)
 