"""Base provider interface for exchange rate sources."""

from abc import ABC, abstractmethod
from typing import Dict

class RateProvider(ABC):
    """Abstract base class for exchange rate providers."""
    
    @abstractmethod
    def get_rates(self, base_currency: str) -> Dict[str, float]:
        """
        Fetch exchange rates for the base currency.
        
        Args:
            base_currency: The base currency code (e.g., 'USD')
            
        Returns:
            Dictionary mapping currency codes to exchange rates
            
        Raises:
            RateFetchError: If fetching rates fails
            InvalidCurrencyError: If currency code is invalid
        """
        pass
    
    @abstractmethod
    def get_supported_currencies(self) -> set:
        """
        Get set of supported currency codes.
        
        Returns:
            Set of supported currency codes
        """
        pass