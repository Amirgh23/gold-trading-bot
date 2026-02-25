"""Retry logic with exponential backoff."""

import time
import logging
from typing import Callable, Any, Optional, Type, Tuple

logger = logging.getLogger(__name__)


def retry_with_backoff(
    func: Callable,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Any:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        exceptions: Exceptions to catch
    
    Returns:
        Function result
    
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries + 1} failed, "
                    f"retrying in {delay:.1f}s: {str(e)}"
                )
                time.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(
                    f"All {max_retries + 1} attempts failed: {str(e)}"
                )
    
    raise last_exception


class RetryableOperation:
    """Context manager for retryable operations."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.attempt = 0
        self.delay = initial_delay
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
        
        if self.attempt < self.max_retries:
            self.attempt += 1
            logger.warning(
                f"Operation failed (attempt {self.attempt}), "
                f"retrying in {self.delay:.1f}s"
            )
            time.sleep(self.delay)
            self.delay *= self.backoff_factor
            return True
        
        return False
