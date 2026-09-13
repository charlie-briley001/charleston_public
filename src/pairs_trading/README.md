# Pairs Trading

A modular trading signal generation pipeline that pulls historical price data for two assets, tests for cointegration, computes rolling hedging ratios and z-score spreads, generates mean-reversion trading signals, and runs a backtest — all driven by a YAML parameter file.

---

## Architecture

```
CLI (pairs_trading_signals/cli.py)
  └── FinDataApi          → yfinance historical prices  (data_connector/)
  └── StatsUtils          → cointegration test           (utils/stats_utils.py)
  └── PairsTradingAnalysis → hedging ratio + spread      (pairs_trading_signals/trading_analytics.py)
  └── PairsTradingSignals → position signals             (pairs_trading_signals/signals.py)
  └── BacktestSignal      → backtest + portfolio value   (pairs_trading_signals/backtesting.py)
```

**Pipeline steps (per run):**
1. Load a YAML config file specifying the asset pair and strategy parameters
2. Fetch historical close prices for both tickers via `yfinance`
3. Run an Engle-Granger cointegration test — exit early if the pair fails
4. Compute a rolling hedging ratio (simple price-ratio mean or rolling OLS)
5. Derive the spread and its rolling mean, standard deviation, and z-score
6. Generate long/short/flat position signals from z-score thresholds
7. Run a basic hedged backtest and print the ending portfolio value

---

## Key Modules

| Module | Description |
|---|---|
| `data_connector/object_models.py` | `TickerObj`, `TimeData`, `PairsFoundation` — validated input models |
| `data_connector/api_main.py` | `FinDataApi` — fetches historical OHLCV data via yfinance |
| `utils/stats_utils.py` | `StatsUtils` — ADF test, cointegration test, OLS spread |
| `pairs_trading_signals/trading_analytics.py` | `PairsTradingAnalysis` — rolling hedging ratio, spread, z-score |
| `pairs_trading_signals/signals.py` | `PairsTradingSignals` — z-score threshold signal generation |
| `pairs_trading_signals/backtesting.py` | `BacktestSignal` — hedged return backtest |

---

## Requirements

- **Python 3.11+**
- No API key required — price data is sourced from `yfinance` (public market data)

**Dependencies:**
- `yfinance` — historical price data
- `pandas` — time-series data handling
- `numpy` — numerical operations
- `statsmodels` — ADF test, cointegration test, OLS regression
- `pydantic` — input model validation
- `pyyaml` — config file parsing

---

## Setup

Install dependencies from the repo root:

```bash
pip install -r requirements.txt
```

---

## Usage

Run from the repo root with a YAML parameter file:

```bash
python -m src.pairs_trading --param_file path/to/config.yaml
```

**Example YAML config:**

```yaml
asset1: KO
asset2: PEP
start_date: "2016-01-01"
end_date: "2026-01-01"
interval: "1d"
lookback: 60
hedging_method: complex
signal_method: basic
entry_point: 2.0
exit_point: 0.5
portfolio_value: 100000
backtest_method: basic
coint_p_value: 0.05
```

**Config keys:**

| Key | Description |
|---|---|
| `asset1`, `asset2` | Ticker symbols for the two legs of the pair |
| `start_date`, `end_date` | Historical data range (`YYYY-MM-DD`) |
| `interval` | Price frequency — yfinance interval string (e.g. `1d`, `1wk`) |
| `lookback` | Rolling window size in periods |
| `hedging_method` | `simple` (rolling mean ratio) or `complex` (rolling OLS) |
| `signal_method` | Signal strategy — currently `basic` (z-score threshold) |
| `entry_point` | Z-score threshold to open a position |
| `exit_point` | Z-score threshold to close a position |
| `portfolio_value` | Starting portfolio value for the backtest |
| `backtest_method` | Backtest strategy — currently `basic` (hedged percentage returns) |
| `coint_p_value` | Significance level for the cointegration test (default `0.05`) |

If the pair fails the cointegration test at the given significance level, the pipeline exits early without running the signal or backtest.