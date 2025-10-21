"""Shared pytest fixtures for abraxos tests."""

from io import StringIO

import pandas as pd
import pytest
from sqlalchemy import create_engine


@pytest.fixture
def sample_df():
    """Create a simple sample DataFrame."""
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['NYC', 'LA', 'SF']
    })


@pytest.fixture
def empty_df():
    """Create an empty DataFrame with schema."""
    return pd.DataFrame({'name': [], 'age': [], 'city': []})


@pytest.fixture
def single_row_df():
    """Create a DataFrame with a single row."""
    return pd.DataFrame({'name': ['Alice'], 'age': [25], 'city': ['NYC']})


@pytest.fixture
def large_df():
    """Create a larger DataFrame for testing chunking."""
    return pd.DataFrame({
        'id': range(100),
        'value': [i * 2 for i in range(100)]
    })


@pytest.fixture
def csv_with_bad_lines():
    """Create a CSV string with malformed lines."""
    return StringIO(
        """id,name,age
1,Alice,25
2,Bob,30
EXTRA,COLUMNS,HERE,TOO,MANY
3,Charlie,35
,,,,,
4,Diana,40
"""
    )


@pytest.fixture
def valid_csv():
    """Create a valid CSV string."""
    return StringIO(
        """id,name,age
1,Alice,25
2,Bob,30
3,Charlie,35
"""
    )


@pytest.fixture
def sqlite_engine():
    """Create an in-memory SQLite engine."""
    return create_engine('sqlite:///:memory:')


@pytest.fixture
def sample_records():
    """Create sample records as list of dicts."""
    return [
        {'name': 'Alice', 'age': 25, 'city': 'NYC'},
        {'name': 'Bob', 'age': 30, 'city': 'LA'},
        {'name': 'Charlie', 'age': 35, 'city': 'SF'}
    ]

