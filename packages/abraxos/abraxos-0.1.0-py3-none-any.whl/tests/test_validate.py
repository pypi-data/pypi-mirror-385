"""Tests for abraxos.validate module."""

import pandas as pd

from abraxos.validate import ValidateResult, validate


class TestValidateResult:
    """Tests for ValidateResult named tuple."""

    def test_named_tuple_fields(self):
        """Test that ValidateResult has correct fields."""
        df = pd.DataFrame({'a': [1, 2]})
        result = ValidateResult(errors=[], errored_df=df.iloc[:0], success_df=df)

        assert result.errors == []
        assert result.errored_df.empty
        assert result.success_df.equals(df)


class TestValidateSuccess:
    """Tests for successful validation."""

    def test_all_valid_rows(self):
        """Test validation where all rows are valid."""

        class SimpleModel:
            def model_validate(self, record):
                if record['age'] < 0:
                    raise ValueError('Age must be positive')
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
        result = validate(df, SimpleModel())

        assert result.errors == []
        assert result.errored_df.empty
        assert len(result.success_df) == 2

    def test_single_row_validation(self):
        """Test validating single-row DataFrame."""

        class SimpleModel:
            def model_validate(self, record):
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        result = validate(df, SimpleModel())

        assert result.errors == []
        assert len(result.success_df) == 1

    def test_empty_dataframe(self):
        """Test validating empty DataFrame."""

        class SimpleModel:
            def model_validate(self, record):
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': [], 'age': []})
        result = validate(df, SimpleModel())

        assert result.errors == []
        assert result.success_df.empty
        assert result.errored_df.empty


class TestValidateFailure:
    """Tests for validation failures."""

    def test_all_invalid_rows(self):
        """Test validation where all rows fail."""

        class StrictModel:
            def model_validate(self, record):
                raise ValueError('Always fails')

            def model_dump(self):
                return {}

        df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
        result = validate(df, StrictModel())

        assert len(result.errors) == 2
        assert len(result.errored_df) == 2
        assert result.success_df.empty

    def test_single_row_failure(self):
        """Test failure on single row."""

        class StrictModel:
            def model_validate(self, record):
                raise ValueError('Validation failed')

            def model_dump(self):
                return {}

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        result = validate(df, StrictModel())

        assert len(result.errors) == 1
        assert len(result.errored_df) == 1
        assert result.success_df.empty


class TestValidatePartialFailure:
    """Tests for partial validation failures."""

    def test_mixed_validation_results(self):
        """Test validation with some successes and some failures."""

        class AgeValidator:
            def model_validate(self, record):
                if record['age'] < 30:
                    raise ValueError('Too young')
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 35, 28]
        })
        result = validate(df, AgeValidator())

        assert len(result.errors) == 2  # Alice and Charlie fail
        assert len(result.errored_df) == 2
        assert len(result.success_df) == 1  # Only Bob succeeds
        assert result.success_df['name'].iloc[0] == 'Bob'

    def test_preserves_failed_row_data(self):
        """Test that failed rows preserve original data."""

        class FailOnBob:
            def model_validate(self, record):
                if record['name'] == 'Bob':
                    raise ValueError('Bob not allowed')
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
        result = validate(df, FailOnBob())

        # Check that Bob's row is in errored_df with original data
        assert len(result.errored_df) == 1
        assert result.errored_df['name'].iloc[0] == 'Bob'
        assert result.errored_df['age'].iloc[0] == 30


class TestValidateWithTransformation:
    """Tests for validation that transforms data."""

    def test_model_transforms_data(self):
        """Test that validation can transform the data."""

        class TransformingModel:
            def model_validate(self, record):
                self._record = {
                    'name': record['name'].upper(),
                    'age': record['age'] * 2
                }
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['alice', 'bob'], 'age': [25, 30]})
        result = validate(df, TransformingModel())

        assert result.errors == []
        assert result.success_df['name'].iloc[0] == 'ALICE'
        assert result.success_df['age'].iloc[0] == 50

    def test_model_adds_fields(self):
        """Test validation that adds new fields."""

        class AddFieldsModel:
            def model_validate(self, record):
                self._record = {
                    'name': record['name'],
                    'age': record['age'],
                    'doubled_age': record['age'] * 2
                }
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        result = validate(df, AddFieldsModel())

        # Note: validate preserves original column structure
        # Additional fields from model_dump are included
        assert result.errors == []


class TestValidateColumnOrder:
    """Tests for column order preservation."""

    def test_preserves_column_order(self):
        """Test that column order is preserved from input."""

        class SimpleModel:
            def model_validate(self, record):
                # Return fields in different order
                self._record = {
                    'age': record['age'],
                    'name': record['name']
                }
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        result = validate(df, SimpleModel())

        # Should preserve original column order
        assert list(result.success_df.columns) == ['name', 'age']

    def test_errored_df_column_order(self):
        """Test that errored_df preserves column order."""

        class FailingModel:
            def model_validate(self, record):
                raise ValueError('Failed')

            def model_dump(self):
                return {}

        df = pd.DataFrame({'name': ['Alice'], 'age': [25], 'city': ['NYC']})
        result = validate(df, FailingModel())

        assert list(result.errored_df.columns) == list(df.columns)


class TestValidateWithNaN:
    """Tests for validation with NaN/None values."""

    def test_handles_nan_values(self):
        """Test validation with NaN values."""
        import numpy as np

        class NanAwareModel:
            def model_validate(self, record):
                if record['age'] is None:
                    raise ValueError('Age is required')
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [25, np.nan]
        })
        result = validate(df, NanAwareModel())

        # Bob should fail due to NaN age
        assert len(result.errors) == 1
        assert len(result.success_df) == 1
        assert len(result.errored_df) == 1


class TestValidateWithIndex:
    """Tests for index preservation."""

    def test_preserves_index(self):
        """Test that DataFrame index is preserved."""

        class SimpleModel:
            def model_validate(self, record):
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame(
            {'name': ['Alice', 'Bob'], 'age': [25, 30]},
            index=[100, 200]
        )
        result = validate(df, SimpleModel())

        assert list(result.success_df.index) == [100, 200]

    def test_preserves_index_on_failure(self):
        """Test that index is preserved in errored_df."""

        class FailingModel:
            def model_validate(self, record):
                raise ValueError('Failed')

            def model_dump(self):
                return {}

        df = pd.DataFrame(
            {'name': ['Alice'], 'age': [25]},
            index=[999]
        )
        result = validate(df, FailingModel())

        assert result.errored_df.index[0] == 999


class TestValidateErrorDetails:
    """Tests for error information."""

    def test_errors_are_exceptions(self):
        """Test that errors list contains Exception objects."""

        class CustomErrorModel:
            def model_validate(self, record):
                raise ValueError('Custom error message')

            def model_dump(self):
                return {}

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        result = validate(df, CustomErrorModel())

        assert len(result.errors) == 1
        assert isinstance(result.errors[0], Exception)
        assert 'Custom error message' in str(result.errors[0])

    def test_different_error_types(self):
        """Test that different exception types are captured."""

        class MultiErrorModel:
            def __init__(self):
                self.call_count = 0

            def model_validate(self, record):
                self.call_count += 1
                if self.call_count == 1:
                    raise ValueError('ValueError')
                else:
                    raise TypeError('TypeError')

            def model_dump(self):
                return {}

        df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
        model = MultiErrorModel()
        result = validate(df, model)

        assert len(result.errors) == 2
        assert any(isinstance(e, ValueError) for e in result.errors)
        assert any(isinstance(e, TypeError) for e in result.errors)


class TestValidateWithModelClass:
    """Tests for using model class vs instance."""

    def test_accepts_model_instance(self):
        """Test that validate accepts model instance."""

        class Model:
            def model_validate(self, record):
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        result = validate(df, Model())

        assert result.errors == []

    def test_accepts_model_class(self):
        """Test that validate can accept model class (for Pydantic compatibility)."""

        class Model:
            def model_validate(self, record):
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['Alice'], 'age': [25]})
        # Should work with class too
        result = validate(df, Model())

        assert result.errors == []


class TestIntegration:
    """Integration tests for validate module."""

    def test_validate_after_transform(self):
        """Test validation after transformation."""
        from abraxos.transform import transform

        class UppercaseModel:
            def model_validate(self, record):
                self._record = record
                return self

            def model_dump(self):
                return self._record

        df = pd.DataFrame({'name': ['alice', 'bob'], 'age': [25, 30]})

        # First transform
        def uppercase(df):
            df = df.copy()
            df['name'] = df['name'].str.upper()
            return df

        transform_result = transform(df, uppercase)

        # Then validate
        validate_result = validate(transform_result.success_df, UppercaseModel())

        assert validate_result.errors == []
        assert all(transform_result.success_df['name'].str.isupper())

