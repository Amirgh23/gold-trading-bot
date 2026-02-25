"""Data caching with fallback mechanisms."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """In-memory cache for market data with TTL."""
    
    def __init__(self, ttl_minutes: int = 60):
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache = {}
        self.timestamps = {}
    
    def set(self, key: str, data: pd.DataFrame):
        """Store data in cache."""
        self.cache[key] = data.copy()
        self.timestamps[key] = datetime.now()
        logger.debug(f"Cached {len(data)} rows for {key}")
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """Retrieve data from cache if not expired."""
        if key not in self.cache:
            return None
        
        if datetime.now() - self.timestamps[key] > self.ttl:
            logger.debug(f"Cache expired for {key}")
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key].copy()
    
    def is_valid(self, key: str) -> bool:
        """Check if cache entry is valid."""
        if key not in self.cache:
            return False
        
        if datetime.now() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return False
        
        return True
    
    def clear(self, key: Optional[str] = None):
        """Clear cache entry or entire cache."""
        if key:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                logger.debug(f"Cleared cache for {key}")
        else:
            self.cache.clear()
            self.timestamps.clear()
            logger.debug("Cleared entire cache")
    
    def get_size(self) -> int:
        """Get number of cached entries."""
        return len(self.cache)
