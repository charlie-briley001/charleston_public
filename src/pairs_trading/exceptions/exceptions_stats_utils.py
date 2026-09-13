
class StatsUtilityError(Exception):
    """Base exception for all stats utils errors."""


class StatsUtilsDataTypeError(StatsUtilityError):
    """Raised when data types for a stats utils function are incorrect.
    """
    def __init__(self, message):
        super().__init__(message)
