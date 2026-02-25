"""Memory optimization and management."""

import gc
import psutil
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages memory usage and optimization."""
    
    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=5)
    
    def get_memory_usage(self) -> dict:
        """Get current memory usage."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            return {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024),
                'percent': memory_percent,
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}
    
    def should_cleanup(self) -> bool:
        """Check if cleanup should be performed."""
        # Cleanup periodically
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            return True
        
        # Cleanup if memory usage is high
        memory_info = self.get_memory_usage()
        if memory_info.get('percent', 0) > self.max_memory_percent:
            return True
        
        return False
    
    def cleanup(self) -> bool:
        """Perform memory cleanup."""
        try:
            # Force garbage collection
            collected = gc.collect()
            
            memory_before = self.get_memory_usage()
            
            # Additional cleanup
            gc.collect()
            
            memory_after = self.get_memory_usage()
            
            freed_mb = memory_before.get('rss_mb', 0) - memory_after.get('rss_mb', 0)
            
            logger.info(
                f"Memory cleanup: collected {collected} objects, "
                f"freed {freed_mb:.2f}MB, "
                f"current usage: {memory_after.get('percent', 0):.1f}%"
            )
            
            self.last_cleanup = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            return False
    
    def optimize_dataframe(self, df) -> None:
        """Optimize pandas DataFrame memory usage."""
        try:
            import pandas as pd
            
            for col in df.columns:
                col_type = df[col].dtype
                
                # Optimize numeric types
                if col_type != 'object':
                    c_min = df[col].min()
                    c_max = df[col].max()
                    
                    if str(col_type)[:3] == 'int':
                        if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                            df[col] = df[col].astype(np.int8)
                        elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                            df[col] = df[col].astype(np.int16)
                        elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                            df[col] = df[col].astype(np.int32)
                    else:
                        if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                            df[col] = df[col].astype(np.float32)
        except Exception as e:
            logger.debug(f"Error optimizing DataFrame: {e}")
    
    def trim_data(self, data: list, max_items: int = 10000) -> list:
        """Trim data to maximum items."""
        if len(data) > max_items:
            logger.debug(f"Trimming data from {len(data)} to {max_items} items")
            return data[-max_items:]
        return data
    
    def get_memory_report(self) -> str:
        """Get detailed memory report."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            report = f"""
Memory Report:
- RSS: {memory_info.rss / (1024 * 1024):.2f} MB
- VMS: {memory_info.vms / (1024 * 1024):.2f} MB
- Percent: {process.memory_percent():.1f}%
- GC Objects: {len(gc.get_objects())}
            """
            return report
        except Exception as e:
            logger.error(f"Error generating memory report: {e}")
            return ""


# Import numpy for type checking
try:
    import numpy as np
except ImportError:
    np = None
