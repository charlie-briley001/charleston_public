
"""
function that takes individual series or a dataframe
--> df w/ names
or
--> just two series

and --> lookback calc for hedging ratio

--> should this be a class for proper validation?

--> need to implement hedging ratio funcs:
 --> simple divison then sum
 -->  then OLS for more protection against volatility
 --> make sure it's a pd Series so we can calculate it as a spread eventually

 --> then need to calculate spread = stock1 * (ratio * stock2)


"""

from src.fin_data.data_connector import FinDataApi
from src.fin_data.data_connector.object_models import TimeData
from src.fin_data.utils.stats_utils import StatsUtils
import pandas as pd
from typing import Optional, Union
import statsmodels.api as sm

class PairsTradingAnalysis:

    def __init__(self, **kwargs):
        self._prices: Optional[pd.DataFrame] = kwargs.get('prices_df')
        self._series_1: Union[str, pd.Series] = kwargs.get('series_1')
        self._series_2: Union[str, pd.Series] = kwargs.get('series_2')
        self._lookback: int = kwargs.get('lookback')
        self._hedging_method: str = kwargs.get('hedging_method', 'complex')
        self._observations: int = 0
        self._hedging_ratios: Union[pd.DataFrame, pd.Series] = pd.DataFrame([])
        self._spread_df: pd.Series = pd.Series([])

        self._hedging_methods = {
            "simple": self._simple_ratio,
            "complex": self._complex_ratio
        }

        self.post_init()

    def _validate_series_name(self) -> None:
        for ticker in [self._series_1, self._series_2]:
            if not isinstance(ticker, str):
                raise ValueError(
                    'Series 1 and 2 must be str values of tickers, when prices df is passed'
                )
            if ticker not in self._prices.columns:
                raise ValueError(
                    'Ticker must be a column of the prices df'
                )

    def _prep_prices_df(self) -> None:
        _pre_drop_len: int= len(self._prices)
        self._prices: pd.DataFrame = self._prices.dropna()
        self._observations: int = len(self._prices)
        print(f'{_pre_drop_len - self._observations} were dropped due to nan values')

    def post_init(self):
        if self._prices is not None:
            if not isinstance(self._prices, pd.DataFrame):
                raise ValueError('Prices Df must be a pandas dataframe')
            self._validate_series_name()
            self._prep_prices_df()

        elif self._prices is None:
            for series_n in [self._series_1, self._series_2]:
                if not isinstance(series_n, pd.Series):
                    raise ValueError('Series 1 and 2 must both be pandas series')
            self._prices = pd.concat(
                [self._series_1, self._series_2],
                axis=1)
            self._prep_prices_df()

        if self._lookback:
            if self._lookback >= self._observations:
                raise ValueError('Lookback cannot be same length or greater than number of observations')
        elif self._lookback is None:
            self._lookback: int = round(self._observations * .2)

        if self._hedging_method not in list(self._hedging_methods.keys()):
            raise ValueError(
                f'Hedging method must be {list(self._hedging_methods.keys())}'
            )

    def _simple_ratio(self) -> pd.DataFrame:
        self._hedging_ratios: pd.DataFrame = (
            (self._prices[self._series_1] / self._prices[self._series_2])
            .rolling(self._lookback).mean()
        )
        self._hedging_ratios.dropna()
        return self._hedging_ratios

    def _complex_ratio(self) -> pd.Series:
        """Complex ratio calc"""
        self._hedging_ratios: pd.Series = pd.Series([])
        for i in range(self._lookback, len(self._prices)):
            _series_1 = self._prices[self._series_1].iloc[i - self._lookback:i]
            _series_2 = self._prices[self._series_2].iloc[i - self._lookback:i]
            model = sm.OLS(_series_1, _series_2).fit()
            self._hedging_ratios = pd.concat(
                [self._hedging_ratios,
                 pd.Series(
                     data=[model.params[self._series_2]],
                     index=[self._prices.index[i]]
                 )
                 ],
                axis=0)

        return self._hedging_ratios

    def hedging_ratio(self):
        """Run proper hedging method"""
        self._hedging_methods[self._hedging_method]()

    def _calc_spread(self):
        self._spread_df: pd.DataFrame = (
                self._prices[self._series_1][self._lookback:]
                - self._hedging_ratios * self._prices[self._series_2][self._lookback:]
        )
