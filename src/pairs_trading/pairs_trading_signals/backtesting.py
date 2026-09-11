"""Pairs trading backtesting module."""

from dataclasses import dataclass, field
from typing import Union

import pandas as pd


@dataclass
class BacktestingData:
    """Object for backtesting inputs and the aligned working DataFrame.

    Joins ``prices``, ``generated_signals``, and ``ratios`` on a
    shared index in ``__post_init__``, dropping any rows with missing values
    so all downstream calculations operate on a clean, aligned dataset.

    :param backtest_method: Name of the backtest method to invoke
        (e.g. ``'basic'``).
    :type backtest_method: str
    :param portfolio_value: Starting portfolio value.
    :type portfolio_value: float or int
    :param prices: DataFrame of asset prices with one column per asset.
        Must contain exactly the two tickers listed in ``assets``.
    :type prices: pd.DataFrame
    :param generated_signals: Time-indexed series of position signals
        (``-1`` short, ``0`` flat, ``1`` long) produced by
        :class:`~src.fin_data.pairs_trading_signals.signals.PairsTradingSignals`.
    :type generated_signals: pd.Series
    :param ratios: Time-indexed series of rolling hedging ratios produced by
        :class:`~src.fin_data.pairs_trading_signals.trading_analytics.PairsTradingAnalysis`.
    :type ratios: pd.Series
    :param assets: Exactly two ticker strings identifying the primary and
        secondary legs of the pair.
    :type assets: list[str]
    :raises ValueError: If ``assets`` does not contain exactly two elements.
    """

    backtest_method: str
    portfolio_value: Union[float, int]
    prices: pd.DataFrame
    generated_signals: pd.Series
    ratios: pd.Series
    assets: list[str]
    _final_df: pd.DataFrame = field(init=False)

    def __post_init__(self):
        """Validate inputs and build the aligned working DataFrame.

        :raises ValueError: If ``assets`` does not contain exactly two elements.
        """
        if len(self.assets) != 2:
            raise ValueError('asset must hold at least two asset names')
        self._final_df = pd.concat(
            [self.prices, self.generated_signals, self.ratios],
            axis=1,
        ).dropna()
        self._final_df.columns = [
            self.assets[0],
            self.assets[1],
            'generated_signals',
            'ratios',
        ]


@dataclass
class BacktestingResults:
    """Object for backtest output metrics.

    :param ending_portfolio_val: Portfolio value at the end of the backtest
        period, computed by compounding ``returns`` from ``portfolio_value``.
    :type ending_portfolio_val: float or int
    :param returns: Time-indexed series of per-period strategy returns.
    :type returns: pd.Series
    """

    ending_portfolio_val: Union[float, int]
    returns: pd.Series


class BacktestSignal(BacktestingData):
    """Executes backtesting logic against pre-aligned pairs trading data.

    Inherits all fields from :class:`BacktestingData`. Call
    :meth:`run_signal` to execute the method named by ``backtest_method``
    and receive a :class:`BacktestingResults` object.

    Example usage::

        backtest = BacktestSignal(
            backtest_method='basic',
            portfolio_value=100_000,
            prices=prices_df,
            generated_signals=signal_series,
            ratios=ratio_series,
            assets=['AAPL', 'MSFT'],
        )
        results = backtest.run_signal()
        print(results.ending_portfolio_val)
    """

    def run_backtest_basic(self) -> BacktestingResults:
        """Run a basic hedged pairs backtest using percentage returns.

        Computes per-period percentage returns for each leg, applies the
        position signal and hedging ratio, then derives the net strategy
        return as::

            total_return = (signal * series1) - (signal * ratio * series2)

        The ending portfolio value is calculated by compounding
        ``total_return`` from :attr:`portfolio_value`.

        :returns: Backtest results containing the ending portfolio value and
            the full time series of per-period strategy returns.
        :rtype: BacktestingResults
        """
        _series_1: pd.Series = self._final_df[self.assets[0]].pct_change().dropna()
        _series_2: pd.Series = self._final_df[self.assets[1]].pct_change().dropna()

        _series_1_returns: pd.Series = (
            self._final_df['generated_signals'] * _series_1
        )
        _series_2_returns: pd.Series = (
            self._final_df['generated_signals']
            * self._final_df['ratios']
            * _series_2
        )

        _total_returns: pd.Series = _series_1_returns - _series_2_returns

        return BacktestingResults(
            ending_portfolio_val=self.portfolio_value * (_total_returns + 1).cumprod().iloc[-1],
            returns=_total_returns,
        )

    def run_backtest(self) -> BacktestingResults:
        """Call to the backtest method specified by :attr:`backtest_method`.

        Resolves the method named ``run_backtest_{backtest_method}`` and
        calls it, returning the resulting :class:`BacktestingResults`.

        :returns: Backtest output containing the ending portfolio value and
            per-period returns (see :meth:`run_backtest_basic` for value
            semantics).
        :rtype: BacktestingResults
        :raises ValueError: If :attr:`backtest_method` does not correspond
            to a recognised backtest method.
        """
        method_name = f"run_backtest_{self.backtest_method}"
        if not hasattr(self, method_name):
            raise ValueError(f"Signal not found: '{self.backtest_method}'")
        return getattr(self, method_name)()