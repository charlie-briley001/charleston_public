# charleston_public

Charles Briley's public repository — a portfolio of personal projects and algorithm practice.

---

## Projects

### MBTA App — `src/mbta_app/`

A real-time data pipeline that fetches live vehicle positions from the MBTA V3 API and persists them to a DuckDB database. Accepts a YAML config and runs via a single CLI command.

See [`src/mbta_app/README.md`](src/mbta_app/README.md) for setup, usage, and schema details.

---

### Pairs Trading — `src/pairs_trading/`

A modular trading signal generation pipeline that pulls historical price data for two assets, tests for cointegration, computes rolling hedging ratios and z-score spreads, generates mean-reversion signals, and runs a backtest. Driven by a YAML parameter file via CLI.

See [`src/pairs_trading/README.md`](src/pairs_trading/README.md) for setup, usage, and configuration details.

---

## Docs

Sphinx documentation covering both projects is generated in `docs/`. To rebuild:

```bash
cd docs
make html
```

Then open `docs/build/html/index.html`.

---

## License

This repository is public for portfolio purposes. No license is granted for reuse without permission.