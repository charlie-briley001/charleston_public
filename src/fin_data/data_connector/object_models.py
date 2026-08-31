from typing import Optional, Union

import yfinance as yf
from pydantic import BaseModel


class TickerObj(BaseModel):
    ticker: str
    industry_key: Optional[str] = None
    sector_key: Optional[str] = None
    asset_type: Optional[str] = None
    display_name: Optional[str] = None
    meta: Optional[dict] = None

    def model_post_init(self, __context):
        try:
            self.meta = yf.Ticker(self.ticker).info
            self.industry_key = self.meta.get('industryKey')
            self.sector_key =  self.meta.get('sectorKey')
            self.asset_type = self.meta.get('quoteType')
            self.display_name = self.meta.get('displayName')
        except Exception as e:
            raise ValueError(f'THe api to yf didnt work.. please respond - {e}')


class PairsFoundation(BaseModel):
    """Pydantic class that will validate two ticker objects are valid together"""
    ticker_1: Union[TickerObj, str]
    ticker_2: Union[TickerObj, str]

    def model_post_init(self, __context):
        for ticker, symbol in self.__dict__.items():
            if not isinstance(symbol, TickerObj):
                setattr(self, ticker, TickerObj(ticker = symbol))

        if self.ticker_1.asset_type != self.ticker_2.asset_type:
            raise ValueError
