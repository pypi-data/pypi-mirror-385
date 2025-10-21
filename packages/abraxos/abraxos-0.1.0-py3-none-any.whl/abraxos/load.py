"""SQL loading utilities with error handling and retry logic."""

from __future__ import annotations

import typing as t
from collections.abc import Iterable
from typing import Literal

import pandas as pd

from abraxos import utils

__all__ = ['SqlInsert', 'SqlConnection', 'SqlEngine', 'ToSqlResult', 'to_sql', 'use_sql']


class SqlInsert(t.Protocol):
    """
    Protocol for a SQL insert statement object (e.g., sqlalchemy.Insert).
    """
    ...


class SqlConnection(t.Protocol):
    """
    Protocol for a database connection that supports executing insert statements.
    """

    def execute(
        self,
        insert: SqlInsert,
        records: Iterable[dict]
    ) -> None:
        """
        Execute an insert statement with given records.
        """
        ...


class SqlEngine(t.Protocol):
    """
    Protocol for a database engine object that can provide connections.
    """

    def connect(self) -> SqlConnection:
        """
        Obtain a SQL connection from the engine.
        """
        ...


class ToSqlResult(t.NamedTuple):
    """
    Result of inserting a DataFrame into a database.

    Attributes
    ----------
    errors : list of Exception
        Exceptions encountered during insertion.
    errored_df : pandas.DataFrame
        Rows that failed to be inserted.
    success_df : pandas.DataFrame
        Rows that were successfully inserted.
    """
    errors: list[Exception]
    errored_df: pd.DataFrame
    success_df: pd.DataFrame


def to_sql(
    df: pd.DataFrame,
    name: str,
    con: SqlConnection | SqlEngine,
    *,
    if_exists: Literal['fail', 'replace', 'append'] = 'append',
    index: bool = False,
    chunks: int = 2,
    **kwargs: t.Any
) -> ToSqlResult:
    """
    Writes a DataFrame to a SQL database table with error handling.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to insert.
    name : str
        Name of the target table.
    con : SqlConnection or SqlEngine
        SQLAlchemy-like connection or engine object.
    if_exists : {'fail', 'replace', 'append'}, optional
        SQL behavior if the table already exists (default is 'append').
    index : bool, optional
        Whether to include the DataFrame index in the output (default is False).
    chunks : int, optional
        Number of chunks to recursively split on failure (default is 2).
    **kwargs
        Additional arguments passed to `pandas.DataFrame.to_sql`.

    Returns
    -------
    ToSqlResult
        A named tuple with lists of errors, failed rows, and successful rows.
    """
    errors: list[Exception] = []
    errored_dfs: list[pd.DataFrame] = [utils.clear(df)]
    success_dfs: list[pd.DataFrame] = [utils.clear(df)]

    try:
        df.to_sql(name, con, if_exists=if_exists, index=index, method='multi', **kwargs)
        return ToSqlResult([], utils.clear(df), df)
    except Exception:
        if len(df) > 1:
            for df_chunk in utils.split(df, chunks):
                result: ToSqlResult = to_sql(
                    df_chunk,
                    name, con,
                    if_exists=if_exists,
                    index=index,
                    chunks=chunks,
                    **kwargs
                )
                errors.extend(result.errors)
                errored_dfs.append(result.errored_df)
                success_dfs.append(result.success_df)
        else:
            try:
                df.to_sql(name, con, if_exists=if_exists, index=index, method='multi', **kwargs)
                return ToSqlResult([], utils.clear(df), df)
            except Exception as e:
                return ToSqlResult([e], df, utils.clear(df))

    return ToSqlResult(errors, pd.concat(errored_dfs), pd.concat(success_dfs))


def insert_df(
    df: pd.DataFrame,
    connection: SqlConnection,
    sql_query: SqlInsert
) -> ToSqlResult:
    """
    Inserts a DataFrame into a database using a raw SQL insert statement.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to insert.
    connection : SqlConnection
        A SQL connection object with an `execute` method.
    sql_query : SqlInsert
        A SQLAlchemy-compatible insert statement.

    Returns
    -------
    ToSqlResult
        A result containing successful and errored inserts.
    """
    records: list[dict] = utils.to_records(df)
    connection.execute(sql_query, records)
    return ToSqlResult([], utils.clear(df), df)


def use_sql(
    df: pd.DataFrame,
    connection: SqlConnection,
    sql_query: SqlInsert,
    chunks: int = 2
) -> ToSqlResult:
    """
    Executes user-provided SQL insert using `insert_df` with error handling.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to insert.
    connection : SqlConnection
        SQL connection object.
    sql_query : SqlInsert
        SQL insert statement object.
    chunks : int, optional
        Number of chunks to split on failure (default is 2).

    Returns
    -------
    ToSqlResult
        A result indicating which rows succeeded and which failed.
    """
    errors: list[Exception] = []
    errored_dfs: list[pd.DataFrame] = [utils.clear(df)]
    success_dfs: list[pd.DataFrame] = [utils.clear(df)]

    try:
        return insert_df(df, connection, sql_query)
    except Exception:
        if len(df) > 1:
            for df_chunk in utils.split(df, chunks):
                result: ToSqlResult = use_sql(df_chunk, connection, sql_query, chunks)
                errors.extend(result.errors)
                errored_dfs.append(result.errored_df)
                success_dfs.append(result.success_df)
        else:
            try:
                return insert_df(df, connection, sql_query)
            except Exception as e:
                return ToSqlResult([e], df, utils.clear(df))

    return ToSqlResult(
        errors,
        pd.concat(errored_dfs),
        pd.concat(success_dfs)
    )
