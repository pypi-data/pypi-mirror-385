"""Caching mechanism for exchange rates."""

import time
from typing import Dict, Optional, Any
from threading import Lock

class RateCache:
    """Thread-safe cache for exchange rates with TTL support."""

    def __init__(self, ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            ttl: Time to live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl
        self._lock = Lock()

    def get (self, key: str) -> Optional[Dict[str, float]]:
        """
        Retrieve cached rates if not expired.
        
        Args:
            key: Cache key (typically the base currency)
            
        Returns:
            Cached rates dict or None if expired/missing
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if time.time() - entry['timestamp'] > self._ttl:
                del self._cache[key]
                return None
            
            return entry['rates']
        
    def set(self, key: str, rates: Dict[str, float]) -> None:
        """
        Store rates in cache.
        
        Args:
            key: Cache key
            rates: Exchange rates dictionary
        """
        with self._lock:
            self._cache[key] = {
                'rates': rates,
                'timestamp': time.time()
            }
    
    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._cache.clear()