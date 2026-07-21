"""Data caching with fallback mechanisms."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """In-memory cache for market data with TTL."""
    
    def __init__(
        self,
        ttl_minutes: float = 60,
        ttl_seconds: Optional[float] = None,
        max_size: int = 100,
    ):
        seconds = ttl_seconds if ttl_seconds is not None else ttl_minutes * 60
        self.ttl = timedelta(seconds=max(0, seconds))
        self.max_size = max(1, max_size)
        self.cache = {}
    
    def set(self, key: str, data: pd.DataFrame):
        """Store data in cache."""
        if key not in self.cache and len(self.cache) >= self.max_size:
            oldest = min(self.cache, key=lambda item: self.cache[item]['timestamp'])
            del self.cache[oldest]
        self.cache[key] = {'data': data.copy(), 'timestamp': datetime.now().timestamp()}
        logger.debug(f"Cached {len(data)} rows for {key}")
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Retrieve data from cache if not expired."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if datetime.now().timestamp() - entry['timestamp'] > self.ttl.total_seconds():
            logger.debug(f"Cache expired for {key}")
            del self.cache[key]
            return None

        return entry['data'].copy()
    
    def is_valid(self, key: str) -> bool:
        """Check if cache entry is valid."""
        if key not in self.cache:
            return False
        
        if datetime.now().timestamp() - self.cache[key]['timestamp'] > self.ttl.total_seconds():
            del self.cache[key]
            return False
        
        return True
    
    def clear(self, key: Optional[str] = None):
        """Clear cache entry or entire cache."""
        if key:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cleared cache for {key}")
        else:
            self.cache.clear()
            logger.debug("Cleared entire cache")
    
    def get_size(self) -> int:
        """Get number of cached entries."""
        return len(self.cache)
