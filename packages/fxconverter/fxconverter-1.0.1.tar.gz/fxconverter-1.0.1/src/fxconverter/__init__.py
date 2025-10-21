"""
fxconverter - A modern currency converter with live exchange rates.

Example:
    >>> from fxconverter import CurrencyConverter
    >>> converter = CurrencyConverter()
    >>> result = converter.convert(100, 'USD', 'EUR')
    >>> print(f"100 USD = {result} EUR")
"""

from fxconverter.__version__ import __version__, __author__, __email__
from fxconverter.converter import CurrencyConverter
from fxconverter.exceptions import (
    FxConverterError,
    InvalidCurrencyError,
    RateFetchError,
    CacheError
)

__all__ = [
    'CurrencyConverter',
    'FxConverterError',
    'InvalidCurrencyError',
    'RateFetchError',
    'CacheError',
    '__version__'
]