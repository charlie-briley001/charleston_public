"""
Primary API interface for the fin_data connector package.

Exposes :class:`FinDataApi`, the main entry point for downloading historical
price data for a ticker pair via the yfinance library.
"""

import pandas as pd
import yfinance as yf

from src.pairs_trading.data_connector.object_models import PairsFoundation, TimeData
from src.pairs_trading.utils.utils import ticker_data_errors


class FinDataApi(PairsFoundation):
    """API class for downloading historical data for a ticker pair.

    Inherits from :class:`PairsFoundation`, which validates that both tickers
    exist and belong to the same asset class before any data is fetched.

    Example:
        ::

            api = FinDataApi(ticker_1="AAPL", ticker_2="MSFT")
            data = api.pull_hist(TimeData(start_date="2023-01-01",
                                          end_date="2024-01-01",
                                          interval="1d"))
    """

    @ticker_data_errors
    def pull_hist(self, date_params: TimeData) -> pd.DataFrame:
        """Download historical data for both tickers in the pair.

        Uses :func:`yfinance.download` with ``group_by="ticker"`` so the
        returned DataFrame has a two-level column index
        ``(ticker, price_field)``.

        Args:
            date_params (TimeData): Time-range and interval configuration.

        Returns:
            pd.DataFrame: Multi-level column DataFrame with data for
            both tickers over the requested period.

        Raises:
            TickerCreationDataError: If the yfinance download fails for any reason.
        """
        hist_data = yf.download(
            tickers = [self.ticker_1.ticker, self.ticker_2.ticker],
            start = date_params.start_date,
            end = date_params.end_date,
            interval = date_params.interval,
            group_by = "ticker"
        )
        return hist_data
