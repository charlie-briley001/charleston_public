"""Unit tests for the FinDataApi class."""

import pandas as pd
import pytest

from src.pairs_trading.data_connector.api_main import FinDataApi
from src.pairs_trading.data_connector.object_models import TimeData, TickerObj
from src.pairs_trading.exceptions.exceptions_data_connector import (
    AssetClassError,
    TickerCreationDataError,
)
from tests.tests_pair_trading.fixtures.fixture_data_connector import (
    mock_yf_ticker_download,
    mock_yf_ticker_download_fail,
    mock_yf_ticker_info,
    mock_yf_ticker_info_FAIL,
)


def test_fin_data_api1(mock_yf_ticker_info):
    """FinDataApi accepts two pre-built TickerObj instances and preserves all fields."""
    test_obj_1 = TickerObj(ticker="KO")
    test_obj_2 = TickerObj(ticker="PEP")

    test_obj = FinDataApi(ticker_1=test_obj_1, ticker_2=test_obj_2)
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


def test_fin_data_api1_fail(mock_yf_ticker_info_FAIL):
    """FinDataApi raises AssetClassError when tickers have different asset types."""
    test_obj_1 = TickerObj(ticker="KO")
    test_obj_2 = TickerObj(ticker="PEP")

    with pytest.raises(AssetClassError):
        FinDataApi(ticker_1=test_obj_1, ticker_2=test_obj_2)


def test_fin_data_api2(mock_yf_ticker_info):
    """FinDataApi string tickers to TickerObj and populates all fields."""
    test_obj = FinDataApi(ticker_1="KO", ticker_2="PEP")
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


def test_fin_data_api_hist(mock_yf_ticker_download):
    """pull_hist returns a DataFrame and calls yf.download exactly once."""
    test_obj = FinDataApi(ticker_1="KO", ticker_2="PEP")
    test_time = TimeData(
        start_date="2026-03-05",
        end_date="2026-03-05",
        interval="1d",
    )
    test_hist_data = test_obj.pull_hist(test_time)
    assert isinstance(test_hist_data, pd.DataFrame)
    assert mock_yf_ticker_download.call_count == 1


def test_fin_data_api_hist_fail(mock_yf_ticker_download_fail):
    """pull_hist raises TickerCreationDataError when yf.download raises ValueError."""
    test_obj = FinDataApi(ticker_1="KO", ticker_2="PEP")
    test_time = TimeData(
        start_date="2026-03-05",
        end_date="2026-03-05",
        interval="1d",
    )
    with pytest.raises(TickerCreationDataError):
        test_obj.pull_hist(test_time)