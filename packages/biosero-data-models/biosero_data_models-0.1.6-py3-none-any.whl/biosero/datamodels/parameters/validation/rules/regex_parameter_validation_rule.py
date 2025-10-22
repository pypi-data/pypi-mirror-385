import re
from ..parameter_validation_result import ParameterValidationResult

class MissingMemberException(Exception):
    pass

class ParameterValidationRuleBase:
    def validate(self, param):
        if param is None:
            raise ValueError("param cannot be None")
        return ParameterValidationResult.valid()

class Parameter:
    def __init__(self, value=None, value_type=None):
        self.value = value
        self.value_type = value_type

class RegexParameterValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        self.kind = "regex"
        self.pattern_to_match = ""

    def validate(self, param):
        super().validate(param)

        if param.value is None:
            raise MissingMemberException("Value")

        if not self.pattern_to_match:
            raise MissingMemberException("PatternToMatch")

        if not re.match(self.pattern_to_match, param.value):
            return ParameterValidationResult(is_valid=False, error_message="Value doesn't match.")

        return ParameterValidationResult.valid()
