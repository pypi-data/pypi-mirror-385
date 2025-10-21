import json
from typing import List, Type, Any
from dataclasses import dataclass, field
import importlib

from biosero.datamodels.parameters.validation.rules import *
# from ..validation.rules.parameter_validation_result import ParameterValidationResult
# from ..validation.rules.empty_parameter_validation_rule import EmptyParameterValidationRule
# from ..validation.rules.max_length_parameter_validation_rule import MaxLengthParameterValidationRule
# from ..validation.rules.regex_parameter_validation_rule import RegexParameterValidationRule
# from ..validation.rules.range_parameter_validation_rule import RangeParameterValidationRule
# from ..validation.rules.constraint_to_options_parameter_validation_rule import ConstraintToOptionsParameterValidationRule
# from ..validation.rules.parameter_validation_rule_base import ParameterValidationRuleBase

from biosero.datamodels.extensions import string_extensions


class JsonParameterValidationRuleConverter:
    @staticmethod
    def can_write() -> bool:
        return True

    @staticmethod
    def can_read() -> bool:
        return True

    @staticmethod
    def can_convert(object_type: Type) -> bool:
        return issubclass(object_type, ParameterValidationRuleBase)

    @staticmethod
    def read_json(json_data: str, object_type: Type, existing_value: Any, serializer: Any) -> List[ParameterValidationRuleBase]:
        json_objects = json.loads(json_data)
        validation_rules = []

        for json_object in json_objects:
            kind = json_object.get('kind', 'empty')
            try:
                type_name = f"{kind.capitalize()}ParameterValidationRule"
                # Assuming all validation rules are in the same module as above
                module = importlib.import_module('biosero_data_models_parameters_validation_rules')
                validation_rule_class = getattr(module, type_name)
                validation_rule = validation_rule_class()
                serializer.populate(json_object, validation_rule)
                validation_rules.append(validation_rule)
            except Exception as e:
                print(f"Failed to deserialize {json_object}: {e}")

        return validation_rules

    @staticmethod
    def write_json(writer: Any, value: Any, serializer: Any) -> None:
        serializer.serialize(writer, value)

class CustomSerializer:
    @staticmethod
    def populate(json_object: dict, obj: Any) -> None:
        for key, value in json_object.items():
            setattr(obj, key, value)

    @staticmethod
    def serialize(writer: Any, value: Any) -> None:
        json.dump(value, writer)
