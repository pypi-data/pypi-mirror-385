"""Utility functions for DataFrame operations."""

from __future__ import annotations

import typing as t

import numpy as np
import pandas as pd

__all__ = ['split', 'clear', 'to_records']


def split(
    df: pd.DataFrame,
    i: int = 2
) -> tuple[pd.DataFrame, ...]:
    """
    Splits a DataFrame into `i` approximately equal parts.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be split.
    i : int, optional
        The number of parts to split the DataFrame into (default is 2).

    Returns
    -------
    tuple of pd.DataFrame
        A tuple containing `i` DataFrames, each being a partition of the original DataFrame.

    Examples
    --------
    >>> import pandas as pd
    >>> import abraxos
    >>> df = pd.DataFrame({'A': range(10)})
    >>> abraxos.split(df, 3)
    (   A
    0  0
    1  1
    2  2
    3  3,
       A
    4  4
    5  5
    6  6,
       A
    7  7
    8  8
    9  9)
    """
    return tuple(map(pd.DataFrame, np.array_split(df, i)))


def clear(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns an empty DataFrame with the same schema (columns and dtypes) as the input.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.

    Returns
    -------
    pd.DataFrame
        An empty DataFrame with the same structure as `df`.

    Examples
    --------
    >>> df = pd.DataFrame({'x': [1, 2, 3]})
    >>> clear(df)
    Empty DataFrame
    Columns: [x]
    Index: []
    """
    return df.iloc[:0]


def to_records(df: pd.DataFrame) -> list[dict[t.Any, t.Any]]:
    """
    Converts a DataFrame to a list of record dictionaries, replacing NaN with None.

    This is useful for inserting into databases that expect `None` for nulls.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to convert.

    Returns
    -------
    list of dict
        A list of records (dicts), where each dict is a row in the DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame({'a': [1, None], 'b': ['x', 'y']})
    >>> to_records(df)
    [{'a': 1.0, 'b': 'x'}, {'a': None, 'b': 'y'}]
    """
    df = df.fillna(np.nan).replace(np.nan, None)
    return df.to_dict('records')  # type: ignore[no-any-return]
