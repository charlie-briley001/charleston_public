"""
Data classes / models for the fin_data connector package.

Defines the core Pydantic and dataclass models used to represent tickers,
time parameters, and validated ticker pairs consumed by :class:`FinDataApi`.
"""

from dataclasses import dataclass
from typing import Optional, Union

import yfinance as yf
from pydantic import BaseModel

from src.fin_data.exceptions.exceptions_data_connector import AssetClassError, TimeParametersError
from src.fin_data.utils.utils import ticker_data_errors


@dataclass
class TimeData:
    """Container for the time-range and frequency parameters passed to yfinance historical downloads.

    Attributes:
        start_date (str): Start of the historical window in ``YYYY-MM-DD`` format.
        end_date (str): End of the historical window in ``YYYY-MM-DD`` format.
        interval (str): Data frequency accepted by yfinance (e.g. ``"1d"``, ``"1wk"``).
    """
    start_date: str
    end_date: str
    interval: str

    #below validation should be enhanced further
    def __post_init__(self):
        if not self.end_date or not self.start_date or not self.interval:
            raise TimeParametersError("Start & End Date, and Interval must all be passed")
        if (not isinstance(self.end_date, str)
                or not isinstance(self.end_date, str)
                or not isinstance(self.interval, str)):
            raise TimeParametersError("Start & End Date, and Interval must all be strings")


class TickerObj(BaseModel):
    """Pydantic model representing a single financial instrument.

    On instantiation, fetches metadata from the yfinance API and populates
    ``industry_key``, ``sector_key``, ``asset_type``, and ``display_name``
    automatically.

    Attributes:
        ticker (str): The exchange ticker symbol (e.g. ``"AAPL"``).
        industry_key (str, optional): yfinance ``industryKey`` value.
        sector_key (str, optional): yfinance ``sectorKey`` value.
        asset_type (str, optional): yfinance ``quoteType`` (e.g. ``"EQUITY"``).
        display_name (str, optional): Human-readable name from yfinance.
        meta (dict, optional): Full ``yf.Ticker.info`` payload.

    Raises:
        TickerCreationDataError: If the yfinance API call fails or the ticker
            cannot be resolved.
    """

    ticker: str
    industry_key: Optional[str] = None
    sector_key: Optional[str] = None
    asset_type: Optional[str] = None
    display_name: Optional[str] = None
    meta: Optional[dict] = None

    @ticker_data_errors
    def model_post_init(self, __context) -> None:
        """Populate metadata fields by querying the yfinance API.

        Called automatically by Pydantic after ``__init__``.
        """
        self.meta = yf.Ticker(self.ticker).info
        self.industry_key = self.meta.get('industryKey')
        self.sector_key =  self.meta.get('sectorKey')
        self.asset_type = self.meta.get('quoteType')
        self.display_name = self.meta.get('displayName')


class PairsFoundation(BaseModel):
    """Pydantic base model that validates two tickers belong to the same asset class.

    Accepts either pre-built :class:`TickerObj` instances or raw ticker strings;
    raw strings are automatically promoted to :class:`TickerObj` during
    post-init validation.

    Attributes:
        ticker_1 (TickerObj | str): First ticker in the pair.
        ticker_2 (TickerObj | str): Second ticker in the pair.

    Raises:
        AssetClassError: If ``ticker_1`` and ``ticker_2`` have different
            ``asset_type`` values (e.g. an equity paired with a fixed income).
    """

    ticker_1: Union[TickerObj, str]
    ticker_2: Union[TickerObj, str]

    def model_post_init(self, __context) -> None:
        """Coerce string tickers to :class:`TickerObj` and enforce asset-class parity.

        Raises:
            AssetClassError: If the two tickers are of different asset types.
        """
        for ticker, symbol in self.__dict__.items():
            if not isinstance(symbol, TickerObj):
                setattr(self, ticker, TickerObj(ticker = symbol))

        if self.ticker_1.asset_type != self.ticker_2.asset_type:
            raise AssetClassError()