from pathlib import Path

import pandas as pd

from src.pairs_trading.pairs_trading_signals.trading_analytics import PairsTradingAnalysis

FIXTURES = Path(__file__).parent
SERIES_1 = pd.read_pickle(FIXTURES / "series_1.pkl")
SERIES_2 = pd.read_pickle(FIXTURES / "series_2.pkl")

def make_analysis() -> PairsTradingAnalysis:
    """Return a standard PairsTradingAnalysis instance built from a combined DataFrame."""
    return PairsTradingAnalysis(
        prices_df=pd.concat([SERIES_1, SERIES_2], axis=1),
        series_1="KO",
        series_2="PEP",
        lookback=60,
        hedging_method="complex",
    )
