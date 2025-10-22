class ExceptionExtensions:
    @staticmethod
    def log_exception(exception: Exception, logger=None):
        """
        Example method to log the exception.
        """
        if logger:
            logger.error(f"Exception occurred: {str(exception)}")
        else:
            print(f"Exception occurred: {str(exception)}")

    @staticmethod
    def to_string(exception: Exception) -> str:
        """
        Example method to get the string representation of the exception.
        """
        return str(exception)

