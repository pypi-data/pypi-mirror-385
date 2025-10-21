"""Abraxos: A lightweight Python toolkit for robust data processing with Pandas and Pydantic."""

from __future__ import annotations

__version__ = '0.1.0'

from .exceptions import AbraxosError, LoadError, TransformError, ValidationError
from .extract import ReadCsvResult, read_csv, read_csv_chunks
from .load import ToSqlResult, to_sql, use_sql
from .transform import TransformResult, transform
from .utils import clear, split, to_records
from .validate import ValidateResult, validate

__all__ = [
    # Version
    '__version__',
    # Extract
    'read_csv',
    'read_csv_chunks',
    'ReadCsvResult',
    # Transform
    'transform',
    'TransformResult',
    # Load
    'to_sql',
    'use_sql',
    'ToSqlResult',
    # Validate
    'validate',
    'ValidateResult',
    # Utils
    'split',
    'clear',
    'to_records',
    # Exceptions
    'AbraxosError',
    'TransformError',
    'ValidationError',
    'LoadError',
]
