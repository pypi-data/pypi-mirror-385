"""Tests for abraxos.utils module."""

import numpy as np
import pandas as pd

from abraxos.utils import clear, split, to_records


class TestSplit:
    """Tests for split function."""

    def test_split_into_two(self, sample_df):
        """Test splitting DataFrame into 2 parts."""
        parts = split(sample_df, 2)

        assert isinstance(parts, tuple)
        assert len(parts) == 2
        assert all(isinstance(p, pd.DataFrame) for p in parts)
        # Total rows should match original
        assert sum(len(p) for p in parts) == len(sample_df)

    def test_split_into_three(self, sample_df):
        """Test splitting DataFrame into 3 parts."""
        parts = split(sample_df, 3)

        assert len(parts) == 3
        assert sum(len(p) for p in parts) == len(sample_df)

    def test_split_preserves_columns(self, sample_df):
        """Test that split preserves column names."""
        parts = split(sample_df, 2)

        for part in parts:
            assert list(part.columns) == list(sample_df.columns)

    def test_split_single_row(self, single_row_df):
        """Test splitting a single-row DataFrame."""
        parts = split(single_row_df, 2)

        assert len(parts) == 2
        # One part should have 1 row, other should be empty
        assert sum(len(p) for p in parts) == 1

    def test_split_empty_df(self, empty_df):
        """Test splitting an empty DataFrame."""
        parts = split(empty_df, 2)

        assert len(parts) == 2
        assert all(p.empty for p in parts)
        assert all(list(p.columns) == list(empty_df.columns) for p in parts)

    def test_split_default_chunks(self, large_df):
        """Test split with default chunks=2."""
        parts = split(large_df)

        assert len(parts) == 2
        # Should be approximately equal
        assert 45 <= len(parts[0]) <= 55
        assert 45 <= len(parts[1]) <= 55

    def test_split_many_chunks(self, large_df):
        """Test splitting into many chunks."""
        parts = split(large_df, 10)

        assert len(parts) == 10
        assert sum(len(p) for p in parts) == 100

    def test_split_more_chunks_than_rows(self, sample_df):
        """Test when chunk count > row count."""
        parts = split(sample_df, 10)

        # numpy.array_split handles this gracefully
        assert len(parts) == 10
        non_empty = [p for p in parts if not p.empty]
        assert len(non_empty) == len(sample_df)

    def test_split_preserves_index(self):
        """Test that split preserves DataFrame index."""
        df = pd.DataFrame({'a': [1, 2, 3]}, index=[10, 20, 30])
        parts = split(df, 2)

        all_indices = pd.concat(parts).index
        assert list(all_indices) == [10, 20, 30]


class TestClear:
    """Tests for clear function."""

    def test_clear_returns_empty(self, sample_df):
        """Test that clear returns empty DataFrame."""
        result = clear(sample_df)

        assert result.empty
        assert len(result) == 0

    def test_clear_preserves_columns(self, sample_df):
        """Test that clear preserves column names."""
        result = clear(sample_df)

        assert list(result.columns) == list(sample_df.columns)

    def test_clear_preserves_dtypes(self):
        """Test that clear preserves data types."""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'str_col': ['a', 'b', 'c'],
            'float_col': [1.0, 2.0, 3.0]
        })
        result = clear(df)

        assert result['int_col'].dtype == df['int_col'].dtype
        assert result['str_col'].dtype == df['str_col'].dtype
        assert result['float_col'].dtype == df['float_col'].dtype

    def test_clear_already_empty(self, empty_df):
        """Test clearing an already empty DataFrame."""
        result = clear(empty_df)

        assert result.empty
        assert list(result.columns) == list(empty_df.columns)

    def test_clear_single_row(self, single_row_df):
        """Test clearing a single-row DataFrame."""
        result = clear(single_row_df)

        assert result.empty
        assert list(result.columns) == list(single_row_df.columns)

    def test_clear_with_index(self):
        """Test that clear preserves index type but empties it."""
        df = pd.DataFrame({'a': [1, 2, 3]}, index=['x', 'y', 'z'])
        result = clear(df)

        assert result.empty
        assert len(result.index) == 0


class TestToRecords:
    """Tests for to_records function."""

    def test_to_records_basic(self, sample_df):
        """Test converting DataFrame to records."""
        records = to_records(sample_df)

        assert isinstance(records, list)
        assert len(records) == len(sample_df)
        assert all(isinstance(r, dict) for r in records)

    def test_to_records_column_names(self, sample_df):
        """Test that records have correct keys."""
        records = to_records(sample_df)

        for record in records:
            assert set(record.keys()) == set(sample_df.columns)

    def test_to_records_values(self, sample_df):
        """Test that records have correct values."""
        records = to_records(sample_df)

        assert records[0]['name'] == 'Alice'
        assert records[0]['age'] == 25
        assert records[1]['name'] == 'Bob'

    def test_to_records_with_nan(self):
        """Test that NaN is converted to None."""
        df = pd.DataFrame({
            'a': [1, np.nan, 3],
            'b': ['x', 'y', None]
        })
        records = to_records(df)

        assert records[1]['a'] is None
        assert records[2]['b'] is None

    def test_to_records_empty_df(self, empty_df):
        """Test converting empty DataFrame."""
        records = to_records(empty_df)

        assert records == []

    def test_to_records_single_row(self, single_row_df):
        """Test converting single-row DataFrame."""
        records = to_records(single_row_df)

        assert len(records) == 1
        assert records[0]['name'] == 'Alice'

    def test_to_records_preserves_types(self):
        """Test that to_records preserves data types."""
        df = pd.DataFrame({
            'int_col': [1, 2],
            'str_col': ['a', 'b'],
            'float_col': [1.5, 2.5],
            'bool_col': [True, False]
        })
        records = to_records(df)

        assert isinstance(records[0]['int_col'], (int, np.integer))
        assert isinstance(records[0]['str_col'], str)
        assert isinstance(records[0]['float_col'], (float, np.floating))
        assert isinstance(records[0]['bool_col'], (bool, np.bool_))

    def test_to_records_with_none_values(self):
        """Test DataFrame with explicit None values."""
        df = pd.DataFrame({
            'a': [1, None, 3],
            'b': ['x', None, 'z']
        })
        records = to_records(df)

        # None should remain None
        assert records[1]['a'] is None
        assert records[1]['b'] is None


class TestIntegration:
    """Integration tests for utils module."""

    def test_split_clear_concat(self, large_df):
        """Test splitting, clearing, and concatenating."""
        parts = split(large_df, 4)
        cleared = clear(large_df)
        recombined = pd.concat([cleared] + list(parts))

        # Should equal original (minus the empty cleared df)
        assert len(recombined) == len(large_df)

    def test_to_records_to_dataframe_roundtrip(self, sample_df):
        """Test converting to records and back to DataFrame."""
        records = to_records(sample_df)
        df_new = pd.DataFrame(records)

        # Should be equivalent (column order might differ)
        pd.testing.assert_frame_equal(
            df_new[sample_df.columns],
            sample_df.reset_index(drop=True)
        )

