"""DataFrame transformation with error isolation."""

from __future__ import annotations

import collections.abc as a
import typing as t

import pandas as pd

from abraxos import utils

__all__ = ['TransformResult', 'transform']


class TransformResult(t.NamedTuple):
    """
    Result of applying a transformation to a DataFrame.

    Attributes
    ----------
    errors : list of Exception
        Exceptions raised during transformation.
    errored_df : pandas.DataFrame
        Rows that failed to transform.
    success_df : pandas.DataFrame
        Successfully transformed rows.
    """
    errors: list[Exception]
    errored_df: pd.DataFrame
    success_df: pd.DataFrame


def transform(
    df: pd.DataFrame,
    transformer: a.Callable[[pd.DataFrame], pd.DataFrame],
    chunks: int = 2
) -> TransformResult:
    """
    Applies a transformation function to a DataFrame with error isolation.

    If the transformation raises an exception on a chunk, the DataFrame
    is split into smaller chunks recursively to isolate errors. Ultimately,
    rows that fail even as single-row DataFrames are collected separately.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame to transform.
    transformer : Callable[[pd.DataFrame], pd.DataFrame]
        A function that transforms a DataFrame and returns a new DataFrame.
    chunks : int, optional
        Number of subchunks to divide the DataFrame into if transformation fails (default is 2).

    Returns
    -------
    TransformResult
        A named tuple with:
        - errors: A list of exceptions that occurred during transformation.
        - errored_df: A DataFrame of rows that could not be transformed.
        - success_df: A DataFrame of successfully transformed rows.

    Examples
    --------
    >>> import pandas as pd
    >>> def double_values(df): return df.assign(value=df['value'] * 2)
    >>> df = pd.DataFrame({'value': [1, 2, 3]})
    >>> result = transform(df, double_values)
    >>> result.success_df
       value
    0      2
    1      4
    2      6
    >>> result.errored_df.empty
    True
    """
    errors: list[Exception] = []
    errored_dfs: list[pd.DataFrame] = []
    success_dfs: list[pd.DataFrame] = []

    try:
        return TransformResult([], utils.clear(df), transformer(df))
    except Exception:
        if len(df) > 1:
            for df_c in utils.split(df, chunks):
                result: TransformResult = transform(df_c, transformer, chunks)
                errors.extend(result.errors)
                errored_dfs.append(result.errored_df)
                success_dfs.append(result.success_df)
        else:
            try:
                return TransformResult([], utils.clear(df), transformer(df))
            except Exception as e:
                return TransformResult([e], df, utils.clear(df))

    return TransformResult(
        errors,
        pd.concat(errored_dfs),
        pd.concat(success_dfs)
    )
