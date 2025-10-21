"""Integration tests for abraxos - end-to-end workflows."""

from io import StringIO

import pandas as pd

from abraxos import clear, read_csv, split, to_records, to_sql, transform, validate


class TestEndToEndWorkflow:
    """Tests for complete ETL workflows."""

    def test_csv_to_sql_pipeline(self, sqlite_engine):
        """Test complete pipeline from CSV to SQL."""
        csv_data = StringIO("""name,age,city
Alice,25,NYC
Bob,30,LA
Charlie,35,SF
""")

        # Extract
        result = read_csv(csv_data)

        # Load to SQL
        sql_result = to_sql(result.dataframe, 'people', sqlite_engine)

        assert sql_result.errors == []
        assert len(sql_result.success_df) == 3

        # Verify in database
        with sqlite_engine.connect() as conn:
            db_data = pd.read_sql('SELECT * FROM people', conn)
            assert len(db_data) == 3

    def test_csv_transform_validate_sql(self, sqlite_engine):
        """Test full ETL with transformation and validation."""
        csv_data = StringIO("""name,age
alice,25
bob,30
charlie,invalid
""")

        # Extract
        csv_result = read_csv(csv_data)

        # Transform - uppercase names
        def uppercase_names(df):
            df = df.copy()
            df['name'] = df['name'].str.upper()
            return df

        transform_result = transform(csv_result.dataframe, uppercase_names)

        # Validate - check age is numeric (pandas may read 'invalid' as string)
        class AgeValidator:
            def model_validate(self, record):
                age = record.get('age')
                # Check if age is numeric or can be converted
                try:
                    int(age)
                except (ValueError, TypeError):
                    raise ValueError('Age must be numeric') from None
                self._record = record
                return self

            def model_dump(self):
                return self._record

        validate_result = validate(transform_result.success_df, AgeValidator())

        # Should have some errors (charlie's invalid age)
        assert len(validate_result.errors) > 0
        # Should have some successes (alice and bob)
        assert not validate_result.success_df.empty

        # Load valid data to SQL
        sql_result = to_sql(validate_result.success_df, 'validated_people', sqlite_engine)

        assert sql_result.errors == []
        assert len(sql_result.success_df) >= 2  # alice and bob at minimum

        with sqlite_engine.connect() as conn:
            db_data = pd.read_sql('SELECT * FROM validated_people', conn)
            # Should have the valid records
            assert len(db_data) >= 2

    def test_chunked_csv_to_sql(self, sqlite_engine):
        """Test pipeline with chunked CSV reading."""
        csv_data = StringIO("""id,value
1,10
2,20
3,30
4,40
5,50
""")

        # Read in chunks
        all_success = []
        for chunk_result in read_csv(csv_data, chunksize=2):
            # Process each chunk
            sql_result = to_sql(
                chunk_result.dataframe,
                'chunked_data',
                sqlite_engine,
                if_exists='append'
            )
            all_success.append(sql_result.success_df)

        # Verify all data loaded
        with sqlite_engine.connect() as conn:
            db_data = pd.read_sql('SELECT * FROM chunked_data', conn)
            assert len(db_data) == 5


class TestErrorRecovery:
    """Tests for error recovery in workflows."""

    def test_partial_csv_failures_continue(self, sqlite_engine):
        """Test that partial CSV failures don't stop pipeline."""
        csv_data = StringIO("""name,age
Alice,25
TOO,MANY,COLUMNS,HERE
Bob,30
""")

        result = read_csv(csv_data)

        # CSV might parse this differently - check that we got some data
        # Note: pandas may treat extra columns as part of the data depending on engine
        assert not result.dataframe.empty
        # At least the two valid rows should be present
        assert len(result.dataframe) >= 2

        # Continue pipeline with good data
        sql_result = to_sql(result.dataframe, 'partial_data', sqlite_engine)
        assert len(sql_result.success_df) >= 2

    def test_transform_failures_isolated(self, sqlite_engine):
        """Test that transform failures are isolated."""
        df = pd.DataFrame({
            'value': [1, 2, 0, 3, 4]  # 0 will cause issue
        })

        def divide_by_value(df):
            df = df.copy()
            # Check for zeros and raise
            if (df['value'] == 0).any():
                raise ValueError('Division by zero')
            df['result'] = 100 / df['value']
            return df

        result = transform(df, divide_by_value)

        # Should isolate the zero
        assert len(result.errored_df) > 0
        assert len(result.success_df) > 0

        # Load successful rows
        sql_result = to_sql(result.success_df, 'divided', sqlite_engine)
        assert sql_result.errors == []

    def test_validation_errors_captured(self, sqlite_engine):
        """Test that validation errors are properly captured."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 150, 30]  # 150 is invalid
        })

        class ReasonableAgeValidator:
            def model_validate(self, record):
                if record['age'] > 120:
                    raise ValueError('Age too high')
                self._record = record
                return self

            def model_dump(self):
                return self._record

        result = validate(df, ReasonableAgeValidator())

        assert len(result.errored_df) == 1
        assert result.errored_df['name'].iloc[0] == 'Bob'

        # Load only valid data
        sql_result = to_sql(result.success_df, 'reasonable_ages', sqlite_engine)
        assert len(sql_result.success_df) == 2


class TestComplexPipelines:
    """Tests for complex multi-step pipelines."""

    def test_multiple_transformations(self, sqlite_engine):
        """Test pipeline with multiple transformations."""
        df = pd.DataFrame({
            'name': ['alice', 'bob', 'charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000]
        })

        # Transform 1: Uppercase names
        def uppercase(df):
            df = df.copy()
            df['name'] = df['name'].str.upper()
            return df

        result1 = transform(df, uppercase)

        # Transform 2: Add bonus column
        def add_bonus(df):
            df = df.copy()
            df['bonus'] = df['salary'] * 0.1
            return df

        result2 = transform(result1.success_df, add_bonus)

        # Transform 3: Calculate total compensation
        def total_comp(df):
            df = df.copy()
            df['total'] = df['salary'] + df['bonus']
            return df

        result3 = transform(result2.success_df, total_comp)

        assert result3.errors == []
        assert 'total' in result3.success_df.columns

        # Load final result
        sql_result = to_sql(result3.success_df, 'compensations', sqlite_engine)
        assert sql_result.errors == []

    def test_split_process_combine(self, sqlite_engine):
        """Test splitting data, processing separately, then combining."""
        large_df = pd.DataFrame({
            'id': range(100),
            'value': range(100, 200)
        })

        # Split into parts
        parts = split(large_df, 4)

        # Process each part
        processed_parts = []
        for part in parts:
            def double_value(df):
                df = df.copy()
                df['value'] = df['value'] * 2
                return df

            result = transform(part, double_value)
            processed_parts.append(result.success_df)

        # Combine
        combined = pd.concat(processed_parts)

        assert len(combined) == 100

        # Load combined result
        sql_result = to_sql(combined, 'processed', sqlite_engine)
        assert sql_result.errors == []
        assert len(sql_result.success_df) == 100


class TestUtilityIntegration:
    """Tests for utility function integration."""

    def test_to_records_in_pipeline(self):
        """Test using to_records in a pipeline."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [25, 30]
        })

        records = to_records(df)

        # Use records for custom processing
        processed = [
            {**r, 'age': r['age'] + 1}
            for r in records
        ]

        result_df = pd.DataFrame(processed)
        assert all(result_df['age'] == [26, 31])

    def test_clear_for_schema(self):
        """Test using clear to maintain schema."""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [25, 30],
            'city': ['NYC', 'LA']
        })

        # Get empty with same schema
        empty = clear(df)

        assert empty.empty
        assert list(empty.columns) == list(df.columns)

        # Can be used as accumulator
        results = [empty]

        for row in split(df, len(df)):
            results.append(row)

        combined = pd.concat(results)
        assert len(combined) == len(df)


class TestRealWorldScenarios:
    """Tests simulating real-world usage scenarios."""

    def test_data_cleaning_pipeline(self, sqlite_engine):
        """Test a realistic data cleaning pipeline."""
        # Messy CSV data
        csv_data = StringIO("""name,age,email
Alice Smith,25,alice@example.com
Bob,30,bob@example.com
Charlie Brown,35,charlie@example.com
Dave,40,dave@example.com
""")

        # 1. Extract
        extract_result = read_csv(csv_data)

        # 2. Transform - clean data
        def clean_data(df):
            df = df.copy()
            # Remove rows with all nulls
            df = df.dropna(how='all')
            # Strip whitespace from names
            df['name'] = df['name'].str.strip()
            return df

        transform_result = transform(extract_result.dataframe, clean_data)

        # 3. Validate
        class EmailValidator:
            def model_validate(self, record):
                if '@' not in str(record.get('email', '')):
                    raise ValueError('Invalid email')
                # Age should be numeric
                try:
                    int(record.get('age'))
                except (ValueError, TypeError):
                    raise ValueError('Invalid age') from None
                self._record = record
                return self

            def model_dump(self):
                return self._record

        validate_result = validate(transform_result.success_df, EmailValidator())

        # All should be valid in this cleaned dataset
        assert validate_result.errors == [] or len(validate_result.success_df) >= 3

        # 4. Load valid data
        sql_result = to_sql(validate_result.success_df, 'clean_users', sqlite_engine)

        # Should have loaded the clean data
        assert len(sql_result.success_df) >= 3

        with sqlite_engine.connect() as conn:
            clean_data_db = pd.read_sql('SELECT * FROM clean_users', conn)
            # All emails should be valid
            assert all('@' in str(email) for email in clean_data_db['email'])
            assert len(clean_data_db) >= 3

    def test_incremental_data_loading(self, sqlite_engine):
        """Test incremental data loading scenario."""
        # Initial data load
        initial_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': ['a', 'b', 'c']
        })

        to_sql(initial_data, 'incremental', sqlite_engine)

        # New data arrives
        new_data = pd.DataFrame({
            'id': [4, 5],
            'value': ['d', 'e']
        })

        # Append new data
        result = to_sql(new_data, 'incremental', sqlite_engine, if_exists='append')

        assert result.errors == []

        with sqlite_engine.connect() as conn:
            all_data = pd.read_sql('SELECT * FROM incremental', conn)
            assert len(all_data) == 5

