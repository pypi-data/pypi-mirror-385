"""
Custom exceptions for the dotflow package.
"""


class DotFlowError(Exception):
    """Base exception for all dotflow errors."""

    pass


class ValidationError(DotFlowError):
    """Raised when validation fails."""

    pass


class SystemValidationError(DotFlowError):
    """Raised when system validation fails eg Permission error or Graphiz missing."""

    pass


class NodeNotFoundError(DotFlowError):
    """Raised when a referenced node is not found."""

    pass


class DSLParseError(DotFlowError):
    """Raised when DSL parsing fails."""

    pass


class ExportError(DotFlowError):
    """Raised when export operations fail."""

    pass


class InvalidConfigurationError(DotFlowError):
    """Raised when configuration is invalid."""

    pass


class ThemeError(DotFlowError):
    """Raised when theme operations fail."""

    pass
