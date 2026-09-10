"""Command-line interface for the pairs trading signal pipeline.

Reads a YAML parameter file, fetches historical price data for two assets,
computes analytics, generates trading signals, runs a backtest, and prints
the ending portfolio value to stdout.

Run via::

    python -m src.fin_data --param_file <path/to/config.yaml>
"""

import argparse

import pandas as pd
import yaml

from src.fin_data.data_connector.api_main import FinDataApi
from src.fin_data.data_connector.object_models import TimeData
from src.fin_data.pairs_trading_signals.backtesting import BacktestSignal
from src.fin_data.pairs_trading_signals.signals import PairsTradingSignals
from src.fin_data.pairs_trading_signals.trading_analytics import PairsTradingAnalysis
from src.fin_data.utils.stats_utils import StatsUtils


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    :returns: Parsed arguments namespace containing ``param_file``.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Run pairs trading pipeline from a YAML config.")
    parser.add_argument(
        "--param_file",
        type=str,
        required=True,
        help="Path to the YAML parameter config file.",
    )
    return parser.parse_args()


def main() -> None:
    """Coordinate execution of the pairs trading pipeline.

    Reads a YAML config file, fetches historical price data for two assets,
    computes trading analytics, generates position signals, runs a backtest,
    and prints the ending portfolio value.

    Expected YAML keys:

    - ``asset1``, ``asset2``: ticker symbols for the two legs of the pair.
    - ``start_date``, ``end_date``: date range for historical data (``YYYY-MM-DD``).
    - ``interval``: price interval (e.g. ``'1d'``).
    - ``lookback``: rolling window size for analytics.
    - ``hedging_method``: hedging ratio method (e.g. ``'basic'``, ``'complex'``).
    - ``signal_method``: signal generation method (e.g. ``'basic'``).
    - ``entry_point``: z-score threshold to enter a position.
    - ``exit_point``: z-score threshold to exit a position.
    - ``portfolio_value``: starting portfolio value.
    - ``backtest_method``: backtest method to run (e.g. ``'basic'``).
    - ``coint_p_value``: significance level for the test (default ``0.05``).
      The pipeline exits early if the pair fails this test.
    """
    args = parse_args()
    with open(args.param_file, "r") as f:
        config = yaml.safe_load(f)

    # Fetch historical price data
    fin_data_api = FinDataApi(
        ticker_1=config["asset1"],
        ticker_2=config["asset2"],
    )
    hist_data = fin_data_api.pull_hist(
        TimeData(
            start_date=config["start_date"],
            end_date=config["end_date"],
            interval=config["interval"],
        )
    )
    series_1 = hist_data[config["asset1"]]["Close"]
    series_1.name = config["asset1"]
    series_2 = hist_data[config["asset2"]]["Close"]
    series_2.name = config["asset2"]

    # Cointegration check — exit early if the pair is not cointegrated
    if not StatsUtils.cointegration_test(series_1, series_2, p_value=config["coint_p_value"]):
        print(f"Cointegration test failed for {config['asset1']} & {config['asset2']} ")
        return

    # Compute trading analytics
    trading_obj = PairsTradingAnalysis(
        prices_df=pd.concat([series_1, series_2], axis=1),
        series_1=config["asset1"],
        series_2=config["asset2"],
        lookback=config["lookback"],
        hedging_method=config["hedging_method"],
    )
    analytics_result = trading_obj.fetch_analytics()

    # Generate signals
    signal_obj = PairsTradingSignals(
        signal=config["signal_method"],
        meta_data=analytics_result,
        entry_point=config["entry_point"],
        exit_point=config["exit_point"],
    )
    res1 = signal_obj.run_signal()

    # Run backtest
    backtest_obj = BacktestSignal(
        portfolio_value=config["portfolio_value"],
        backtest_method=config["backtest_method"],
        prices=trading_obj._prices,
        generated_signals=res1,
        ratios=trading_obj._hedging_ratios,
        assets=[trading_obj._series_1, trading_obj._series_2],
    )
    back_test_results = backtest_obj.run_backtest()

    print(f"Portfolio Value - {back_test_results.ending_portfolio_val}")

