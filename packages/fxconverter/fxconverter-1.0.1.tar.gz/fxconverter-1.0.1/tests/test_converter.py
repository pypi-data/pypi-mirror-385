"""Tests for the main CurrencyConverter class."""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from fxconverter import CurrencyConverter
from fxconverter.exceptions import InvalidCurrencyError, RateFetchError


class TestCurrencyConverter:
    """Test suite for CurrencyConverter."""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock rate provider."""
        provider = Mock()
        provider.get_rates.return_value = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'JPY': 110.0
        }
        provider.get_supported_currencies.return_value = {
            'USD', 'EUR', 'GBP', 'JPY'
        }
        return provider
    
    @pytest.fixture
    def converter(self, mock_provider):
        """Create a converter with mocked provider."""
        return CurrencyConverter(provider=mock_provider, cache_ttl=0)
    
    def test_same_currency_conversion(self, converter):
        """Test converting same currency returns same amount."""
        result = converter.convert(100, 'USD', 'USD')
        assert result == Decimal('100.00')
    
    def test_basic_conversion(self, converter):
        """Test basic currency conversion."""
        result = converter.convert(100, 'USD', 'EUR')
        assert result == Decimal('85.00')
    
    def test_conversion_precision(self, converter):
        """Test conversion precision."""
        result = converter.convert(123.456, 'USD', 'EUR')
        # 123.456 * 0.85 = 104.9376 → 104.94
        assert result == Decimal('104.94')
    
    def test_invalid_target_currency(self, converter):
        """Test invalid target currency raises error."""
        with pytest.raises(InvalidCurrencyError):
            converter.convert(100, 'USD', 'XXX')
    
    def test_get_rate(self, converter):
        """Test getting exchange rate."""
        rate = converter.get_rate('USD', 'EUR')
        assert rate == Decimal('0.85')
    
    def test_get_rate_same_currency(self, converter):
        """Test getting rate for same currency."""
        rate = converter.get_rate('USD', 'USD')
        assert rate == Decimal('1.00')
    
    def test_case_insensitive(self, converter):
        """Test currency codes are case insensitive."""
        result1 = converter.convert(100, 'usd', 'eur')
        result2 = converter.convert(100, 'USD', 'EUR')
        assert result1 == result2
    
    def test_cache_is_used(self, mock_provider):
        """Test that cache is used on subsequent calls."""
        converter = CurrencyConverter(provider=mock_provider, cache_ttl=3600)
        
        # First call
        converter.convert(100, 'USD', 'EUR')
        assert mock_provider.get_rates.call_count == 1
        
        # Second call should use cache
        converter.convert(200, 'USD', 'EUR')
        assert mock_provider.get_rates.call_count == 1
    
    def test_cache_bypass(self, mock_provider):
        """Test bypassing cache."""
        converter = CurrencyConverter(provider=mock_provider, cache_ttl=3600)
        
        converter.convert(100, 'USD', 'EUR', use_cache=True)
        converter.convert(100, 'USD', 'EUR', use_cache=False)
        
        assert mock_provider.get_rates.call_count == 2
    
    def test_clear_cache(self, mock_provider):
        """Test clearing cache."""
        converter = CurrencyConverter(provider=mock_provider, cache_ttl=3600)
        
        converter.convert(100, 'USD', 'EUR')
        converter.clear_cache()
        converter.convert(100, 'USD', 'EUR')
        
        assert mock_provider.get_rates.call_count == 2