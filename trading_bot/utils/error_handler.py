"""Error handling and recovery."""

import logging
import traceback
from typing import Callable, Any, Optional
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error type classification."""
    NETWORK_ERROR = "NETWORK_ERROR"
    ORDER_EXECUTION_ERROR = "ORDER_EXECUTION_ERROR"
    DATA_ERROR = "DATA_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorHandler:
    """Handles errors and recovery with context-aware strategies."""
    
    @staticmethod
    def classify_error(error: Exception) -> ErrorType:
        """Classify error type."""
        error_str = str(error).lower()
        
        if any(x in error_str for x in ['connection', 'timeout', 'network', 'socket']):
            return ErrorType.NETWORK_ERROR
        elif any(x in error_str for x in ['order', 'execution', 'fill']):
            return ErrorType.ORDER_EXECUTION_ERROR
        elif any(x in error_str for x in ['data', 'parse', 'format']):
            return ErrorType.DATA_ERROR
        elif any(x in error_str for x in ['invalid', 'validation']):
            return ErrorType.VALIDATION_ERROR
        elif any(x in error_str for x in ['config', 'parameter']):
            return ErrorType.CONFIGURATION_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    @staticmethod
    def handle_error(
        error: Exception,
        context: str = "",
        severity: str = "ERROR",
        error_type: Optional[ErrorType] = None,
    ) -> None:
        """
        Handle error with logging and context.
        
        Args:
            error: Exception to handle
            context: Context information
            severity: Error severity (ERROR, WARNING, CRITICAL)
            error_type: Classified error type
        """
        if error_type is None:
            error_type = ErrorHandler.classify_error(error)
        
        error_msg = f"[{error_type.value}] {context}: {str(error)}" if context else f"[{error_type.value}] {str(error)}"
        stack_trace = traceback.format_exc()
        
        log_data = {
            'error_type': error_type.value,
            'message': error_msg,
            'stack_trace': stack_trace,
        }
        
        if severity == "CRITICAL":
            logger.critical(f"{error_msg}\n{stack_trace}")
        elif severity == "WARNING":
            logger.warning(f"{error_msg}\n{stack_trace}")
        else:
            logger.error(f"{error_msg}\n{stack_trace}")
    
    @staticmethod
    def safe_execute(
        func: Callable,
        *args,
        default_return: Any = None,
        context: str = "",
        **kwargs,
    ) -> Any:
        """
        Safely execute function with error handling.
        
        Args:
            func: Function to execute
            default_return: Default return value on error
            context: Context information
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, context)
            return default_return
    
    @staticmethod
    def retry_on_error(
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        retryable_errors: Optional[list] = None,
    ):
        """
        Decorator for retrying function on error.
        
        Args:
            max_retries: Maximum number of retries
            delay: Initial delay between retries
            backoff: Backoff multiplier
            retryable_errors: List of error types to retry on
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                
                current_delay = delay
                last_error = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        error_type = ErrorHandler.classify_error(e)
                        
                        # Check if error is retryable
                        if retryable_errors and error_type not in retryable_errors:
                            raise
                        
                        last_error = e
                        
                        if attempt < max_retries:
                            logger.warning(
                                f"Attempt {attempt + 1} failed ({error_type.value}), "
                                f"retrying in {current_delay}s: {str(e)}"
                            )
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(
                                f"All {max_retries + 1} attempts failed: {str(e)}"
                            )
                
                raise last_error
            
            return wrapper
        return decorator


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary."""
    try:
        return dictionary.get(key, default)
    except Exception:
        return default


def safe_list_access(lst: list, index: int, default: Any = None) -> Any:
    """Safely access list element."""
    try:
        if 0 <= index < len(lst):
            return lst[index]
        return default
    except Exception:
        return default
