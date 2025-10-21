"""Tests for abraxos.transform module."""

import pandas as pd

from abraxos.transform import TransformResult, transform


class TestTransformResult:
    """Tests for TransformResult named tuple."""

    def test_named_tuple_fields(self):
        """Test that TransformResult has correct fields."""
        df = pd.DataFrame({'a': [1, 2]})
        result = TransformResult(errors=[], errored_df=df.iloc[:0], success_df=df)

        assert result.errors == []
        assert result.errored_df.empty
        assert result.success_df.equals(df)


class TestTransformSuccess:
    """Tests for successful transformations."""

    def test_simple_transformation(self, sample_df):
        """Test a simple successful transformation."""
        def uppercase_names(df):
            df = df.copy()
            df['name'] = df['name'].str.upper()
            return df

        result = transform(sample_df, uppercase_names)

        assert result.errors == []
        assert result.errored_df.empty
        assert all(result.success_df['name'] == ['ALICE', 'BOB', 'CHARLIE'])

    def test_transformation_adds_column(self, sample_df):
        """Test transformation that adds a column."""
        def add_doubled_age(df):
            df = df.copy()
            df['age_doubled'] = df['age'] * 2
            return df

        result = transform(sample_df, add_doubled_age)

        assert 'age_doubled' in result.success_df.columns
        assert result.errors == []

    def test_transformation_with_single_row(self, single_row_df):
        """Test transformation on single-row DataFrame."""
        def double_age(df):
            df = df.copy()
            df['age'] = df['age'] * 2
            return df

        result = transform(single_row_df, double_age)

        assert result.errors == []
        assert result.success_df['age'].iloc[0] == 50

    def test_transformation_with_empty_df(self, empty_df):
        """Test transformation on empty DataFrame."""
        def uppercase_names(df):
            df = df.copy()
            if not df.empty:
                df['name'] = df['name'].str.upper()
            return df

        result = transform(empty_df, uppercase_names)

        assert result.errors == []
        assert result.success_df.empty


class TestTransformFailure:
    """Tests for transformations that fail."""

    def test_complete_failure(self, sample_df):
        """Test transformation that always fails."""
        def always_fails(df):
            raise ValueError('Transformation failed')

        result = transform(sample_df, always_fails)

        assert len(result.errors) == len(sample_df)  # One error per row
        assert len(result.errored_df) == len(sample_df)
        assert result.success_df.empty

    def test_single_row_failure(self, single_row_df):
        """Test failure on single-row DataFrame."""
        def always_fails(df):
            raise ValueError('Failed')

        result = transform(single_row_df, always_fails)

        assert len(result.errors) == 1
        assert len(result.errored_df) == 1
        assert result.success_df.empty


class TestTransformPartialFailure:
    """Tests for transformations with partial failures."""

    def test_partial_failure_by_row(self, sample_df):
        """Test transformation that fails on specific rows."""
        def fail_on_bob(df):
            df = df.copy()
            if 'Bob' in df['name'].values:
                raise ValueError('Bob not allowed')
            df['name'] = df['name'].str.upper()
            return df

        result = transform(sample_df, fail_on_bob)

        # Should have some errors
        assert len(result.errors) > 0
        # Should have some successes
        assert not result.success_df.empty
        # Should have some failures
        assert not result.errored_df.empty
        # Total should equal original
        assert len(result.success_df) + len(result.errored_df) == len(sample_df)

    def test_partial_failure_numeric(self):
        """Test transformation with numeric data causing partial failure."""
        df = pd.DataFrame({'x': [1, 2, 0, 3, 4]})

        def divide_by_x(df):
            df = df.copy()
            # Check for zeros and raise error
            if (df['x'] == 0).any():
                raise ValueError('Cannot divide by zero')
            df['result'] = 10 / df['x']
            return df

        result = transform(df, divide_by_x)

        # Division by zero should cause one failure
        assert len(result.errors) > 0
        assert not result.success_df.empty
        assert not result.errored_df.empty


class TestTransformChunking:
    """Tests for chunk parameter behavior."""

    def test_chunks_parameter_two(self, large_df):
        """Test chunking with chunks=2."""
        call_count = {'count': 0}

        def counting_transformer(df):
            call_count['count'] += 1
            if len(df) > 10:
                raise ValueError('Too many rows')
            return df

        _ = transform(large_df, counting_transformer, chunks=2)

        # Should have recursively split until chunks are small enough
        assert call_count['count'] > 1

    def test_chunks_parameter_four(self, large_df):
        """Test chunking with chunks=4."""
        call_count = {'count': 0}

        def counting_transformer(df):
            call_count['count'] += 1
            if len(df) > 5:
                raise ValueError('Too many rows')
            return df

        _ = transform(large_df, counting_transformer, chunks=4)

        # Should split into 4 chunks each time
        assert call_count['count'] > 1

    def test_chunks_maintained_in_recursion(self, large_df):
        """Test that chunks parameter is maintained through recursion."""
        # This is a regression test for the bug fix
        chunk_sizes_seen = []

        def track_chunk_size(df):
            chunk_sizes_seen.append(len(df))
            if len(df) > 20:
                raise ValueError('Too large')
            return df

        _ = transform(large_df, track_chunk_size, chunks=3)

        # After first split with chunks=3, should see sizes around 33, 33, 34
        # Not 50, 50 (which would happen if chunks reset to 2)
        max_chunk = max(chunk_sizes_seen[1:4]) if len(chunk_sizes_seen) > 3 else 0
        assert max_chunk < 40, 'Chunks parameter not maintained in recursion'


class TestTransformErrorIsolation:
    """Tests for error isolation behavior."""

    def test_isolates_single_bad_row(self):
        """Test that bad rows are isolated from good ones."""
        df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})

        def fail_on_three(df):
            df = df.copy()
            if 3 in df['value'].values:
                raise ValueError('Three not allowed')
            df['doubled'] = df['value'] * 2
            return df

        result = transform(df, fail_on_three)

        # Should isolate the row with value=3
        assert len(result.errored_df) == 1
        assert result.errored_df['value'].iloc[0] == 3
        # Other rows should succeed
        assert len(result.success_df) == 4

    def test_preserves_original_rows_on_error(self):
        """Test that errored rows contain original data."""
        df = pd.DataFrame({'value': [1, 2, 3]})

        def always_fails(df):
            raise ValueError('Failed')

        result = transform(df, always_fails)

        # Errored df should contain original data
        pd.testing.assert_frame_equal(result.errored_df, df)

    def test_error_contains_exception(self):
        """Test that errors list contains actual exceptions."""
        df = pd.DataFrame({'value': [1, 2, 3]})

        def custom_error(df):
            raise ValueError('Custom error message')

        result = transform(df, custom_error)

        assert len(result.errors) > 0
        assert all(isinstance(e, Exception) for e in result.errors)
        assert any('Custom error message' in str(e) for e in result.errors)


class TestTransformColumnPreservation:
    """Tests for column preservation."""

    def test_preserves_column_names(self, sample_df):
        """Test that column names are preserved."""
        def identity(df):
            return df.copy()

        result = transform(sample_df, identity)

        assert list(result.success_df.columns) == list(sample_df.columns)

    def test_preserves_index(self):
        """Test that DataFrame index is preserved."""
        df = pd.DataFrame({'value': [1, 2, 3]}, index=[10, 20, 30])

        def double_value(df):
            df = df.copy()
            df['value'] = df['value'] * 2
            return df

        result = transform(df, double_value)

        assert list(result.success_df.index) == [10, 20, 30]


class TestIntegration:
    """Integration tests for transform module."""

    def test_complex_transformation_pipeline(self, sample_df):
        """Test a complex multi-step transformation."""
        def complex_transform(df):
            df = df.copy()
            df['name'] = df['name'].str.upper()
            df['age_category'] = df['age'].apply(
                lambda x: 'young' if x < 30 else 'old'
            )
            df['city_code'] = df['city'].str[:2]
            return df

        result = transform(sample_df, complex_transform)

        assert result.errors == []
        assert 'age_category' in result.success_df.columns
        assert 'city_code' in result.success_df.columns

    def test_transform_after_split(self, large_df):
        """Test transforming DataFrames after splitting."""
        from abraxos.utils import split

        parts = split(large_df, 3)

        def double_value(df):
            df = df.copy()
            df['value'] = df['value'] * 2
            return df

        results = [transform(part, double_value) for part in parts]

        assert all(r.errors == [] for r in results)
        total_rows = sum(len(r.success_df) for r in results)
        assert total_rows == len(large_df)

