"""Entry point for the fin_data package.

Delegates execution to :func:`~src.fin_data.pairs_trading_signals.cli.main`.

Run via::

    python -m src.fin_data --param_file <path/to/config.yaml>
"""

from src.pairs_trading.pairs_trading_signals.cli import main

if __name__ == "__main__":
    main()