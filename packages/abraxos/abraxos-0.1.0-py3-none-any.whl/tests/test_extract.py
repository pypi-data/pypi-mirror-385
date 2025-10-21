"""Tests for abraxos.extract module."""

from io import StringIO

import pandas as pd

from abraxos.extract import ReadCsvResult, read_csv, read_csv_all, read_csv_chunks


class TestReadCsvResult:
    """Tests for ReadCsvResult named tuple."""

    def test_named_tuple_fields(self):
        """Test that ReadCsvResult has correct fields."""
        df = pd.DataFrame({'a': [1, 2]})
        result = ReadCsvResult(bad_lines=[], dataframe=df)

        assert result.bad_lines == []
        assert result.dataframe.equals(df)

    def test_named_tuple_access(self):
        """Test accessing fields by index and name."""
        df = pd.DataFrame({'a': [1, 2]})
        bad = [['x', 'y']]
        result = ReadCsvResult(bad, df)

        assert result[0] == bad
        assert result.bad_lines == bad
        assert result[1].equals(df)


class TestReadCsvAll:
    """Tests for read_csv_all function."""

    def test_read_valid_csv(self, valid_csv):
        """Test reading a valid CSV file."""
        result = read_csv_all(valid_csv)

        assert isinstance(result, ReadCsvResult)
        assert len(result.bad_lines) == 0
        assert len(result.dataframe) == 3
        assert list(result.dataframe.columns) == ['id', 'name', 'age']

    def test_read_csv_with_bad_lines(self, csv_with_bad_lines):
        """Test reading CSV with malformed lines."""
        result = read_csv_all(csv_with_bad_lines)

        assert isinstance(result, ReadCsvResult)
        assert len(result.bad_lines) > 0
        # Should have captured the malformed lines
        assert any(len(line) > 3 for line in result.bad_lines)
        # Valid data should still be parsed
        assert len(result.dataframe) > 0

    def test_read_empty_csv(self):
        """Test reading an empty CSV."""
        csv = StringIO('id,name,age\n')
        result = read_csv_all(csv)

        assert len(result.bad_lines) == 0
        assert result.dataframe.empty
        assert list(result.dataframe.columns) == ['id', 'name', 'age']

    def test_kwargs_passed_to_pandas(self):
        """Test that kwargs are passed to pandas.read_csv."""
        csv = StringIO('id;name;age\n1;Alice;25\n2;Bob;30')
        result = read_csv_all(csv, sep=';')

        assert len(result.dataframe) == 2
        assert list(result.dataframe.columns) == ['id', 'name', 'age']


class TestReadCsvChunks:
    """Tests for read_csv_chunks function."""

    def test_read_in_chunks(self, valid_csv):
        """Test reading CSV in chunks."""
        chunks = list(read_csv_chunks(valid_csv, chunksize=2))

        assert len(chunks) == 2  # 3 rows / chunksize 2 = 2 chunks
        assert all(isinstance(c, ReadCsvResult) for c in chunks)
        assert len(chunks[0].dataframe) == 2
        assert len(chunks[1].dataframe) == 1

    def test_chunks_with_bad_lines(self, csv_with_bad_lines):
        """Test chunked reading with malformed lines."""
        chunks = list(read_csv_chunks(csv_with_bad_lines, chunksize=2))

        assert len(chunks) > 0
        # Check that bad lines are captured per chunk
        total_bad = sum(len(c.bad_lines) for c in chunks)
        assert total_bad > 0

    def test_single_row_chunks(self, valid_csv):
        """Test reading with chunksize=1."""
        chunks = list(read_csv_chunks(valid_csv, chunksize=1))

        assert len(chunks) == 3
        assert all(len(c.dataframe) == 1 for c in chunks)

    def test_chunk_size_larger_than_file(self, valid_csv):
        """Test chunksize larger than file."""
        chunks = list(read_csv_chunks(valid_csv, chunksize=100))

        assert len(chunks) == 1
        assert len(chunks[0].dataframe) == 3


class TestReadCsv:
    """Tests for main read_csv function."""

    def test_read_without_chunks(self, valid_csv):
        """Test read_csv without chunking."""
        result = read_csv(valid_csv)

        assert isinstance(result, ReadCsvResult)
        assert len(result.dataframe) == 3

    def test_read_with_chunks(self, valid_csv):
        """Test read_csv with chunking."""
        result = read_csv(valid_csv, chunksize=2)

        # Should return a generator
        chunks = list(result)
        assert len(chunks) == 2
        assert all(isinstance(c, ReadCsvResult) for c in chunks)

    def test_chunksize_none_returns_result(self, valid_csv):
        """Test that chunksize=None returns ReadCsvResult not generator."""
        result = read_csv(valid_csv, chunksize=None)

        assert isinstance(result, ReadCsvResult)
        assert not hasattr(result, '__next__')

    def test_chunksize_explicit_returns_generator(self, valid_csv):
        """Test that explicit chunksize returns generator."""
        result = read_csv(valid_csv, chunksize=1)

        # Check it's a generator
        assert hasattr(result, '__next__')

    def test_kwargs_forwarded(self):
        """Test that kwargs are forwarded correctly."""
        csv = StringIO('id;name;age\n1;Alice;25')
        result = read_csv(csv, sep=';')

        assert 'Alice' in result.dataframe['name'].values


class TestIntegration:
    """Integration tests for extract module."""

    def test_read_bad_csv_file(self):
        """Test reading the actual bad.csv test file."""
        result = read_csv_all('tests/bad.csv')

        assert len(result.bad_lines) == 2
        assert len(result.dataframe) == 5
        assert 'id' in result.dataframe.columns

    def test_chunked_bad_csv_file(self):
        """Test reading bad.csv in chunks."""
        chunks = list(read_csv_chunks('tests/bad.csv', chunksize=3))

        total_bad = sum(len(c.bad_lines) for c in chunks)
        assert total_bad == 2

        total_rows = sum(len(c.dataframe) for c in chunks)
        assert total_rows == 5

