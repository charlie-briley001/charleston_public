
class AnalyticsError(Exception):
    """Base exception for all analytical errors."""


class ParamValidationError(AnalyticsError):
    """Raised when data types for analytics functions or objects are incorrect.
    """
    def __init__(self, message):
        super().__init__(message)

class SeriesValidationError(AnalyticsError):
    """Raised when series variable is used incorrectly
    """
    def __init__(self, message):
        super().__init__(message)

class LookbackError(AnalyticsError):
    """Raised when lookback value is not possible
    """
    def __init__(self, message):
        super().__init__(message)