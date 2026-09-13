"""Unit tests for the AdfData dataclass and StatsUtils statistical methods."""

import numpy as np
import pandas as pd
import pytest

from src.pairs_trading.exceptions.exceptions_stats_utils import StatsUtilsDataTypeError
from src.pairs_trading.utils.stats_utils import AdfData, StatsUtils


def test_adf_data_pass():
    """AdfData stores all fields correctly on construction."""
    test_obj = AdfData(
        test_stat=1,
        p_value=0.05,
        lags=0,
        observations=10,
    )
    assert test_obj.test_stat == 1
    assert test_obj.p_value == 0.05
    assert test_obj.lags == 0
    assert test_obj.observations == 10


def test_adf_test_pass1():
    """adf_test returns correct statistics for a numpy array input."""
    np.random.seed(42)
    arr = np.random.rand(10)
    test_res = StatsUtils.adf_test(arr)
    assert test_res.test_stat == pytest.approx(-3.2679632294080396)
    assert test_res.p_value == pytest.approx(0.07168972745698056)


def test_adf_test_pass2():
    """adf_test returns correct statistics for a pd.Series input."""
    np.random.seed(42)
    arr = np.random.rand(10)
    test_res = StatsUtils.adf_test(pd.Series(arr))
    assert test_res.test_stat == pytest.approx(-3.2679632294080396)
    assert test_res.p_value == pytest.approx(0.07168972745698056)


def test_adf_test_fail():
    """adf_test raises StatsUtilsDataTypeError for non-array input."""
    with pytest.raises(StatsUtilsDataTypeError):
        StatsUtils.adf_test("123")


def test_stationarity_test_pass1():
    """stationarity_test returns False when p-value exceeds the threshold via dict input."""
    test_dict = {
        "test_stat": -3.2679632294080396,
        "p_value": 0.07168972745698056,
        "lags": 2,
        "observations": 7,
    }
    test_obj = StatsUtils.stationarity_test(adf_result=test_dict)
    assert test_obj is False


def test_stationarity_test_pass2():
    """stationarity_test returns False when passed a pre-computed AdfData result."""
    np.random.seed(42)
    arr = np.random.rand(10)
    test_adf_obj = StatsUtils.adf_test(pd.Series(arr))
    test_obj = StatsUtils.stationarity_test(adf_result=test_adf_obj)
    assert test_obj is False


def test_stationarity_test_pass3():
    """stationarity_test returns False when passed a raw data series."""
    np.random.seed(42)
    arr = np.random.rand(10)
    test_obj = StatsUtils.stationarity_test(data_series=pd.Series(arr))
    assert test_obj is False


def test_stationarity_test_fail1():
    """stationarity_test raises StatsUtilsDataTypeError when test_p_val is not numeric."""
    with pytest.raises(StatsUtilsDataTypeError):
        StatsUtils.stationarity_test(test_p_val=".05")


def test_stationarity_test_fail2():
    """stationarity_test raises StatsUtilsDataTypeError when test_p_val is outside (0, 1)."""
    with pytest.raises(StatsUtilsDataTypeError):
        StatsUtils.stationarity_test(test_p_val=5)


def test_stationarity_test_fail3():
    """stationarity_test raises StatsUtilsDataTypeError when no adf_result or data_series is provided."""
    with pytest.raises(StatsUtilsDataTypeError):
        StatsUtils.stationarity_test(test_p_val=0.5)


def test_stationarity_test_fail4():
    """stationarity_test raises StatsUtilsDataTypeError when adf_result is not an AdfData or dict."""
    with pytest.raises(StatsUtilsDataTypeError):
        StatsUtils.stationarity_test(adf_result="test")


def test_cointegration_test():
    """cointegration_test returns False for two unrelated random series."""
    np.random.seed(42)
    arr1 = np.random.rand(10)
    np.random.seed(24)
    arr2 = np.random.rand(10)

    test_res = StatsUtils.cointegration_test(pd.Series(arr1), pd.Series(arr2))
    assert test_res is False


def test_compute_coint_spread():
    """compute_coint_spread returns OLS residuals matching expected values."""
    np.random.seed(42)
    arr1 = np.random.rand(10)
    np.random.seed(24)
    arr2 = np.random.rand(10)

    test_res = StatsUtils.compute_coint_spread(pd.Series(arr1), pd.Series(arr2))
    expected = [
        -0.04196584257367286,
        0.4629117068277643,
        0.32639436415827977,
        -0.020361426462481624,
        -0.4244145413508972,
        -0.3207706133071555,
        -0.3484496637229758,
        0.2735066341033696,
        -0.040763897211983036,
        0.13391327953975196,
    ]
    assert test_res.to_list() == pytest.approx(expected)