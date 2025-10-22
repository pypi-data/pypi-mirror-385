from ..parameter_validation_result import ParameterValidationResult

class MissingMemberException(Exception):
    pass

class ParameterValidationRuleBase:
    def validate(self, param):
        # Base validation logic if any
        pass

class Parameter:
    def __init__(self, value=None, value_options=None):
        self.value = value
        self.value_options = value_options

class MaxLengthParameterValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        self.kind = "maxLength"
        self.minimum_length = 0
        self.maximum_length = float('inf')

    def validate(self, param):
        super().validate(param)

        if param.value is None:
            raise MissingMemberException("Value")

        length = len(param.value)

        if length < self.minimum_length or length > self.maximum_length:
            return ParameterValidationResult(
                is_valid=False,
                error_message=f"Value must be between {self.minimum_length} and {self.maximum_length} characters long."
            )

        return ParameterValidationResult.valid()
