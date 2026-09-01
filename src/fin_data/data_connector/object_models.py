from dataclasses import dataclass
from typing import Optional, Union

import yfinance as yf
from pydantic import BaseModel

from src.fin_data.exceptions.exceptions_data_connector import AssetClassError
from src.fin_data.utils.utils import ticker_data_errors


@dataclass
class TimeData:
    start_date: str
    end_date: str
    interval: str


class TickerObj(BaseModel):
    ticker: str
    industry_key: Optional[str] = None
    sector_key: Optional[str] = None
    asset_type: Optional[str] = None
    display_name: Optional[str] = None
    meta: Optional[dict] = None

    @ticker_data_errors
    def model_post_init(self, __context) -> None:
        """"""
        self.meta = yf.Ticker(self.ticker).info
        self.industry_key = self.meta.get('industryKey')
        self.sector_key =  self.meta.get('sectorKey')
        self.asset_type = self.meta.get('quoteType')
        self.display_name = self.meta.get('displayName')


class PairsFoundation(BaseModel):
    """Pydantic class that will validate two ticker objects are valid together"""
    ticker_1: Union[TickerObj, str]
    ticker_2: Union[TickerObj, str]

    def model_post_init(self, __context) -> AssetClassError | None:
        for ticker, symbol in self.__dict__.items():
            if not isinstance(symbol, TickerObj):
                setattr(self, ticker, TickerObj(ticker = symbol))

        if self.ticker_1.asset_type != self.ticker_2.asset_type:
            raise AssetClassError