"""
Retry Logic with Exponential Backoff
Purpose: Automatically retry failed operations with intelligent backoff
"""

import time
import random
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps


def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator for retrying function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff (usually 2)
        jitter: Add random jitter to prevent thundering herd
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Callback function called on each retry (receives attempt number and exception)

    Usage:
        @exponential_backoff_retry(max_retries=3, base_delay=1.0)
        def fetch_data():
            return requests.get("https://api.example.com/data")

        @exponential_backoff_retry(
            max_retries=5,
            base_delay=2.0,
            exceptions=(requests.RequestException,),
            on_retry=lambda attempt, exc: print(f"Retry {attempt}: {exc}")
        )
        def api_call():
            return external_api.get_user(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Don't retry on last attempt
                    if attempt == max_retries:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Add jitter (0-100% of delay)
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt + 1, e)

                    print(
                        f"[Retry {attempt + 1}/{max_retries}] "
                        f"{func.__name__} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)

            # All retries exhausted
            raise last_exception

        return wrapper

    return decorator


class RetryStrategy:
    """
    Configurable retry strategy with multiple backoff algorithms.
    """

    @staticmethod
    def constant_backoff(attempt: int, base_delay: float) -> float:
        """Constant delay between retries."""
        return base_delay

    @staticmethod
    def linear_backoff(attempt: int, base_delay: float) -> float:
        """Linear increase in delay."""
        return base_delay * attempt

    @staticmethod
    def exponential_backoff(
        attempt: int,
        base_delay: float,
        exponential_base: float = 2.0,
        max_delay: float = 60.0
    ) -> float:
        """Exponential increase in delay."""
        delay = base_delay * (exponential_base ** attempt)
        return min(delay, max_delay)

    @staticmethod
    def fibonacci_backoff(attempt: int, base_delay: float, max_delay: float = 60.0) -> float:
        """Fibonacci sequence backoff."""
        fib = [1, 1]
        for i in range(2, attempt + 1):
            fib.append(fib[-1] + fib[-2])
        delay = base_delay * fib[attempt]
        return min(delay, max_delay)

    @staticmethod
    def add_jitter(delay: float, jitter_factor: float = 0.5) -> float:
        """Add random jitter to delay (0 to jitter_factor of delay)."""
        jitter = random.uniform(0, delay * jitter_factor)
        return delay + jitter


def retry_with_strategy(
    strategy: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Retry decorator with custom backoff strategy.

    Usage:
        @retry_with_strategy(
            strategy=RetryStrategy.exponential_backoff,
            max_retries=5,
            base_delay=2.0
        )
        def fetch_user_data(user_id):
            return api.get_user(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    delay = strategy(attempt, base_delay)
                    delay = RetryStrategy.add_jitter(delay)

                    print(
                        f"[Retry {attempt + 1}/{max_retries}] "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


class RetryableError(Exception):
    """Base exception for retryable errors."""
    pass


class NonRetryableError(Exception):
    """Exception that should not be retried."""
    pass


# Example Usage
if __name__ == "__main__":
    import requests

    # Example 1: Simple exponential backoff
    @exponential_backoff_retry(max_retries=3, base_delay=1.0)
    def fetch_api_data(url: str):
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    # Example 2: Custom retry callback
    def on_retry_callback(attempt: int, exception: Exception):
        print(f"⚠️  Retry attempt {attempt}: {type(exception).__name__}")

    @exponential_backoff_retry(
        max_retries=5,
        base_delay=2.0,
        exceptions=(requests.RequestException,),
        on_retry=on_retry_callback
    )
    def fetch_with_logging(url: str):
        return requests.get(url, timeout=5).json()

    # Example 3: Custom backoff strategy
    @retry_with_strategy(
        strategy=RetryStrategy.fibonacci_backoff,
        max_retries=4,
        base_delay=1.0
    )
    def fibonacci_retry_example():
        # Simulate transient failure
        if random.random() < 0.7:
            raise RetryableError("Simulated failure")
        return "Success!"

    # Test the functions
    try:
        data = fetch_api_data("https://api.example.com/data")
        print(f"Data fetched: {data}")
    except Exception as e:
        print(f"Failed after all retries: {e}")
