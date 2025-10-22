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


class EmptyParameterValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        self.kind = None

    def validate(self, param):
        raise NotImplementedError("Validate method is not implemented yet")

