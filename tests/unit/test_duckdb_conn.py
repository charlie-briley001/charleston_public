import tempfile
from pathlib import Path

import pytest

from src.mbta_app.db_builder.general.exceptions import ValidationError, DBConnectionError


def test_validate_args_fail1(in_memory_db_init):
    in_memory_db_init._file_name = None
    in_memory_db_init._memory = None
    with pytest.raises(ValidationError):
        in_memory_db_init._validate_args({})

def test_validate_args_fail2(in_memory_db_init):
    in_memory_db_init._file_name = "test"
    in_memory_db_init._memory = "test"
    with pytest.raises(ValidationError):
        in_memory_db_init._validate_args({})

def test_connect_args_pass1(in_memory_db_init):
    tmp_dir = tempfile.TemporaryDirectory()
    in_memory_db_init._file_name = Path(tmp_dir.name) / 'test.db'
    in_memory_db_init.connect()
    in_memory_db_init.close()
    assert in_memory_db_init._file_name.exists()
    tmp_dir.cleanup()

def test_connect_args_pass2(in_memory_db_init):
    in_memory_db_init._memory = True
    in_memory_db_init._file_name = None
    in_memory_db_init.connect()
    assert in_memory_db_init._conn.execute("SELECT 1").fetchone()[0] == 1
    in_memory_db_init.close()

def test_connect_args_fail1(in_memory_db_init):
    with pytest.raises(DBConnectionError):
        in_memory_db_init._file_name = None
        in_memory_db_init._memory = None
        in_memory_db_init.connect()
