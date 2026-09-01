"""
Exceptions for data connector package
"""

class FinDataExtractError(Exception):
    pass


class TickerCreationDataError(FinDataExtractError):
    """
    """
    def __init__(self):
        message = "Ticker / symbol could not be properly loaded"
        super().__init__(message)

class AssetClassError(FinDataExtractError):
    """
    """
    def __init__(self):
        message = "Both securities must be of the same asset class"
        super().__init__(message)