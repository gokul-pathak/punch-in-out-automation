import sys
import traceback
import logging
from typing import Optional, Callable
from functools import wraps
from datetime import datetime
from config.settings import ScheduleConfig

logger = logging.getLogger(__name__)

class RetryableError(Exception):
    """Error that can be retried"""
    pass

class CriticalError(Exception):
    """Error that requires immediate attention"""
    pass

class ErrorManager:
    def __init__(self):
        self.error_counts = {}
        self.last_error_time = {}

    def handle_error(self, error: Exception, context: str):
        """Handle different types of errors"""
        error_key = f"{context}:{type(error).__name__}"
        
        # Update error counts
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_error_time[error_key] = datetime.now()

        if isinstance(error, RetryableError):
            return self._handle_retryable_error(error, context)
        elif isinstance(error, CriticalError):
            return self._handle_critical_error(error, context)
        else:
            return self._handle_unknown_error(error, context)

    def _handle_retryable_error(self, error: RetryableError, context: str) -> bool:
        """Handle retryable errors with exponential backoff"""
        error_count = self.error_counts.get(f"{context}:{type(error).__name__}", 0)
        
        if error_count <= ScheduleConfig.MAX_RETRIES:
            retry_delay = ScheduleConfig.RETRY_DELAY * (2 ** (error_count - 1))
            logger.warning(
                f"Retryable error in {context} (attempt {error_count}): {str(error)}. "
                f"Retrying in {retry_delay} seconds"
            )
            return True
        else:
            logger.error(f"Max retries exceeded for {context}: {str(error)}")
            return False

    def _handle_critical_error(self, error: CriticalError, context: str) -> bool:
        """Handle critical errors"""
        logger.critical(f"Critical error in {context}: {str(error)}")
        self._send_emergency_notification(error, context)
        return False

    def _handle_unknown_error(self, error: Exception, context: str) -> bool:
        """Handle unknown errors"""
        logger.error(
            f"Unknown error in {context}: {str(error)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return False

    def _send_emergency_notification(self, error: Exception, context: str):
        """Send emergency notification for critical errors"""
        # Implement emergency notification system here
        pass

def retry_on_failure(max_retries: int = ScheduleConfig.MAX_RETRIES):
    """Decorator for automatic retry on failure"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(
                        f"Retry attempt {attempt + 1} of {max_retries} for {func.__name__}: {str(e)}"
                    )
                    time.sleep(ScheduleConfig.RETRY_DELAY * (2 ** attempt))
        return wrapper
    return decorator