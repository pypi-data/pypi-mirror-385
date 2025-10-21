class ParameterValidationRuleBase:
    def __init__(self):
        self.kind = None

    def validate(self, param):
        pass


class ConstraintToOptionsParameterValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        super().__init__()
        self.kind = "options"

    def validate(self, param):
        super().validate(param)

        if param.value is None:
            raise AttributeError("Value")

        if param.value_options is None:
            raise AttributeError("ValueOptions")

        if param.value not in param.value_options:
            return ParameterValidationResult(False, "Value doesn't contain in ValueOptions.")

        return ParameterValidationResult.Valid