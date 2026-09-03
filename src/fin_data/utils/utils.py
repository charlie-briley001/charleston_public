"""
Shared utility decorators for the fin_data connector package.
"""

import functools

from src.fin_data.exceptions.exceptions_data_connector import TickerCreationDataError


def ticker_data_errors(func):
    """Decorator that converts any unhandled exception into a :class:`TickerCreationDataError`.

    Wraps yfinance API calls and Pydantic post-init hooks so that callers
    receive a consistent exception type regardless of the underlying failure
    (network error, invalid ticker, unexpected API response, etc.).

    Args:
        func (Callable): The function or method to wrap.

    Returns:
        Callable: Wrapped function that raises :class:`TickerCreationDataError`
        on any exception.

    Raises:
        TickerCreationDataError: On any exception raised by the wrapped function.

    Example:
        ::

            @ticker_data_errors
            def fetch_something():
                return yf.Ticker("INVALID").info
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise TickerCreationDataError
    return wrapper