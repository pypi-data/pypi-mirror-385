# src/exceptions.py

class ReduMetricsError(Exception):
    """Base class for ReduMetrics exceptions."""


class InvalidShapeError(ReduMetricsError):
    """Raised when input arrays have invalid shapes or ranks."""


class InconsistentDimensionsError(ReduMetricsError):
    """Raised when X_high and X_low have different number of samples."""


class InvalidKError(ReduMetricsError):
    """Raised when k is not in the valid range [1, m-1]."""


class NaNInputError(ReduMetricsError):
    """Raised when inputs contain NaN or infinite values."""


class UnsupportedMetricError(ReduMetricsError):
    """Raised when a distance metric or backend is not supported."""
