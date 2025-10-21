from io import StringIO

import pandas as pd
import pytest
from sqlalchemy import create_engine

from abraxos import clear, read_csv, read_csv_chunks, split, to_sql, transform, use_sql, validate


# ---------------------
# Fixtures and Helpers
# ---------------------
@pytest.fixture
def sample_csv():
    return StringIO(
        """id,name,age
1,Joe,28
TOO,MANY,COLUMNS,HERE
2,Alice,35
3,Marcus,40
"""
    )


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "name": ["Joe", "Alice", "Marcus"],
        "age": [28, 35, 40]
    })


@pytest.fixture
def sqlite_engine():
    return create_engine("sqlite:///:memory:")


# ----------------
# Extract Tests
# ----------------
def test_read_csv(sample_csv):
    result = read_csv(sample_csv)
    assert isinstance(result.bad_lines, list)
    assert isinstance(result.dataframe, pd.DataFrame)
    assert not result.dataframe.empty


def test_read_csv_chunks(sample_csv):
    chunks = list(read_csv_chunks(sample_csv, chunksize=2))
    assert all(isinstance(r.dataframe, pd.DataFrame) for r in chunks)

    # At least one chunk should have a non-empty bad_lines list
    total_bad_lines = sum(len(r.bad_lines) for r in chunks)
    assert total_bad_lines >= 1


# ----------------
# Transform Tests
# ----------------
def test_transform_success(sample_df):
    def lowercase(df):
        df = df.copy()
        df["name"] = df["name"].str.lower()
        return df

    result = transform(sample_df, lowercase)
    assert result.errors == []
    assert result.success_df.equals(lowercase(sample_df))
    assert result.errored_df.empty


# ----------------
# Load Tests
# ----------------
def test_to_sql_success(sample_df, sqlite_engine):
    result = to_sql(sample_df, "people", sqlite_engine)
    assert isinstance(result.success_df, pd.DataFrame)

    # Verify data was written to SQLite
    with sqlite_engine.connect() as conn:
        result_df = pd.read_sql("SELECT * FROM people", conn)
        assert not result_df.empty


def test_use_sql_partial_failure(sample_df, sqlite_engine):
    df = sample_df.copy()
    df.loc[1, "name"] = "FAIL"  # Simulate a failure condition

    class FailingConnection:
        def execute(self, stmt, records):
            if any(r.get("name") == "FAIL" for r in records):
                raise ValueError("Insert error")

    class DummyInsert:
        pass

    result = use_sql(df, FailingConnection(), DummyInsert())
    assert isinstance(result.errors, list)
    assert not result.success_df.empty
    assert not result.errored_df.empty


# ----------------
# Validate Tests
# ----------------
class DummyModel:
    def model_validate(self, record):
        if record["age"] < 30:
            raise ValueError("Too young")
        self._record = record
        return self

    def model_dump(self):
        return self._record


def test_validate_mixed():
    df = pd.DataFrame({"name": ["A", "B"], "age": [25, 35]})
    result = validate(df, DummyModel())
    assert isinstance(result.errors, list)
    assert not result.success_df.empty
    assert not result.errored_df.empty


# ----------------
# Utils Tests
# ----------------
def test_split():
    df = pd.DataFrame({"x": range(10)})
    parts = split(df, 3)
    assert len(parts) == 3
    assert sum(len(p) for p in parts) == 10


def test_clear():
    df = pd.DataFrame({"x": [1, 2, 3]})
    cleared = clear(df)
    assert cleared.empty
    assert list(cleared.columns) == ["x"]
