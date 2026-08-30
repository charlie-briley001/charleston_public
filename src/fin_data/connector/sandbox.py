from typing import Optional, Union

import yfinance as yf
from pydantic import BaseModel


# I want a function that will take two tickers, load specific information that I set from pydantic model.
## set that the two securities are of the same asset class....

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

    ## need to check that both are of the same class

class FinDataApi:

    def __init(self, ticker_1: str, ticker_2: str):
        """Initial function to load the tickers and validate as needed"""
        self._ticker_1 = ticker_1
        self._ticker_2 = ticker_2


if __name__ == '__main__':
    tt = PairsFoundation(ticker_1 = '', ticker_2 = '')
    print('hi')