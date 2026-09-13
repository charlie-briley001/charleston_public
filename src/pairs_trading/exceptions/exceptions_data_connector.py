"""
Custom exceptions for the fin_data connector package.

All exceptions inherit from :class:`FinDataExtractError` so callers can catch
the entire family with a single ``except FinDataExtractError`` clause.
"""


class FinDataExtractError(Exception):
    """Base exception for all fin_data extraction errors."""


class TimeParametersError(FinDataExtractError):
    """Raised when a date parameters passed for data extract are not valid

    Typically a result of invalid param type or missing params.
    """

    def __init__(self, message):
        super().__init__(message)


class TickerCreationDataError(FinDataExtractError):
    """Raised when a ticker symbol cannot be loaded or resolved via yfinance.

    Typically wraps network failures, invalid symbols, or unexpected API
    response shapes returned by ``yf.Ticker.info``.
    """

    def __init__(self):
        message = "Ticker / symbol could not be properly loaded"
        super().__init__(message)


class AssetClassError(FinDataExtractError):
    """Raised when the two tickers in a pair belong to different asset classes.

    :class:`PairsFoundation` compares the ``asset_type`` field of each
    :class:`TickerObj` and raises this error if they do not match (e.g.
    pairing an equity with fixed income).
    """

    def __init__(self):
        message = "Both securities must be of the same asset class"
        super().__init__(message)