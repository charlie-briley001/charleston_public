from typing import Optional, Union

import yfinance as yf
from pydantic import BaseModel
from src.fin_data.data_connector.object_models import PairsFoundation

class FinDataApi(PairsFoundation):

    def __init(self, ticker_1: str, ticker_2: str):
        """Initial function to load the tickers and validate as needed"""
        self.ticker_1 = ticker_1
        self.ticker_2 = ticker_2

    def pull_hist(self, start_date: str, end_date: str, inter: str = '1d'):
        ## put in param validation prior to as a decorator or data class
        hist_data = yf.download(
            tickers = [self.ticker_1.ticker, self.ticker_2.ticker],
            start = start_date,
            end = end_date,
            interval = inter,
            group_by = "ticker"
        )

        return hist_data
