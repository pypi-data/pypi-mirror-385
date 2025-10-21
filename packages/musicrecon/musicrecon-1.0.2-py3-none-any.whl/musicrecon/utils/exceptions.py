"""
Custom exceptions for the dotflow package.
"""


class MusicRecon(Exception):
    """Base exception for all dotflow errors."""

    pass


class ValidationError(MusicRecon):
    """Raised when validation fails."""

    pass


class SystemError(MusicRecon):
    """Raised os related error."""

    pass


class SystemValidationError(MusicRecon):
    """Raised when system validation fails eg Permission error or Graphiz missing."""

    pass


class SecretsError(MusicRecon):
    """Raised when secrets manager encounters error"""

    pass


class InvalidConfigurationError(MusicRecon):
    """Raised when configuration is invalid."""

    pass
