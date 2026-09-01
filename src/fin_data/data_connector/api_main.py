import pandas as pd
import yfinance as yf

from src.fin_data.data_connector.object_models import PairsFoundation, TimeData
from src.fin_data.utils.utils import ticker_data_errors


class FinDataApi(PairsFoundation):

    def __init(self, ticker_1: str, ticker_2: str) -> None:
        """Initial function to load the tickers and validate as needed"""
        self.ticker_1 = ticker_1
        self.ticker_2 = ticker_2

    @ticker_data_errors
    def pull_hist(self, date_params: TimeData) -> pd.DataFrame:
        """"""
        hist_data = yf.download(
            tickers = [self.ticker_1.ticker, self.ticker_2.ticker],
            start = date_params.start_date,
            end = date_params.end_date,
            interval = date_params.interval,
            group_by = "ticker"
        )
        return hist_data
