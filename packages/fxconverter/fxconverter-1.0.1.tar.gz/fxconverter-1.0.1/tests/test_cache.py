"""Tests for the cache module."""

import pytest
import time
from fxconverter.cache import RateCache


class TestRateCache:
    """Test suite for RateCache."""
    
    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = RateCache(ttl=3600)
        rates = {'EUR': 0.85, 'GBP': 0.73}
        
        cache.set('USD', rates)
        result = cache.get('USD')
        
        assert result == rates
    
    def test_get_nonexistent(self):
        """Test getting non-existent key."""
        cache = RateCache()
        assert cache.get('USD') is None
    
    def test_ttl_expiration(self):
        """Test that cache expires after TTL."""
        cache = RateCache(ttl=1)
        rates = {'EUR': 0.85}
        
        cache.set('USD', rates)
        assert cache.get('USD') is not None
        
        time.sleep(1.1)
        assert cache.get('USD') is None
    
    def test_clear(self):
        """Test clearing cache."""
        cache = RateCache()
        cache.set('USD', {'EUR': 0.85})
        cache.set('EUR', {'USD': 1.18})
        
        cache.clear()
        
        assert cache.get('USD') is None
        assert cache.get('EUR') is None