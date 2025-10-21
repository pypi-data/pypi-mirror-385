class ParameterValidationResult:
    def __init__(self, is_valid=True, error_message=''):
        self.is_valid = is_valid
        self.error_message = error_message

    @staticmethod
    def invalid():
        return ParameterValidationResult(is_valid=False, error_message='')

    @staticmethod
    def valid():
        return ParameterValidationResult(is_valid=True, error_message='')


# Usage
invalid_result = ParameterValidationResult.invalid()
valid_result = ParameterValidationResult.valid()
