"""Class object to hold a variety of pairs trading methods"""
from dataclasses import dataclass, field
from typing import Union

import pandas as pd

from src.fin_data.pairs_trading_signals.trading_analytics import SpreadCalcResult


@dataclass
class PairsTradingDetails:
    signal: str
    meta_data: SpreadCalcResult
    entry_point: Union[float, int]
    exit_point: Union[float, int]
    signal_result: pd.Series = field(default_factory = pd.Series)


class PairsTradingSignals(PairsTradingDetails):
    """Class to hold trading signals, and run specific signal requested"""
    def _pairs_trading_basic(self) -> pd.Series:
        """
        Basic signal generation that we are dealing with
        Treating series_1 as the primary position (determines long or short)
        """
        _holding = 0 #variable to identify what kind of position is held
        z_scores = self.meta_data.z_score.dropna()
        self.signal_result = pd.Series(0, index=z_scores.index)
        for idx, score in z_scores.items():
            # loop over each day and identify the action to be taken based on the z-score spread
            if _holding == 0: ## not currently holding an open positions
                if score > self.entry_point:  # spread is wide --> short as we expect spread to converge back (series 1 down and/or series 2 up)
                    _holding = -1 ## -->  ( (-1) * series_1 ) - ( (-1) * hedging_ratio * series_2 )
                elif score < ( -1 * self.entry_point):  # spread too narrow --> expect it to diverge (series 1 goes up and / or series 2 goes down)
                    _holding = 1 ## -->  ( (1) * series_1 ) - ( (1) * hedging_ratio * series_2 )

            elif _holding == 1:  ## this means we had previously believed that spread was to close and would expect series 1 to rise and / or series 2 to fall
                if score > (-1 * self.exit_point):  # spread has widened enough to revert close to mean --> long opportunity is gone.
                    _holding = 0

            elif _holding == -1:
                if score < self.exit_point:  # spread has narrowed close enough to mean to close any short opportunity that existed
                    _holding = 0

            self.signal_result.loc[idx] = _holding

        return self.signal_result

    def run_signal(self):
        """function to take in obj param and call specific signal function needed"""
        signal_name = f"_pairs_trading_{self.signal}"
        if not hasattr(self, signal_name):
            raise ValueError(f"Signal not found: '{self.signal}'")
        return getattr(self, signal_name)()

