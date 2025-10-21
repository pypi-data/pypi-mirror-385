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


class ConstraintToOptionsParameterValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        self.kind = "options"

    def validate(self, param):
        super().validate(param)

        if param.value is None:
            raise MissingMemberException("Value")

        if param.value_options is None:
            raise MissingMemberException("ValueOptions")

        if param.value not in param.value_options:
            return ParameterValidationResult(is_valid=False, error_message="Value doesn't contain in ValueOptions.")

        return ParameterValidationResult.valid()

