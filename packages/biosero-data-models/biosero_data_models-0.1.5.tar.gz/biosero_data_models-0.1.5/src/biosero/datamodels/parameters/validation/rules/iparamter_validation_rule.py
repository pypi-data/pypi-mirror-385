from abc import ABC, abstractmethod
from ..parameter_validation_result import ParameterValidationResult


class Parameter:
    def __init__(self, value=None, value_options=None):
        self.value = value
        self.value_options = value_options


class IParameterValidationRule(ABC):
    @property
    @abstractmethod
    def kind(self):
        pass

    @kind.setter
    @abstractmethod
    def kind(self, value):
        pass

    @abstractmethod
    def validate(self, param: Parameter) -> ParameterValidationResult:
        pass
