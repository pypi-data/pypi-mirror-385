from abc import ABC, abstractmethod
from ..parameter_validation_result import ParameterValidationResult

class Parameter:
    def __init__(self, value=None, value_type=None):
        self.value = value
        self.value_type = value_type

class ParameterValidationRuleBase(ABC):
    @property
    @abstractmethod
    def kind(self):
        pass

    @kind.setter
    @abstractmethod
    def kind(self, value):
        pass

    def validate(self, param):
        if param is None:
            raise ValueError("param cannot be None")
        return ParameterValidationResult.valid()

# Usage example for a derived class
class SampleValidationRule(ParameterValidationRuleBase):
    def __init__(self):
        self._kind = "sample"

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        self._kind = value

    def validate(self, param):
        # Implement specific validation logic here
        super().validate(param)
        return ParameterValidationResult.valid()
