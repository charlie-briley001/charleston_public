"""Pairs trading signal generation module."""

from dataclasses import dataclass, field
from typing import Union

import pandas as pd

from src.fin_data.pairs_trading_signals.trading_analytics import SpreadCalcResult


@dataclass
class PairsTradingDetails:
    """Container for pairs trading signal config and results.

    :param signal: Name of the signal method to invoke (e.g. ``'basic'``).
    :type signal: str
    :param meta_data: Pre-computed spread analytics returned by
        :class:`~src.fin_data.pairs_trading_signals.trading_analytics.PairsTradingAnalysis`.
    :type meta_data: SpreadCalcResult
    :param entry_point: Z-score threshold at which a position is opened.
    :type entry_point: float or int
    :param exit_point: Z-score threshold at which an open position is closed.
    :type exit_point: float or int
    :param signal_result: Time-indexed series of position signals (``-1``, ``0``,
        or ``1``). Populated after calling :meth:`~PairsTradingSignals.run_signal`.
    :type signal_result: pd.Series
    """

    signal: str
    meta_data: SpreadCalcResult
    entry_point: Union[float, int]
    exit_point: Union[float, int]
    signal_result: pd.Series = field(default_factory=pd.Series)


class PairsTradingSignals(PairsTradingDetails):
    """Executes pairs trading signal logic against pre-computed spread analytics.

    Inherits all fields from :class:`PairsTradingDetails`. Call
    :meth:`run_signal` to execute the method named by ``signal`` and
    populate :attr:`signal_result`.

    Example usage::

        result = analysis.fetch_analytics()
        signals = PairsTradingSignals(
            signal='basic',
            meta_data=result,
            entry_point=2.0,
            exit_point=0.5,
        )
        signals.run_signal()
        print(signals.signal_result)
    """

    def _pairs_trading_basic(self) -> pd.Series:
        """Generate a basic mean-reversion signal from z-score thresholds.

        Iterates over each z-score value and assigns a position of ``1``
        (long), ``-1`` (short), or ``0`` (flat) based on whether the spread
        has moved beyond :attr:`entry_point` or reverted within
        :attr:`exit_point`. ``series_1`` is treated as the primary leg:
        a long position expects ``series_1`` to rise relative to
        ``series_2``; a short position expects the reverse.

        Updates :attr:`signal_result` in place and also returns it.

        :returns: Time-indexed series of position signals where ``1`` is long,
            ``-1`` is short, and ``0`` is flat.
        :rtype: pd.Series
        """
        _holding = 0
        z_scores = self.meta_data.z_score.dropna()
        self.signal_result = pd.Series(0, index=z_scores.index)

        for idx, score in z_scores.items():
            if _holding == 0:
                if score > self.entry_point:
                    # Spread too wide — short: expect convergence (series_1 down, series_2 up).
                    _holding = -1
                elif score < (-1 * self.entry_point):
                    # Spread too narrow — long: expect divergence (series_1 up, series_2 down).
                    _holding = 1

            elif _holding == 1:
                if score > (-1 * self.exit_point):
                    # Spread has reverted toward mean, long opportunity gone.
                    _holding = 0

            elif _holding == -1:
                if score < self.exit_point:
                    # Spread has narrowed back toward mean, short opportunity gone.
                    _holding = 0

            self.signal_result.loc[idx] = _holding

        return self.signal_result

    def run_signal(self) -> pd.Series:
        """Call the signal method specified by :attr:`signal`.

        Resolves the method named ``_pairs_trading_{signal}`` and calls it,
        populating :attr:`signal_result` with the generated position series.

        :returns: Time-indexed series of position signals (see
            :meth:`_pairs_trading_basic` for value semantics).
        :rtype: pd.Series
        :raises ValueError: If :attr:`signal` does not correspond to a
            recognised signal method.
        """
        signal_name = f"_pairs_trading_{self.signal}"
        if not hasattr(self, signal_name):
            raise ValueError(f"Signal not found: '{self.signal}'")
        return getattr(self, signal_name)()