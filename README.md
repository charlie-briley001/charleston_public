# charleston_public

Charles Briley's public repository — a portfolio of personal projects and algorithm practice.

---

## Projects

### MBTA App (`src/mbta_app/`)

A real-time data pipeline that fetches live vehicle positions from the [MBTA V3 API](https://api-v3.mbta.com) and persists them to a [DuckDB](https://duckdb.org) database.

#### Architecture

```
CLI (orchestrator/cli.py)
  └── MbtaApiPull (orchestrator/orchestration.py)
        ├── GetConnection  → DuckDBConn  (db_builder/)
        ├── MbtaApi        → MBTA V3 REST API (mbta_connector/api_main.py)
        └── Vehicles       → Pydantic model + DuckDB insert (mbta_connector/data_parsing.py)
```

**Pipeline steps (per run):**
1. Open a DuckDB connection (file-backed or in-memory)
2. Fetch the current vehicle snapshot from `GET /vehicles`
3. Flatten the JSON:API response into typed `Vehicles` records via Pydantic
4. `CREATE TABLE IF NOT EXISTS vehicles` (idempotent DDL)
5. Insert all vehicle records; close the connection

**Database schema (`vehicles` table):**

| Column | Type | Description |
|---|---|---|
| `id` | VARCHAR | Unique vehicle ID |
| `current_status` | VARCHAR | `IN_TRANSIT_TO`, `STOPPED_AT`, `INCOMING_AT` |
| `current_stop_sequence` | VARCHAR | Current/next stop ordinal |
| `direction_id` | VARCHAR | `0` (outbound) or `1` (inbound) |
| `latitude` | BIGINT | WGS-84 latitude |
| `longitude` | BIGINT | WGS-84 longitude |
| `updated_at` | TIMESTAMP | ISO 8601 timestamp of last position update |
| `route` | VARCHAR | Route short name (e.g. `Red`, `28`) |
| `trip` | VARCHAR | GTFS trip ID |

**Supported MBTA V3 resources** (via `mbta_connector/data_parsing.py`):

| Model | Endpoint | Key fields |
|---|---|---|
| `Lines` | `/lines` | `id`, `long_name`, `short_name` |
| `Route` | `/routes` | `id`, `long_name`, `direction_destinations`, `fare_class`, `line` |
| `Vehicles` | `/vehicles` | `id`, `latitude`, `longitude`, `current_status`, `route`, `trip` |

#### Requirements

- **Python 3.11+**
- **Windows** — the API key is read from Windows Credential Manager via `win32cred`. Linux/macOS would require swapping `get_auth` for a cross-platform keyring library.
- MBTA V3 API key stored in Windows Credential Manager under the name `mbta_api_key`

**Dependencies** (install via `pip install -r requirements.txt` or `pyproject.toml`):
- `httpx` — HTTP client
- `pydantic` — model validation
- `duckdb` — embedded analytics database
- `pywin32` — Windows Credential Manager access
- `pyyaml` — SQL template loading

#### Setup

1. **Get an MBTA API key** at [api-v3.mbta.com](https://api-v3.mbta.com).
2. **Store it in Windows Credential Manager:**
   - Open *Credential Manager* → *Windows Credentials* → *Add a generic credential*
   - Internet or network address: `mbta_api_key`
   - Password: your API key
3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

#### Usage

Run from the repo root:

```bash
# Persist to a DuckDB file
python -m src.mbta_app --conn_type duckdb --db-file_path mbta.db

# Run entirely in memory (no file written)
python -m src.mbta_app --conn_type duckdb --db-memory true
```

`--db-file_path` and `--db-memory` are mutually exclusive.

Logs are written to `src/mbta_app/logs/mbta_api_<timestamp>.log`.

#### Docs

Sphinx documentation is generated in `docs/`. Docstrings written with Claude assistance.

To rebuild:

```bash
cd docs
make html
```

Then open `docs/build/html/index.html`.

---

### LeetCode Examples (`src/leetcode_examples/`)

Algorithm practice problems implemented as Jupyter notebooks.

| Category | Problems |
|---|---|
| **Breadth-first search** | Invert Binary Tree, Level Order Bottom |
| **Strings** | Excel Sheet Column Finder, Isomorphic Strings, Valid Palindrome |
| **Arrays** | Remove Duplicates from Sorted Array, Three Closest |


## License

This repository is public for portfolio purposes. No license is granted for reuse without permission.
