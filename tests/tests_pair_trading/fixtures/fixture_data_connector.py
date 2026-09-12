"""Shared pytest fixtures for the data connector test suite."""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def mock_yf_ticker_info():
    """Patch yf.Ticker to return metadata for KO and PEP."""
    mock_ticker1 = MagicMock()
    mock_ticker1.info = {
        "industryKey": "beverages-non-alcoholic",
        "sectorKey": "consumer-defensive",
        "quoteType": "EQUITY",
        "displayName": "Coca-Cola",
    }

    mock_ticker2 = MagicMock()
    mock_ticker2.info = {
        "industryKey": "beverages-non-alcoholic",
        "sectorKey": "consumer-defensive",
        "quoteType": "EQUITY",
        "displayName": "Pepsi",
    }

    with patch(
        "src.pairs_trading.data_connector.object_models.yf.Ticker",
        side_effect=[mock_ticker1, mock_ticker2],
    ) as mock_ticker:
        yield mock_ticker


@pytest.fixture
def mock_yf_ticker_info_FAIL():
    """Patch yf.Ticker so the second ticker returns a non-correct asset type."""
    mock_ticker1 = MagicMock()
    mock_ticker1.info = {
        "industryKey": "beverages-non-alcoholic",
        "sectorKey": "consumer-defensive",
        "quoteType": "EQUITY",
        "displayName": "Coca-Cola",
    }

    mock_ticker2 = MagicMock()
    mock_ticker2.info = {
        "industryKey": "beverages-non-alcoholic",
        "sectorKey": "consumer-defensive",
        "quoteType": "FIXED_INCOME",
        "displayName": "Pepsi",
    }

    with patch(
        "src.pairs_trading.data_connector.object_models.yf.Ticker",
        side_effect=[mock_ticker1, mock_ticker2],
    ) as mock_ticker:
        yield mock_ticker


def build_hist_data():
    """Return a mock yfinance historical DataFrame for KO and PEP."""
    data = np.array([
        [
            227.50, 229.10, 226.80, 228.75, 228.75, 45230100,
            410.20, 413.55, 408.90, 412.30, 412.30, 18904500,
        ],
        [
            228.90, 230.40, 227.60, 229.95, 229.95, 39871200,
            412.80, 415.10, 410.75, 414.60, 414.60, 17233800,
        ],
    ])

    mock_data = pd.DataFrame(
        data,
        index=pd.date_range("2026-09-01", periods=2, freq="D"),
        columns=pd.MultiIndex.from_product(
            [["KO", "PEP"], ["Open", "High", "Low", "Close", "Adj Close", "Volume"]],
            names=["Ticker", "Price"],
        ),
    )
    mock_data.index.name = "Date"
    return mock_data


@pytest.fixture
def mock_yf_ticker_download():
    """Patch yf.download to return a pre-built multi-ticker DataFrame."""
    with patch(
        "src.pairs_trading.data_connector.api_main.yf.download",
        return_value=build_hist_data(),
    ) as mock_ticker:
        yield mock_ticker


@pytest.fixture
def mock_yf_ticker_download_fail():
    """Patch yf.download to raise a ValueError, simulating a failed download."""
    with patch(
        "src.pairs_trading.data_connector.api_main.yf.download",
        side_effect=ValueError("Error Occured"),
    ) as mock_ticker:
        yield mock_ticker