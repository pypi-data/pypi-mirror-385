"""Pydantic model validation for DataFrame rows."""

from __future__ import annotations

import typing as t

import pandas as pd

from abraxos import utils

__all__ = ['PydanticModel', 'ValidateResult', 'validate']


class PydanticModel(t.Protocol):
    """
    Protocol representing a Pydantic-like model for validation and serialization.
    """

    def model_validate(self, record: dict[t.Any, t.Any]) -> PydanticModel:
        """
        Validates a dictionary record and returns a validated model instance.
        """
        ...

    def model_dump(self) -> dict:
        """
        Serializes the model into a dictionary.
        """
        ...


class ValidateResult(t.NamedTuple):
    """
    Result of validating a DataFrame using a Pydantic-like model.

    Attributes
    ----------
    errors : list of Exception
        List of exceptions encountered during validation.
    errored_df : pd.DataFrame
        DataFrame of rows that failed validation.
    success_df : pd.DataFrame
        DataFrame of successfully validated and serialized rows.
    """
    errors: list[Exception]
    errored_df: pd.DataFrame
    success_df: pd.DataFrame


def validate(
    df: pd.DataFrame,
    model: type[PydanticModel] | PydanticModel
) -> ValidateResult:
    """
    Validates each row in a DataFrame using a Pydantic-like model.

    Each record is passed to the model's `model_validate` method.
    Successfully validated models are converted back into rows using `model_dump`.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing records to be validated.
    model : type[PydanticModel] or PydanticModel
        A Pydantic-style model class or instance with `model_validate` and `model_dump` methods.

    Returns
    -------
    ValidateResult
        A named tuple with:
        - errors: List of exceptions raised during validation.
        - errored_df: DataFrame of rows that failed validation.
        - success_df: DataFrame of rows that were successfully validated.

    Examples
    --------
    >>> import pandas as pd
    >>> from pydantic import BaseModel
    >>> class Person(BaseModel):
    ...     name: str
    ...     age: int
    >>> df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [30, 'invalid']})
    >>> result = validate(df, Person)
    >>> len(result.success_df)
    1
    >>> len(result.errored_df)
    1
    """
    errors: list[Exception] = []
    errored_records: list[pd.Series] = []
    valid_records: list[pd.Series] = []

    records: list[dict] = utils.to_records(df)

    for index, record in zip(df.index, records):
        try:
            validated: PydanticModel = model.model_validate(record)  # type: ignore[call-arg, arg-type]
            valid_records.append(pd.Series(validated.model_dump(), name=index))
        except Exception as e:
            errors.append(e)
            errored_records.append(pd.Series(record, name=index))

    errored_df = pd.DataFrame(errored_records)
    success_df = pd.DataFrame(valid_records)

    # Ensure column order matches input DataFrame
    errored_df = errored_df[df.columns] if not errored_df.empty else utils.clear(df)
    success_df = success_df[df.columns] if not success_df.empty else utils.clear(df)

    return ValidateResult(errors, errored_df, success_df)
