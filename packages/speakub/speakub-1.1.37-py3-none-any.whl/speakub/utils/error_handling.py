
#!/usr/bin/env python3
"""
Unified error handling utilities for SpeakUB.
"""

import functools
import logging
from typing import Any, Callable, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


class ErrorHandler:
    """Centralized error handling with configurable behavior."""

    def __init__(self):
        self._handlers = {}

    def register_handler(self, exception_type: Type[Exception],
                         handler: Callable):
        """Register a custom handler for specific exception types."""
        self._handlers[exception_type] = handler

    def handle_error(self, error: Exception, context: Optional[str] = None) -> Any:
        """Handle an error using registered handlers or default behavior."""
        handler = self._handlers.get(type(error))
        if handler:
            return handler(error, context)
        return self._default_handler(error, context)

    def _default_handler(self, error: Exception,
                         context: Optional[str] = None) -> None:
        """Default error handling behavior."""
        context_msg = f" in {context}" if context else ""
        logger.error(f"Unhandled error{context_msg}: {error}")


# Global error handler instance
error_handler = ErrorHandler()


def handle_errors(
    *exception_types: Type[Exception],
    default_return: Any = None,
    log_level: str = 'error',
    user_message: Optional[str] = None,
    reraise: bool = False
):
    """
    Unified error handling decorator.

    Args:
        *exception_types: Exception types to catch
        default_return: Value to return on error
        log_level: Logging level ('debug', 'info', 'warning', 'error', 'critical')
        user_message: User-friendly message to display
        reraise: Whether to re-raise the exception after handling

    Returns:
        Decorated function
    """
    if not exception_types:
        exception_types = (Exception,)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # Log the error
                log_func = getattr(logger, log_level.lower(), logger.error)
                log_func(f"Error in {func.__name__}: {e}")

                # Show user message if specified and app reference available
                if user_message:
                    # Try to find app reference in args/kwargs or instance
                    app = None
                    if args and hasattr(args[0], 'notify'):
                        app = args[0]
                    elif hasattr(func, '__self__') and hasattr(func.__self__, 'notify'):
                        app = func.__self__

                    if app and hasattr(app, 'notify'):
                        severity = 'error' if log_level in (
                            'error', 'critical') else 'warning'
                        app.notify(user_message, severity=severity)

                # Re-raise if requested
                if reraise:
                    raise

                return default_return

        return wrapper
    return decorator


def handle_async_errors(
    *exception_types: Type[Exception],
    default_return: Any = None,
    log_level: str = 'error',
    user_message: Optional[str] = None,
    reraise: bool = False
):
    """
    Unified error handling decorator for async functions.

    Args:
        *exception_types: Exception types to catch
        default_return: Value to return on error
        log_level: Logging level
        user_message: User-friendly message to display
        reraise: Whether to re-raise the exception after handling

    Returns:
        Decorated async function
    """
    if not exception_types:
        exception_types = (Exception,)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exception_types as e:
                # Log the error
                log_func = getattr(logger, log_level.lower(), logger.error)
                log_func(f"Error in {func.__name__}: {e}")

                # Show user message if specified and app reference available
                if user_message:
                    app = None
                    if args and hasattr(args[0], 'notify'):
                        app = args[0]
                    elif hasattr(func, '__self__') and hasattr(func.__self__, 'notify'):
                        app = func.__self__

                    if app and hasattr(app, 'notify'):
                        severity = 'error' if log_level in (
                            'error', 'critical') else 'warning'
                        app.notify(user_message, severity=severity)

                # Re-raise if requested
                if reraise:
                    raise

                return default_return

        return wrapper
    return decorator


# Convenience decorators for common error types
def handle_io_errors(
    default_return: Any = None,
    user_message: str = "File operation failed",
    log_level: str = 'error'
):
    """Handle common I/O errors."""
    return handle_errors(
        (IOError, OSError, FileNotFoundError, PermissionError),
        default_return=default_return,
        user_message=user_message,
        log_level=log_level
    )


def handle_network_errors(
    default_return: Any = None,
    user_message: str = "Network operation failed",
    log_level: str = 'warning'
):
    """Handle common network errors."""
    return handle_errors(
        (ConnectionError, TimeoutError, OSError),
        default_return=default_return,
        user_message=user_message,
        log_level=log_level
    )


def handle_tts_errors(
    default_return: Any = None,
    user_message: str = "TTS operation failed",
    log_level: str = 'warning'
):
    """Handle TTS-related errors."""
    return handle_errors(
        (Exception,),  # TTS can raise various exceptions
        default_return=default_return,
        user_message=user_message,
        log_level=log_level
    )


def handle_parsing_errors(
    default_return: Any = None,
    user_message: str = "Content parsing failed",
    log_level: str = 'warning'
):
    """Handle parsing-related errors."""
    return handle_errors(
        (ValueError, TypeError, AttributeError),
        default_return=default_return,
        user_message=user_message,
        log_level=log_level
    )


# Context manager for error handling
class ErrorContext:
    """Context manager for scoped error handling."""

    def __init__(
        self,
        *exception_types: Type[Exception],
        default_return: Any = None,
        log_level: str = 'error',
        user_message: Optional[str] = None,
        app_ref: Optional[Any] = None
    ):
        self.exception_types = exception_types or (Exception,)
        self.default_return = default_return
        self.log_level = log_level
        self.user_message = user_message
        self.app_ref = app_ref

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, self.exception_types):
            # Log the error
            log_func = getattr(logger, self.log_level.lower(), logger.error)
            log_func(f"Error in context: {exc_val}")

            # Show user message
            if self.user_message and self.app_ref and hasattr(self.app_ref, 'notify'):
                severity = 'error' if self.log_level in (
                    'error', 'critical') else 'warning'
                self.app_ref.notify(self.user_message, severity=severity)

            # Suppress the exception
            return True
        return False
