"""Custom exceptions for the abraxos package."""

from __future__ import annotations


class AbraxosError(Exception):
    """Base exception for all abraxos errors."""
    pass


class TransformError(AbraxosError):
    """Exception raised when DataFrame transformation fails."""
    pass


class ValidationError(AbraxosError):
    """Exception raised when row validation fails."""
    pass


class LoadError(AbraxosError):
    """Exception raised when loading data to SQL fails."""
    pass


__all__ = ['AbraxosError', 'TransformError', 'ValidationError', 'LoadError']

