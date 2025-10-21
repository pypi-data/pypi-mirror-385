"""Exchange rate provider using exchangerate-api.com free tier."""

import requests
from typing import Dict
from fxconverter.providers.base import RateProvider
from fxconverter.exceptions import RateFetchError, InvalidCurrencyError


class ExchangeRateAPI(RateProvider):
    """Provider using exchangerate-api.com (free tier, no API key required)."""
    
    BASE_URL = "https://open.exchangerate-api.com/v6/latest"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the provider.
        
        Args:
            timeout: Request timeout in seconds
        """
        self._timeout = timeout
        self._supported_currencies = None
    
    def get_rates(self, base_currency: str) -> Dict[str, float]:
        """
        Fetch exchange rates from exchangerate-api.com.
        
        Args:
            base_currency: Base currency code
            
        Returns:
            Dictionary of exchange rates
            
        Raises:
            RateFetchError: If API request fails
            InvalidCurrencyError: If currency is not supported
        """
        base_currency = base_currency.upper()
        
        try:
            url = f"{self.BASE_URL}/{base_currency}"
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') != 'success':
                raise RateFetchError(
                    f"API returned error: {data.get('error-type', 'Unknown error')}"
                )
            
            return data.get('rates', {})
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise InvalidCurrencyError(
                    f"Currency '{base_currency}' is not supported"
                )
            raise RateFetchError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise RateFetchError(f"Network error: {e}")
        except ValueError as e:
            raise RateFetchError(f"Invalid JSON response: {e}")
    
    def get_supported_currencies(self) -> set:
        """
        Get supported currencies by fetching USD rates.
        
        Returns:
            Set of currency codes
        """
        if self._supported_currencies is None:
            try:
                rates = self.get_rates('USD')
                self._supported_currencies = set(rates.keys())
            except Exception:
                # Fallback to common currencies
                self._supported_currencies = {
                    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD'
                }
        
        return self._supported_currencies