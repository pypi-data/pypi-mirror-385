from ..parameter_validation_result import ParameterValidationResult

class ParameterValueType:
    Double = "double"
    Other = "other"

class MissingMemberException(Exception):
    pass

class ParameterValidationRuleBase:
    def validate(self, param):
        # Base validation logic if any
        pass

class Parameter:
    def __init__(self, value=None, value_type=None):
        self.value = value
        self.value_type = value_type

class RangeParameterValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        self.kind = "range"
        self.minimum_value = None
        self.maximum_value = None

    def validate(self, param):
        super().validate(param)

        if param.value is None:
            raise MissingMemberException("Value")

        type_ = int

        if param.value_type == ParameterValueType.Double:
            type_ = float
        elif param.value_type == ParameterValueType.Other:
            raise NotSupportedException("ValueType")

        value = type_(param.value)
        minimum_value = type_(self.minimum_value)
        maximum_value = type_(self.maximum_value)

        result = ParameterValidationResult()

        value_is_greater_than_equal_to_minimum_value = self.is_x_less_than_or_equal_to_y(minimum_value, value)
        value_is_less_than_equal_to_maximum_value = self.is_x_less_than_or_equal_to_y(value, maximum_value)

        result.is_valid = value_is_greater_than_equal_to_minimum_value and value_is_less_than_equal_to_maximum_value
        result.error_message = None if result.is_valid else "Value is out of range."

        return result

    @staticmethod
    def is_x_less_than_or_equal_to_y(x, y):
        return x <= y

