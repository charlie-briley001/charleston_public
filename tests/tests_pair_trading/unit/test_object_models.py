"""Unit tests for TimeData, TickerObj, and PairsFoundation object models."""

import pytest

from src.pairs_trading.data_connector.object_models import (
    PairsFoundation,
    TickerObj,
    TimeData,
)
from src.pairs_trading.exceptions.exceptions_data_connector import (
    AssetClassError,
    TimeParametersError,
)
from tests.tests_pair_trading.fixtures.fixture_data_connector import (
    mock_yf_ticker_info,
    mock_yf_ticker_info_FAIL,
)


def test_time_data_base():
    """TimeData accepts valid string date and interval inputs."""
    test_obj = TimeData(
        start_date="2016-01-01",
        end_date="2026-03-05",
        interval="1d",
    )
    assert test_obj.start_date == "2016-01-01"
    assert test_obj.end_date == "2026-03-05"
    assert test_obj.interval == "1d"


def test_time_data_fail1():
    """TimeData raises TimeParametersError when start_date is not a string."""
    with pytest.raises(TimeParametersError):
        TimeData(start_date=2, end_date="2026-03-05", interval="1d")


def test_time_data_fail2():
    """TimeData raises TimeParametersError when end_date is not a string."""
    with pytest.raises(TimeParametersError):
        TimeData(start_date="2026-03-5", end_date=20, interval="1d")


def test_time_data_fail3():
    """TimeData raises TimeParametersError when interval is not a string."""
    with pytest.raises(TimeParametersError):
        TimeData(start_date="2026-03-05", end_date="2026-03-05", interval=1)


def test_time_data_fail4():
    """TimeData raises TimeParametersError when start_date is None."""
    with pytest.raises(TimeParametersError):
        TimeData(start_date=None, end_date="2026-03-05", interval=1)


def test_time_data_fail5():
    """TimeData raises TimeParametersError when end_date is None."""
    with pytest.raises(TimeParametersError):
        TimeData(start_date="2026-03-05", end_date=None, interval=1)


def test_time_data_fail6():
    """TimeData raises TimeParametersError when interval is None."""
    with pytest.raises(TimeParametersError):
        TimeData(start_date="2026-03-05", end_date="2026-03-05", interval=None)


def test_ticker_obj(mock_yf_ticker_info):
    """TickerObj populates metadata fields from the yfinance API response."""
    test_obj = TickerObj(ticker="KO")
    assert test_obj.ticker == "KO"
    assert test_obj.industry_key == "beverages-non-alcoholic"
    assert test_obj.sector_key == "consumer-defensive"
    assert test_obj.asset_type == "EQUITY"
    assert test_obj.display_name == "Coca-Cola"
    assert len(test_obj.meta) == 4


def test_pairs_foundation1(mock_yf_ticker_info):
    """PairsFoundation accepts two pre-built TickerObj instances and preserves all fields."""
    test_obj_1 = TickerObj(ticker="KO")
    test_obj_2 = TickerObj(ticker="PEP")

    test_obj = PairsFoundation(ticker_1=test_obj_1, ticker_2=test_obj_2)
    assert test_obj.ticker_1.ticker == "KO"
    assert test_obj.ticker_1.industry_key == "beverages-non-alcoholic"
    assert test_obj.ticker_1.sector_key == "consumer-defensive"
    assert test_obj.ticker_1.asset_type == "EQUITY"
    assert test_obj.ticker_1.display_name == "Coca-Cola"
    assert len(test_obj.ticker_1.meta) == 4
    assert test_obj.ticker_2.ticker == "PEP"
    assert test_obj.ticker_2.industry_key == "beverages-non-alcoholic"
    assert test_obj.ticker_2.sector_key == "consumer-defensive"
    assert test_obj.ticker_2.asset_type == "EQUITY"
    assert test_obj.ticker_2.display_name == "Pepsi"
    assert len(test_obj.ticker_2.meta) == 4
    assert mock_yf_ticker_info.call_count == 2


def test_pairs_foundation1_fail(mock_yf_ticker_info_FAIL):
    """PairsFoundation raises AssetClassError when tickers have different asset types."""
    test_obj_1 = TickerObj(ticker="KO")
    test_obj_2 = TickerObj(ticker="PEP")

    with pytest.raises(AssetClassError):
        PairsFoundation(ticker_1=test_obj_1, ticker_2=test_obj_2)


def test_pairs_foundation2(mock_yf_ticker_info):
    """PairsFoundation string tickers to TickerObj and populates all fields."""
    test_obj = PairsFoundation(ticker_1="KO", ticker_2="PEP")
    assert test_obj.ticker_1.ticker == "KO"
    assert test_obj.ticker_1.industry_key == "beverages-non-alcoholic"
    assert test_obj.ticker_1.sector_key == "consumer-defensive"
    assert test_obj.ticker_1.asset_type == "EQUITY"
    assert test_obj.ticker_1.display_name == "Coca-Cola"
    assert len(test_obj.ticker_1.meta) == 4
    assert test_obj.ticker_2.ticker == "PEP"
    assert test_obj.ticker_2.industry_key == "beverages-non-alcoholic"
    assert test_obj.ticker_2.sector_key == "consumer-defensive"
    assert test_obj.ticker_2.asset_type == "EQUITY"
    assert test_obj.ticker_2.display_name == "Pepsi"
    assert len(test_obj.ticker_2.meta) == 4
    assert mock_yf_ticker_info.call_count == 2