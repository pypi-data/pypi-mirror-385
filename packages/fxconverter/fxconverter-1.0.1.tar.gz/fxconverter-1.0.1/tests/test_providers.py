"""Tests for exchange rate providers."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fxconverter.providers.exchangerate_api import ExchangeRateAPI
from fxconverter.exceptions import RateFetchError, InvalidCurrencyError


class TestExchangeRateAPI:
    """Test suite for ExchangeRateAPI provider."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return ExchangeRateAPI(timeout=10)
    
    @pytest.fixture
    def mock_success_response(self):
        """Mock successful API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': 'success',
            'rates': {
                'USD': 1.0,
                'EUR': 0.85,
                'GBP': 0.73,
                'JPY': 110.0
            }
        }
        return mock_response
    
    @pytest.fixture
    def mock_error_response(self):
        """Mock error API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': 'error',
            'error-type': 'unsupported-code'
        }
        return mock_response
    
    def test_initialization(self, provider):
        """Test provider initialization."""
        assert provider._timeout == 10
        assert provider._supported_currencies is None
        assert provider.BASE_URL == "https://open.exchangerate-api.com/v6/latest"
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_success(self, mock_get, provider, mock_success_response):
        """Test successful rate fetching."""
        mock_get.return_value = mock_success_response
        
        rates = provider.get_rates('USD')
        
        assert rates == {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'JPY': 110.0
        }
        mock_get.assert_called_once()
        assert 'USD' in mock_get.call_args[0][0]
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_uppercase_conversion(self, mock_get, provider, mock_success_response):
        """Test that currency codes are converted to uppercase."""
        mock_get.return_value = mock_success_response
        
        rates = provider.get_rates('usd')
        
        assert rates is not None
        # Verify the URL contains uppercase USD
        called_url = mock_get.call_args[0][0]
        assert 'USD' in called_url
        assert 'usd' not in called_url
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_api_error(self, mock_get, provider, mock_error_response):
        """Test handling of API error responses."""
        mock_get.return_value = mock_error_response
        
        with pytest.raises(RateFetchError) as exc_info:
            provider.get_rates('USD')
        
        assert 'API returned error' in str(exc_info.value)
        assert 'unsupported-code' in str(exc_info.value)
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_http_404(self, mock_get, provider):
        """Test handling of HTTP 404 errors (invalid currency)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        from requests.exceptions import HTTPError
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        
        with pytest.raises(InvalidCurrencyError) as exc_info:
            provider.get_rates('XXX')
        
        assert 'not supported' in str(exc_info.value)
        assert 'XXX' in str(exc_info.value)
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_http_error(self, mock_get, provider):
        """Test handling of general HTTP errors."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(RateFetchError) as exc_info:
            provider.get_rates('USD')
        
        assert 'HTTP error' in str(exc_info.value)
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_network_error(self, mock_get, provider):
        """Test handling of network errors."""
        from requests.exceptions import RequestException
        
        mock_get.side_effect = RequestException("Connection timeout")
        
        with pytest.raises(RateFetchError) as exc_info:
            provider.get_rates('USD')
        
        assert 'Network error' in str(exc_info.value)
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_invalid_json(self, mock_get, provider):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(RateFetchError) as exc_info:
            provider.get_rates('USD')
        
        assert 'Invalid JSON response' in str(exc_info.value)
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_timeout(self, mock_get, provider):
        """Test that timeout parameter is used."""
        from requests.exceptions import Timeout
        
        mock_get.side_effect = Timeout("Request timeout")
        
        with pytest.raises(RateFetchError):
            provider.get_rates('USD')
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_supported_currencies_success(self, mock_get, provider, mock_success_response):
        """Test getting supported currencies."""
        mock_get.return_value = mock_success_response
        
        currencies = provider.get_supported_currencies()
        
        assert isinstance(currencies, set)
        assert 'USD' in currencies
        assert 'EUR' in currencies
        assert 'GBP' in currencies
        assert 'JPY' in currencies
        assert len(currencies) == 4
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_supported_currencies_cached(self, mock_get, provider, mock_success_response):
        """Test that supported currencies are cached."""
        mock_get.return_value = mock_success_response
        
        # First call
        currencies1 = provider.get_supported_currencies()
        # Second call should use cached value
        currencies2 = provider.get_supported_currencies()
        
        assert currencies1 == currencies2
        # Should only call API once
        assert mock_get.call_count == 1
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_supported_currencies_fallback(self, mock_get, provider):
        """Test fallback currencies when API fails."""
        mock_get.side_effect = Exception("API error")
        
        currencies = provider.get_supported_currencies()
        
        # Should return fallback currencies
        assert isinstance(currencies, set)
        assert len(currencies) >= 8
        assert 'USD' in currencies
        assert 'EUR' in currencies
        assert 'GBP' in currencies
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_with_custom_timeout(self, mock_get, mock_success_response):
        """Test custom timeout parameter."""
        mock_get.return_value = mock_success_response
        
        provider = ExchangeRateAPI(timeout=5)
        provider.get_rates('USD')
        
        # Verify timeout was passed to requests.get
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs['timeout'] == 5
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_empty_rates(self, mock_get, provider):
        """Test handling of empty rates in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': 'success',
            'rates': {}
        }
        mock_get.return_value = mock_response
        
        rates = provider.get_rates('USD')
        
        assert rates == {}
    
    @patch('fxconverter.providers.exchangerate_api.requests.get')
    def test_get_rates_missing_rates_key(self, mock_get, provider):
        """Test handling of missing 'rates' key in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': 'success'
        }
        mock_get.return_value = mock_response
        
        rates = provider.get_rates('USD')
        
        # Should return empty dict when 'rates' key is missing
        assert rates == {}


class TestRateProviderInterface:
    """Test the abstract base provider interface."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that RateProvider cannot be instantiated directly."""
        from fxconverter.providers.base import RateProvider
        
        with pytest.raises(TypeError):
            RateProvider()
    
    def test_custom_provider_implementation(self):
        """Test implementing a custom provider."""
        from fxconverter.providers.base import RateProvider
        
        class CustomProvider(RateProvider):
            def get_rates(self, base_currency: str):
                return {'EUR': 0.85, 'GBP': 0.73}
            
            def get_supported_currencies(self):
                return {'USD', 'EUR', 'GBP'}
        
        provider = CustomProvider()
        rates = provider.get_rates('USD')
        currencies = provider.get_supported_currencies()
        
        assert rates == {'EUR': 0.85, 'GBP': 0.73}
        assert currencies == {'USD', 'EUR', 'GBP'}


class TestProviderIntegration:
    """Integration tests with real API (optional, can be skipped)."""
    
    @pytest.mark.skip(reason="Requires internet connection and hits real API")
    def test_real_api_call(self):
        """Test actual API call (skipped by default)."""
        provider = ExchangeRateAPI()
        rates = provider.get_rates('USD')
        
        assert isinstance(rates, dict)
        assert len(rates) > 0
        assert 'EUR' in rates
        assert all(isinstance(v, (int, float)) for v in rates.values())
    
    @pytest.mark.skip(reason="Requires internet connection")
    def test_real_supported_currencies(self):
        """Test getting real supported currencies."""
        provider = ExchangeRateAPI()
        currencies = provider.get_supported_currencies()
        
        assert isinstance(currencies, set)
        assert len(currencies) > 100  # Should have many currencies