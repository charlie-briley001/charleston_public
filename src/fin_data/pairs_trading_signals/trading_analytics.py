"""
Pairs trading analytics module for calculating hedging ratios, spreads, and z-scores.

Accepts either a prices DataFrame (with ticker column names) or two individual
``pd.Series`` objects. Supports simple (rolling mean ratio) and complex
(rolling OLS regression) hedging ratio methods.
"""

from dataclasses import dataclass
from typing import Optional, Union

import pandas as pd
import statsmodels.api as sm

from src.fin_data.exceptions.exceptions_trading_analytics import (
    LookbackError,
    ParamValidationError,
    SeriesValidationError,
)


@dataclass
class SpreadCalcResult:
    """Container for spread calculation output metrics.

    :param mean: Rolling mean of the spread series.
    :type mean: pd.Series
    :param std_dev: Rolling standard deviation of the spread series.
    :type std_dev: pd.Series
    :param z_score: Rolling z-score of the spread relative to its mean and std dev.
    :type z_score: pd.Series
    """

    mean: pd.Series
    std_dev: pd.Series
    z_score: pd.Series


class PairsTradingAnalysis:
    """Computes pairs trading signals for a given pair of price series.

    Accepts either a combined prices DataFrame or two separate ``pd.Series``
    objects. Calculates a rolling hedging ratio (simple or OLS-based), derives
    the price spread, and returns rolling mean, standard deviation, and z-score
    metrics used to generate trading signals.

    Example usage::

        analysis = PairsTradingAnalysis(
            prices_df=df,
            series_1='AAPL',
            series_2='MSFT',
            lookback=60,
            hedging_method='complex',
        )
        result = analysis.fetch_analytics()
    """

    def __init__(self, **kwargs):
        """Initialise the analysis object and run post-init validation.

        :param prices_df: DataFrame of price series with ticker symbols as column names.
            Mutually exclusive with passing raw ``pd.Series`` objects.
        :type prices_df: pd.DataFrame, optional
        :param series_1: Either a ticker string (when ``prices_df`` is supplied) or a
            ``pd.Series`` of prices for the first instrument.
        :type series_1: str or pd.Series
        :param series_2: Either a ticker string (when ``prices_df`` is supplied) or a
            ``pd.Series`` of prices for the second instrument.
        :type series_2: str or pd.Series
        :param lookback: Rolling window size in periods. Defaults to 20 % of the
            available observations when not provided.
        :type lookback: int, optional
        :param hedging_method: Hedging ratio method to use. One of ``'simple'``
            (rolling mean of price ratio) or ``'complex'`` (rolling OLS regression).
            Defaults to ``'complex'``.
        :type hedging_method: str, optional
        :raises ParamValidationError: If ``prices_df`` is not a ``pd.DataFrame``, or if
            raw series inputs are not ``pd.Series`` objects.
        :raises SeriesValidationError: If ticker strings are not present as columns in
            ``prices_df``.
        :raises LookbackError: If ``lookback`` is greater than or equal to the number
            of available observations.
        """
        self._prices: Optional[pd.DataFrame] = kwargs.get('prices_df')
        self._series_1: Union[str, pd.Series] = kwargs.get('series_1')
        self._series_2: Union[str, pd.Series] = kwargs.get('series_2')
        self._lookback: int = kwargs.get('lookback')
        self._hedging_method: str = kwargs.get('hedging_method', 'complex')
        self._observations: int = 0
        self._hedging_ratios: Union[pd.DataFrame, pd.Series] = pd.DataFrame([])
        self._spread_df: pd.Series = pd.Series([])
        self._spread_metrics: SpreadCalcResult = SpreadCalcResult(
            mean=pd.Series([]),
            std_dev=pd.Series([]),
            z_score=pd.Series([]),
        )

        self._hedging_methods = {
            "simple": self._simple_ratio,
            "complex": self._complex_ratio
        }

        self.post_init()

    def _validate_series_name(self) -> None:
        """Verify that both series identifiers are strings present in ``_prices``.

        :raises SeriesValidationError: If either identifier is not a string, or if
            either ticker is not a column in ``_prices``.
        """
        for ticker in [self._series_1, self._series_2]:
            if not isinstance(ticker, str):
                raise SeriesValidationError(
                    'Series 1 and 2 must be str values of tickers, when prices df is passed'
                )
            if ticker not in self._prices.columns:
                raise SeriesValidationError(
                    'Ticker must be a column of the prices df'
                )

    def _prep_prices_df(self) -> None:
        """Drop rows containing nan values and record the observation count.

        Prints the number of rows dropped to stdout.
        """
        _pre_drop_len: int = len(self._prices)
        self._prices: pd.DataFrame = self._prices.dropna()
        self._observations: int = len(self._prices)
        print(f'{_pre_drop_len - self._observations} were dropped due to nan values')

    def post_init(self) -> None:
        """Validate all constructor inputs and prepare internal state.

        Handles two input modes:

        * **DataFrame mode** — ``prices_df`` is provided; ``series_1`` and
          ``series_2`` must be column name strings.
        * **Series mode** — no ``prices_df``; ``series_1`` and ``series_2``
          must be ``pd.Series`` objects which are concatenated internally.

        Sets ``_lookback`` to 20 % of observations when not supplied, then
        validates the chosen hedging method.

        :raises ParamValidationError: If type constraints on inputs are violated or
            if ``hedging_method`` is not a recognised key.
        :raises SeriesValidationError: If ticker column validation fails.
        :raises LookbackError: If the supplied ``lookback`` is too large.
        """
        if self._prices is not None:
            if not isinstance(self._prices, pd.DataFrame):
                raise ParamValidationError('Prices Df must be a pandas dataframe')
            self._validate_series_name()
            self._prep_prices_df()

        else:
            for series_n in [self._series_1, self._series_2]:
                if not isinstance(series_n, pd.Series):
                    raise ParamValidationError('Series 1 and 2 must both be pandas series')
            self._prices = pd.concat(
                [self._series_1, self._series_2],
                axis=1
            )
            self._series_1: str = self._series_1.name
            self._series_2: str = self._series_2.name
            self._prep_prices_df()

        if self._lookback:
            if self._lookback >= self._observations:
                raise LookbackError(
                    'Lookback cannot be same length or greater than number of observations'
                )
        elif self._lookback is None:
            self._lookback: int = round(self._observations * .2)

        if self._hedging_method not in list(self._hedging_methods.keys()):
            raise ParamValidationError(
                f'Hedging method must be {list(self._hedging_methods.keys())}'
            )

    def _simple_ratio(self) -> pd.DataFrame:
        """Calculate the hedging ratio as a rolling mean of the price ratio.

        Divides ``series_1`` by ``series_2`` on each date, then applies a
        rolling mean of length ``_lookback``. NaN rows (from the initial
        window) are dropped.

        :returns: Rolling mean price ratio indexed to valid dates.
        :rtype: pd.DataFrame
        """
        self._hedging_ratios: pd.DataFrame = (
            (self._prices[self._series_1] / self._prices[self._series_2])
            .rolling(self._lookback).mean()
        ).dropna()

        return self._hedging_ratios

    def _complex_ratio(self) -> pd.Series:
        """Calculate the hedging ratio using rolling OLS regression.

        For each window of length ``_lookback``, fits an OLS model of
        ``series_1`` on ``series_2`` (no intercept) and records the
        estimated coefficient as the hedging ratio for that date.

        :returns: Time-indexed series of OLS-derived hedging ratios.
        :rtype: pd.Series
        """
        _dates = []
        _ratios = []
        for i in range(self._lookback, len(self._prices)):
            _series_1 = self._prices[self._series_1].iloc[i - self._lookback:i]
            _series_2 = self._prices[self._series_2].iloc[i - self._lookback:i]
            model = sm.OLS(_series_1, _series_2).fit()
            _ratios.append(model.params[self._series_2])
            _dates.append(self._prices.index[i])

        self._hedging_ratios = pd.Series(data=_ratios, index=_dates)
        return self._hedging_ratios

    def hedging_ratio(self) -> None:
        """Dispatch to the selected hedging ratio calculation method.

        Calls either :meth:`_simple_ratio` or :meth:`_complex_ratio` based on
        the ``hedging_method`` provided at construction and stores the result
        in ``_hedging_ratios``.
        """
        self._hedging_methods[self._hedging_method]()

    def _calc_spread(self) -> None:
        """Compute the price spread from the hedging ratio.

        Spread is defined as::

            spread = series_1 - (hedging_ratio * series_2)

        Both series are sliced from index ``_lookback`` onwards to align with
        the valid hedging ratio window.
        """
        self._spread_df: pd.DataFrame = (
            self._prices[self._series_1][self._lookback:]
            - self._hedging_ratios * self._prices[self._series_2][self._lookback:]
        )

    def spread_calc(self) -> SpreadCalcResult:
        """Calculate rolling spread statistics and return a :class:`SpreadCalcResult`.

        Computes the spread via :meth:`_calc_spread`, then derives rolling mean,
        standard deviation, and z-score over the ``_lookback`` window.

        :returns: Dataclass containing the rolling mean, standard deviation, and
            z-score of the spread.
        :rtype: SpreadCalcResult
        """
        self._calc_spread()
        _mean: pd.Series = self._spread_df.rolling(self._lookback).mean()
        _std_dev: pd.Series = self._spread_df.rolling(self._lookback).std()
        self._spread_metrics: SpreadCalcResult = SpreadCalcResult(
            mean=_mean,
            std_dev=_std_dev,
            z_score=(self._spread_df - _mean) / _std_dev,
        )
        return self._spread_metrics

    def fetch_analytics(self) -> SpreadCalcResult:
        """Run the full pairs trading analytics pipeline.

        Calls :meth:`hedging_ratio` followed by :meth:`spread_calc` and returns
        the complete spread metrics.

        :returns: Spread metrics containing rolling mean, standard deviation, and
            z-score.
        :rtype: SpreadCalcResult
        """
        self.hedging_ratio()
        return self.spread_calc()