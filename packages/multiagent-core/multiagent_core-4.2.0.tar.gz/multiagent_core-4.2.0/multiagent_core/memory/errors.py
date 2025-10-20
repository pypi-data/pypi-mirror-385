"""Memory System Error Handling

Custom exceptions and error handling utilities for graceful degradation.
"""


class MemoryError(Exception):
    """Base exception for all memory system errors."""
    pass


class MemoryInitializationError(MemoryError):
    """Raised when memory system fails to initialize."""

    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message)
        self.cause = cause


class MemoryStorageError(MemoryError):
    """Raised when storage operations fail."""

    def __init__(self, operation: str, cause: Exception = None):
        message = f"Storage operation failed: {operation}"
        if cause:
            message += f" - {str(cause)}"
        super().__init__(message)
        self.operation = operation
        self.cause = cause


class MemorySearchError(MemoryError):
    """Raised when search operations fail."""

    def __init__(self, query: str, cause: Exception = None):
        message = f"Search failed for query: {query}"
        if cause:
            message += f" - {str(cause)}"
        super().__init__(message)
        self.query = query
        self.cause = cause


class MemoryDegradedModeError(MemoryError):
    """Raised when trying to use memory in degraded mode."""

    def __init__(self):
        super().__init__(
            "Memory system is in degraded mode. "
            "Some features may be unavailable. "
            "Check system logs for initialization errors."
        )


def handle_memory_error(operation: str, error: Exception, logger) -> None:
    """Handle memory errors with appropriate logging.

    Args:
        operation: Name of the operation that failed
        error: The exception that was raised
        logger: Logger instance for error reporting
    """
    if isinstance(error, MemoryError):
        logger.error(f"Memory operation '{operation}' failed: {error}")
    else:
        logger.error(f"Unexpected error in memory operation '{operation}': {error}", exc_info=True)


def safe_memory_operation(func):
    """Decorator for safe memory operations with error handling.

    Catches exceptions and provides graceful degradation.
    Returns None if operation fails instead of raising.

    Example:
        @safe_memory_operation
        async def search_memories(self, query):
            # Operation that might fail
            pass
    """
    import functools
    import logging

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        try:
            return await func(*args, **kwargs)
        except MemoryDegradedModeError:
            logger.warning(f"Memory operation {func.__name__} unavailable in degraded mode")
            return None
        except MemoryError as e:
            handle_memory_error(func.__name__, e, logger)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return None

    return wrapper
