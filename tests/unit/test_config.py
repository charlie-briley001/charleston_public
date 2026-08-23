import pytest

from src.mbta_app.config.config import UPDATE_ROW, CREATE_TABLE, _load_queries, _QUERY_TEMPLATES_PATH
from tests.conftest import TEST_YAML, TEST_YAML_FAIL


def test_load_queries_pass():
    _query: dict = _load_queries(TEST_YAML)
    assert isinstance(_query, dict)
    assert list(_query.keys()) == ['create_table']
    assert len(_query.get('create_table')) == 344

def test_load_queries_exception():
    with pytest.raises(KeyError):
        _query: dict = _load_queries(TEST_YAML_FAIL)

def test_variables():
    assert len(UPDATE_ROW) == 311
    assert len(CREATE_TABLE) == 405
    assert _QUERY_TEMPLATES_PATH.name == 'query_templates.yaml'