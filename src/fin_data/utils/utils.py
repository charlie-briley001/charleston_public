import functools

from src.fin_data.exceptions.exceptions_data_connector import TickerCreationDataError


def ticker_data_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raise TickerCreationDataError
    return wrapper