"""Unit tests for PairsTradingSignals construction and signal generation."""

import pandas as pd
import pytest

from src.pairs_trading.pairs_trading_signals.signals import PairsTradingSignals
from tests.tests_pair_trading.fixtures.fixture_pairs_trading_signals import make_analysis


def test_signal_obj_create():
    """PairsTradingSignals initialises correctly and signal_result is empty before run_signal."""
    test_trading_obj = make_analysis()
    signals = PairsTradingSignals(
        signal="basic",
        meta_data=test_trading_obj.fetch_analytics(),
        entry_point=2.0,
        exit_point=0.5,
    )
    assert signals.signal == "basic"
    assert signals.entry_point == 2.0
    assert signals.exit_point == 0.5
    assert signals.signal_result.empty


def test_run_signal_pass():
    """run_signal returns a Series of position values with the expected mean."""
    test_trading_obj = make_analysis()
    signals = PairsTradingSignals(
        signal="basic",
        meta_data=test_trading_obj.fetch_analytics(),
        entry_point=2.0,
        exit_point=0.5,
    )
    test_res = signals.run_signal()
    assert isinstance(test_res, pd.Series)
    assert set(test_res.unique()).issubset({-1, 0, 1})
    assert test_res.mean() == pytest.approx(-0.011899876897825195)


def test_run_signal_fail():
    """run_signal raises ValueError for an unrecognised signal name."""
    test_trading_obj = make_analysis()
    signals = PairsTradingSignals(
        signal="complex",
        meta_data=test_trading_obj.fetch_analytics(),
        entry_point=2.0,
        exit_point=0.5,
    )
    with pytest.raises(ValueError):
        test_res = signals.run_signal()