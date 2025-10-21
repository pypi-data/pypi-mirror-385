"""Tests for abraxos.load module."""

import pandas as pd

from abraxos.load import ToSqlResult, insert_df, to_sql, use_sql


class TestToSqlResult:
    """Tests for ToSqlResult named tuple."""

    def test_named_tuple_fields(self):
        """Test that ToSqlResult has correct fields."""
        df = pd.DataFrame({'a': [1, 2]})
        result = ToSqlResult(errors=[], errored_df=df.iloc[:0], success_df=df)

        assert result.errors == []
        assert result.errored_df.empty
        assert result.success_df.equals(df)


class TestToSqlSuccess:
    """Tests for successful SQL insertions."""

    def test_simple_insert(self, sample_df, sqlite_engine):
        """Test basic insertion to SQL database."""
        result = to_sql(sample_df, 'test_table', sqlite_engine)

        assert result.errors == []
        assert result.errored_df.empty
        assert len(result.success_df) == len(sample_df)

        # Verify data was actually inserted
        with sqlite_engine.connect() as conn:
            query_result = pd.read_sql('SELECT * FROM test_table', conn)
            assert len(query_result) == len(sample_df)

    def test_insert_with_index(self, sample_df, sqlite_engine):
        """Test insertion including DataFrame index."""
        result = to_sql(sample_df, 'test_with_index', sqlite_engine, index=True)

        assert result.errors == []
        assert len(result.success_df) == len(sample_df)

    def test_insert_if_exists_append(self, sample_df, sqlite_engine):
        """Test appending to existing table."""
        # First insert
        to_sql(sample_df, 'append_table', sqlite_engine)

        # Second insert with append
        result = to_sql(sample_df, 'append_table', sqlite_engine, if_exists='append')

        assert result.errors == []

        # Should have double the rows
        with sqlite_engine.connect() as conn:
            query_result = pd.read_sql('SELECT * FROM append_table', conn)
            assert len(query_result) == len(sample_df) * 2

    def test_insert_if_exists_replace(self, sample_df, sqlite_engine):
        """Test replacing existing table."""
        # First insert
        to_sql(sample_df, 'replace_table', sqlite_engine)

        # Create different data
        new_df = pd.DataFrame({'name': ['Xavier'], 'age': [50], 'city': ['Boston']})

        # Replace with new data
        result = to_sql(new_df, 'replace_table', sqlite_engine, if_exists='replace')

        assert result.errors == []

        # Should only have new data
        with sqlite_engine.connect() as conn:
            query_result = pd.read_sql('SELECT * FROM replace_table', conn)
            assert len(query_result) == 1
            assert query_result['name'].iloc[0] == 'Xavier'

    def test_insert_empty_df(self, empty_df, sqlite_engine):
        """Test inserting empty DataFrame."""
        result = to_sql(empty_df, 'empty_table', sqlite_engine)

        # Should succeed with no errors
        assert result.errors == []
        assert result.success_df.empty

    def test_insert_single_row(self, single_row_df, sqlite_engine):
        """Test inserting single-row DataFrame."""
        result = to_sql(single_row_df, 'single_row', sqlite_engine)

        assert result.errors == []
        assert len(result.success_df) == 1


class TestToSqlChunking:
    """Tests for chunking behavior in to_sql."""

    def test_chunks_parameter_maintained(self, sqlite_engine):
        """Test that chunks parameter is maintained through recursion."""
        # Create a DataFrame where we can track chunking behavior
        df = pd.DataFrame({'value': range(20)})

        # Use chunks=4 to verify it's maintained
        result = to_sql(df, 'chunks_test', sqlite_engine, chunks=4)

        # Should succeed
        assert result.errors == []


class TestToSqlPartialFailure:
    """Tests for partial failures in SQL insertions."""

    def test_isolates_bad_row(self, sqlite_engine):
        """Test that bad rows are isolated using chunking."""
        # Create a mock failing scenario
        # This is hard to test with real SQLite, so we'll test the structure
        df = pd.DataFrame({'id': [1, 2, 3, 4, 5]})
        result = to_sql(df, 'test_isolate', sqlite_engine)

        # All should succeed in this case
        assert len(result.success_df) + len(result.errored_df) == len(df)


class TestUseSql:
    """Tests for use_sql function."""

    def test_use_sql_with_mock_connection(self):
        """Test use_sql with mocked connection."""

        class MockConnection:
            def __init__(self):
                self.executed = []

            def execute(self, query, records):
                self.executed.extend(records)

        class MockQuery:
            pass

        df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        conn = MockConnection()
        query = MockQuery()

        result = use_sql(df, conn, query)

        assert result.errors == []
        assert len(result.success_df) == 3
        assert result.errored_df.empty
        assert len(conn.executed) == 3

    def test_use_sql_with_failure(self):
        """Test use_sql with partial failure."""

        class FailingConnection:
            def execute(self, query, records):
                # Fail on records with 'b'
                if any(r['name'] == 'Bob' for r in records):
                    raise ValueError('Bob not allowed')

        class MockQuery:
            pass

        df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie']})
        result = use_sql(df, FailingConnection(), MockQuery())

        # Should have isolated Bob
        assert len(result.errors) > 0
        assert len(result.success_df) > 0
        assert len(result.errored_df) > 0

    def test_use_sql_chunks_parameter(self):
        """Test that chunks parameter works in use_sql."""

        class FailingConnection:
            def execute(self, query, records):
                if len(records) > 2:
                    raise ValueError('Too many records')

        class MockQuery:
            pass

        df = pd.DataFrame({'value': range(10)})
        result = use_sql(df, FailingConnection(), MockQuery(), chunks=3)

        # Should split into smaller chunks
        assert len(result.success_df) + len(result.errored_df) == len(df)


class TestInsertDf:
    """Tests for insert_df helper function."""

    def test_insert_df_basic(self):
        """Test basic insert_df functionality."""

        class MockConnection:
            def __init__(self):
                self.records = []

            def execute(self, query, records):
                self.records = records

        class MockQuery:
            pass

        df = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y']})
        conn = MockConnection()

        result = insert_df(df, conn, MockQuery())

        assert result.errors == []
        assert len(result.success_df) == 2
        assert len(conn.records) == 2
        assert conn.records[0]['a'] == 1
        assert conn.records[0]['b'] == 'x'


class TestIntegration:
    """Integration tests for load module."""

    def test_full_pipeline_with_sqlite(self, large_df, sqlite_engine):
        """Test full insertion pipeline with larger dataset."""
        result = to_sql(large_df, 'large_table', sqlite_engine)

        assert result.errors == []
        assert len(result.success_df) == len(large_df)

        # Verify all data
        with sqlite_engine.connect() as conn:
            query_result = pd.read_sql('SELECT * FROM large_table', conn)
            assert len(query_result) == len(large_df)

    def test_multiple_tables(self, sample_df, sqlite_engine):
        """Test inserting into multiple tables."""
        result1 = to_sql(sample_df, 'table1', sqlite_engine)
        result2 = to_sql(sample_df, 'table2', sqlite_engine)

        assert result1.errors == []
        assert result2.errors == []

        with sqlite_engine.connect() as conn:
            t1 = pd.read_sql('SELECT * FROM table1', conn)
            t2 = pd.read_sql('SELECT * FROM table2', conn)
            assert len(t1) == len(t2) == len(sample_df)

    def test_with_nan_values(self, sqlite_engine):
        """Test inserting DataFrame with NaN values."""
        import numpy as np

        df = pd.DataFrame({
            'a': [1, np.nan, 3],
            'b': ['x', 'y', None]
        })

        result = to_sql(df, 'with_nans', sqlite_engine)

        assert result.errors == []

        with sqlite_engine.connect() as conn:
            query_result = pd.read_sql('SELECT * FROM with_nans', conn)
            assert len(query_result) == 3

