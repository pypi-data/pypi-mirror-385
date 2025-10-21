"""Main currency converter implementation."""

from typing import Optional
from decimal import Decimal, ROUND_HALF_UP
from fxconverter.cache import RateCache
from fxconverter.providers.base import RateProvider
from fxconverter.providers.exchangerate_api import ExchangeRateAPI
from fxconverter.exceptions import InvalidCurrencyError


class CurrencyConverter:
    """
    Main currency converter class.
    
    Features:
    - Live exchange rates
    - Automatic caching
    - High precision decimal arithmetic
    - Extensible provider system
    
    Example:
        >>> converter = CurrencyConverter()
        >>> result = converter.convert(100, 'USD', 'EUR')
        >>> print(f"Amount: {result}")
    """
    
    def __init__(
        self,
        provider: Optional[RateProvider] = None,
        cache_ttl: int = 3600,
        precision: int = 2
    ):
        """
        Initialize the converter.
        
        Args:
            provider: Exchange rate provider (defaults to ExchangeRateAPI)
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            precision: Decimal places for results (default: 2)
        """
        self._provider = provider or ExchangeRateAPI()
        self._cache = RateCache(ttl=cache_ttl)
        self._precision = precision
    
    def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        use_cache: bool = True
    ) -> Decimal:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
            use_cache: Whether to use cached rates (default: True)
            
        Returns:
            Converted amount as Decimal
            
        Raises:
            InvalidCurrencyError: If currency codes are invalid
            RateFetchError: If fetching rates fails
            
        Example:
            >>> converter.convert(100, 'USD', 'EUR')
            Decimal('85.23')
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Same currency check
        if from_currency == to_currency:
            return self._round_result(Decimal(str(amount)))
        
        # Get rates
        rates = self._get_rates(from_currency, use_cache)
        
        if to_currency not in rates:
            raise InvalidCurrencyError(
                f"Currency '{to_currency}' is not supported"
            )
        
        # Perform conversion using Decimal for precision
        amount_decimal = Decimal(str(amount))
        rate_decimal = Decimal(str(rates[to_currency]))
        result = amount_decimal * rate_decimal
        
        return self._round_result(result)
    
    def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        use_cache: bool = True
    ) -> Decimal:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            use_cache: Whether to use cached rates
            
        Returns:
            Exchange rate as Decimal
            
        Example:
            >>> converter.get_rate('USD', 'EUR')
            Decimal('0.85')
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            return Decimal('1.0')
        
        rates = self._get_rates(from_currency, use_cache)
        
        if to_currency not in rates:
            raise InvalidCurrencyError(
                f"Currency '{to_currency}' is not supported"
            )
        
        return self._round_result(Decimal(str(rates[to_currency])))
    
    def get_supported_currencies(self) -> set:
        """
        Get all supported currency codes.
        
        Returns:
            Set of currency codes
        """
        return self._provider.get_supported_currencies()
    
    def clear_cache(self) -> None:
        """Clear the exchange rate cache."""
        self._cache.clear()
    
    def _get_rates(self, base_currency: str, use_cache: bool) -> dict:
        """Get rates from cache or provider."""
        if use_cache:
            cached = self._cache.get(base_currency)
            if cached is not None:
                return cached
        
        rates = self._provider.get_rates(base_currency)
        self._cache.set(base_currency, rates)
        return rates
    
    def _round_result(self, value: Decimal) -> Decimal:
        """Round result to specified precision."""
        quantize_exp = Decimal(10) ** -self._precision
        return value.quantize(quantize_exp, rounding=ROUND_HALF_UP)