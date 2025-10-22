import json
from typing import List, Any
from dataclasses import dataclass, field

from biosero.datamodels.view_model import ViewModel
from biosero.datamodels.parameters.validation.rules import ParameterValidationRuleBase

class CustomSerializer:
    @staticmethod
    def populate(json_object: dict, obj: Any) -> None:
        for key, value in json_object.items():
            setattr(obj, key, value)

    @staticmethod
    def serialize(writer: Any, value: Any) -> None:
        json.dump(value, writer)

class Parameter(ViewModel):
    def __init__(self, name: str = "", value: str = "", valueType=None, unit: str = "", defaultValue: str = "", valueOptions: List[str] = None,
                 validationRules: List[ParameterValidationRuleBase] = None, tags: List[str] = None, identity: str = "", description: str = ""):
        from biosero.datamodels.parameters.parameter_value_type import ParameterValueType

        self.name = name
        self.value = value
        self.valueType = valueType if valueType else ParameterValueType.OTHER
        self.unit = unit
        self.defaultValue = defaultValue
        self.valueOptions = valueOptions if valueOptions else []
        self.validationRules = validationRules if validationRules else []
        self.tags = tags if tags else []
        self.identity = identity
        self.description = description

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, val: str):
        if not isinstance(val, str):
            raise TypeError(f"Parameter.value must be a string, got {type(val).__name__}")
        self.set_field("_value", val)

    def is_valid(self) -> bool:
        return all(vr.validate(self).is_valid for vr in self.validation_rules)

    def get_validation_error_message(self) -> str:
        return ", ".join(vr.validate(self).error_message for vr in self.validation_rules if not vr.validate(self).is_valid)

    def set_field(self, field_name: str, value: str):
        setattr(self, field_name, value)

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def to_dict(self) -> dict:
        from biosero.datamodels.parameters.parameter_value_type import ParameterValueType
        return {k: (v.value if isinstance(v, ParameterValueType) else v)
                for k, v in {
                    "name": self.name,
                    "value": self.value,
                    "valueType": self.valueType.value,
                    "unit": self.unit,
                    "defaultValue": self.defaultValue,
                    "valueOptions": self.valueOptions,
                    "validationRules": [vr.to_dict() for vr in self.validationRules] if self.validationRules else [],
                    "tags": self.tags,
                    "identity": self.identity,
                    "description": self.description,
                }.items() if v is not None}

    @staticmethod
    def from_json(json_str: str):
        from biosero.datamodels.parameters.converters import JsonParameterValueTypeConverter, JsonParameterValidationRuleConverter
        from biosero.datamodels.parameters.validation.rules import ParameterValidationRuleBase

        data = json.loads(json_str)
        valueType = JsonParameterValueTypeConverter.read_json(json.dumps(data['valueType']))
        validationRules = JsonParameterValidationRuleConverter.read_json(json.dumps(data['validationRules']), ParameterValidationRuleBase, None, CustomSerializer)
        return Parameter(
            name=data['name'],
            value=data['value'],
            valueType=valueType,
            unit=data['unit'],
            defaultValue=data['defaultValue'],
            valueOptions=data['valueOptions'],
            validationRules=validationRules,
            tags=data['tags'],
            identity=data['identity'],
            description=data['description']
        )
