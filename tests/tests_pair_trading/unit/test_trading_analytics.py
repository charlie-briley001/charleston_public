"""Unit tests for PairsTradingAnalysis construction, validation, and analytics."""

from pathlib import Path

import pandas as pd
import pytest

from src.pairs_trading.exceptions.exceptions_trading_analytics import (
    LookbackError,
    ParamValidationError,
    SeriesValidationError,
)
from src.pairs_trading.pairs_trading_signals.trading_analytics import PairsTradingAnalysis
from tests.tests_pair_trading.fixtures.fixture_pairs_trading_signals import make_analysis, SERIES_1, SERIES_2


def test_pairs_trading_pass1():
    """PairsTradingAnalysis accepts a DataFrame and two ticker strings."""
    test_obj = make_analysis()
    assert test_obj._prices.shape == (2556, 2)


def test_pairs_trading_fail1():
    """PairsTradingAnalysis raises ParamValidationError when prices_df is not a DataFrame."""
    with pytest.raises(ParamValidationError):
        PairsTradingAnalysis(
            prices_df="hi",
            series_1="KO",
            series_2="PEP",
            lookback=60,
            hedging_method="complex",
        )


def test_pairs_trading_valid_series_fail1():
    """PairsTradingAnalysis raises SeriesValidationError when series_1 is not a string."""
    with pytest.raises(SeriesValidationError):
        PairsTradingAnalysis(
            prices_df=pd.concat([SERIES_1, SERIES_2], axis=1),
            series_1=0,
            series_2="PEP",
            lookback=60,
            hedging_method="complex",
        )


def test_pairs_trading_valid_series_fail2():
    """PairsTradingAnalysis raises SeriesValidationError when series_2 is not a column in prices_df."""
    with pytest.raises(SeriesValidationError):
        PairsTradingAnalysis(
            prices_df=pd.concat([SERIES_1, SERIES_2], axis=1),
            series_1="KO",
            series_2="HI",
            lookback=60,
            hedging_method="complex",
        )


def test_pairs_trading_prep_prices_pass():
    """PairsTradingAnalysis correctly records the observation count after nan removal."""
    test_obj = make_analysis()
    assert test_obj._observations == 2556


def test_pairs_trading_pass2():
    """PairsTradingAnalysis accepts two raw pd.Series objects and concatenates them internally."""
    test_obj = PairsTradingAnalysis(
        series_1=SERIES_1,
        series_2=SERIES_2,
        lookback=60,
        hedging_method="complex",
    )
    assert test_obj._prices.shape == (2556, 2)


def test_pairs_trading_fail2():
    """PairsTradingAnalysis raises ParamValidationError when series_1 is not a pd.Series."""
    with pytest.raises(ParamValidationError):
        PairsTradingAnalysis(
            series_1="test",
            series_2=SERIES_2,
            lookback=60,
            hedging_method="complex",
        )


def test_pairs_trading_obs_pass1():
    """PairsTradingAnalysis defaults lookback to 20% of observations when lookback is None."""
    test_obj = PairsTradingAnalysis(
        series_1=SERIES_1,
        series_2=SERIES_2,
        lookback=None,
        hedging_method="complex",
    )
    assert test_obj._lookback == 511


def test_pairs_trading_obs_fail1():
    """PairsTradingAnalysis raises LookbackError when lookback greater than observations."""
    with pytest.raises(LookbackError):
        PairsTradingAnalysis(
            series_1=SERIES_1,
            series_2=SERIES_2,
            lookback=6000,
            hedging_method="complex",
        )


def test_pairs_trading_hedging_fail1():
    """PairsTradingAnalysis raises ParamValidationError for an unknown hedging_method."""
    with pytest.raises(ParamValidationError):
        PairsTradingAnalysis(
            series_1=SERIES_1,
            series_2=SERIES_2,
            lookback=60,
            hedging_method="test",
        )


def test_hedging_simple():
    """_simple_ratio returns a series of correct length and expected mean."""
    test_obj = make_analysis()
    test_res = test_obj._simple_ratio()
    assert test_res.shape == (2497,)
    assert test_res.mean() == pytest.approx(0.3977085175359924)


def test_hedging_complex():
    """_complex_ratio returns a series of correct length and expected mean."""
    test_obj = make_analysis()
    test_res = test_obj._complex_ratio()
    assert test_res.shape == (2496,)
    assert test_res.mean() == pytest.approx(0.39738568520889106)


def test_spread_calc():
    """fetch_analytics returns spread metrics with correct shape and expected rolling statistics."""
    test_obj = make_analysis()
    test_res = test_obj.fetch_analytics()
    assert test_res.mean.shape == (2496,)
    assert test_res.mean.mean() == pytest.approx(0.14923500001835893)
    assert test_res.z_score.mean() == pytest.approx(0.0036885533755526534)
    assert test_res.std_dev.mean() == pytest.approx(1.1394984286018999)