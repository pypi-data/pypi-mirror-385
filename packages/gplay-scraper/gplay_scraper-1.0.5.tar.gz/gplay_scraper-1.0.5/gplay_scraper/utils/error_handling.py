"""Unified error handling decorators for all gplay_scraper methods."""

import time
import logging
import json
from functools import wraps
from ..config import Config
from ..exceptions import AppNotFoundError, NetworkError, DataParsingError, RateLimitError, InvalidAppIdError

logger = logging.getLogger(__name__)

def retry_on_not_found(max_retries=Config.DEFAULT_RETRY_COUNT, delay=1.0):
    """Decorator to retry methods on AppNotFoundError with all HTTP clients.
    
    This decorator implements automatic retry logic when apps are not found,
    cycling through different HTTP clients to overcome potential blocking.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Delay in seconds between retries (default: 1.0)
        
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry_on_not_found(max_retries=5, delay=2.0)
        def fetch_app_data(self, app_id):
            # Method implementation
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except AppNotFoundError as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        # Switch to next HTTP client for retry
                        if hasattr(self, 'scraper') and hasattr(self.scraper, 'http_client'):
                            self.scraper.http_client._try_next_client()
                    continue
                except Exception as e:
                    # Re-raise non-recoverable exceptions immediately
                    raise e
            logger.error(f"All {max_retries} attempts failed. Skipping.")
            return None
        return wrapper
    return decorator

def handle_network_errors(return_empty=False):
    """Decorator to handle network errors gracefully.
    
    Catches network-related exceptions and provides graceful degradation
    instead of crashing the application.
    
    Args:
        return_empty: If True, return empty list/dict on errors instead of None
        
    Returns:
        Decorated function with network error handling
        
    Example:
        @handle_network_errors(return_empty=True)
        def fetch_search_results(self, query):
            # Method implementation that may fail due to network issues
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except NetworkError as e:
                logger.warning(f"Network error in {func.__name__}: {e}")
                return [] if return_empty else None
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                return [] if return_empty else None
        return wrapper
    return decorator

def handle_parsing_errors(return_empty=False):
    """Decorator to handle data parsing errors gracefully.
    
    Catches JSON parsing and data extraction errors that may occur when
    Google Play Store changes their data structure.
    
    Args:
        return_empty: If True, return empty list/dict on errors instead of None
        
    Returns:
        Decorated function with parsing error handling
        
    Example:
        @handle_parsing_errors(return_empty=True)
        def parse_app_data(self, raw_data):
            # Method implementation that may fail due to data format changes
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except DataParsingError as e:
                logger.warning(f"Parsing error in {func.__name__}: {e}")
                return [] if return_empty else None
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                return [] if return_empty else None
        return wrapper
    return decorator

def handle_rate_limit():
    """Decorator to handle rate limiting with exponential backoff.
    
    Implements exponential backoff strategy when rate limits are encountered,
    gradually increasing delay between retries to avoid overwhelming the server.
    
    Returns:
        Decorated function with rate limit handling
        
    Example:
        @handle_rate_limit()
        def make_api_request(self, endpoint):
            # Method implementation that may trigger rate limits
            pass
            
    Note:
        Uses exponential backoff: 1s, 2s, 4s, 8s, etc.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            max_attempts = Config.DEFAULT_RETRY_COUNT
            base_delay = Config.RATE_LIMIT_DELAY
            
            for attempt in range(max_attempts):
                try:
                    return func(self, *args, **kwargs)
                except RateLimitError as e:
                    if attempt < max_attempts - 1:
                        # Exponential backoff: 1s, 2s, 4s, 8s...
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limited. Waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue
                    logger.error(f"Rate limit exceeded after {max_attempts} attempts")
                    return None
                except Exception as e:
                    # Re-raise non-rate-limit exceptions
                    raise e
        return wrapper
    return decorator

def validate_inputs():
    """Decorator to validate method inputs.
    
    Performs basic input validation to ensure app IDs, queries, and other
    parameters are valid before processing.
    
    Returns:
        Decorated function with input validation
        
    Raises:
        InvalidAppIdError: When input validation fails
        
    Example:
        @validate_inputs()
        def fetch_app_details(self, app_id):
            # Method implementation with validated inputs
            pass
            
    Note:
        Validates that first argument is non-empty string
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # Validate first argument (usually app_id, query, etc.)
                if args and not args[0]:
                    raise InvalidAppIdError("Input cannot be empty")
                if args and not isinstance(args[0], str):
                    raise InvalidAppIdError("Input must be a string")
                return func(self, *args, **kwargs)
            except InvalidAppIdError:
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                logger.error(f"Input validation error in {func.__name__}: {e}")
                raise InvalidAppIdError(f"Invalid input: {e}")
        return wrapper
    return decorator

def safe_print():
    """Decorator to handle Unicode errors in print methods.
    
    Handles Unicode encoding issues when printing data containing
    special characters from different languages.
    
    Returns:
        Decorated function with Unicode-safe printing
        
    Example:
        @safe_print()
        def print_app_data(self, app_id):
            # Method implementation that prints data with Unicode characters
            pass
            
    Note:
        Falls back to ASCII encoding if Unicode printing fails
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except UnicodeEncodeError:
                # Fallback: get data and print with ASCII encoding
                data = getattr(self, func.__name__.replace('print', 'analyze'))(*args, **kwargs)
                if data:
                    print(json.dumps(data, indent=2, ensure_ascii=True))
                else:
                    print("No data available")
            except Exception as e:
                print(f"Error: {e}")
        return wrapper
    return decorator

def comprehensive_error_handler(return_empty=False):
    """Comprehensive decorator combining all error handling strategies.
    
    This decorator provides unified error handling for all scraper methods,
    combining input validation, retry logic, network error handling,
    and graceful degradation in a single decorator.
    
    Args:
        return_empty: If True, return empty list/dict on errors instead of None
        
    Returns:
        Decorated function with comprehensive error handling
        
    Example:
        @comprehensive_error_handler(return_empty=True)
        def scrape_app_data(self, app_id):
            # Method implementation with full error protection
            pass
            
    Features:
        - Input validation
        - Automatic retries with HTTP client fallback
        - Network and parsing error handling
        - Rate limit management
        - Graceful degradation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # Input validation
                if args and not args[0]:
                    raise InvalidAppIdError("Input cannot be empty")
                if args and not isinstance(args[0], str):
                    raise InvalidAppIdError("Input must be a string")
                    
                # Retry logic with HTTP client fallback
                max_retries = Config.DEFAULT_RETRY_COUNT
                for attempt in range(max_retries):
                    try:
                        return func(self, *args, **kwargs)
                    except AppNotFoundError as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                            time.sleep(Config.RATE_LIMIT_DELAY)
                            # Switch to next HTTP client for retry
                            if hasattr(self, 'scraper') and hasattr(self.scraper, 'http_client'):
                                self.scraper.http_client._try_next_client()
                            continue
                        logger.error(f"All {max_retries} attempts failed")
                        return [] if return_empty else None
                    except (NetworkError, DataParsingError, RateLimitError) as e:
                        # Handle recoverable errors gracefully
                        logger.warning(f"Recoverable error in {func.__name__}: {e}")
                        return [] if return_empty else None
                    except Exception as e:
                        # Handle unexpected errors
                        logger.error(f"Unexpected error in {func.__name__}: {e}")
                        return [] if return_empty else None
                        
            except InvalidAppIdError:
                # Re-raise validation errors
                raise 
            except Exception as e:
                # Handle critical errors
                logger.error(f"Critical error in {func.__name__}: {e}")
                return [] if return_empty else None
        return wrapper
    return decorator