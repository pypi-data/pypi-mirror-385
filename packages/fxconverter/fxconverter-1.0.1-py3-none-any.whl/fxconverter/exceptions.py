"""Custom exceptions for the fxconverter package."""

class FxConverterError(Exception):
    """Base exception for all fxconverter errors."""
    pass


class InvalidCurrencyError(FxConverterError):
    """Raised when an invalid currency code is provided."""
    pass


class RateFetchError(FxConverterError):
    """Raised when fetching exchange rates fails."""
    pass


class CacheError(FxConverterError):
    """Raised when cache operations fail."""
    pass