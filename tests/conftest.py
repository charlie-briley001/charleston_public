from pathlib import Path

import pytest

from src.mbta_app.db_builder import GetConnection

# Paths
TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"
TEST_YAML = FIXTURES_DIR / "test_query_templates.yaml"
TEST_YAML_FAIL = FIXTURES_DIR / "test_query_templates_fail.yaml"


@pytest.fixture(scope="session")
def in_memory_db_init():
    connector_cls = GetConnection.create_connection(connection_type='duckdb')
    conn = connector_cls({'memory': True})
    yield conn