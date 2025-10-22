
#!/usr/bin/env python3
"""
Structured logging utilities for SpeakUB.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import structlog
    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False
    structlog = None


class StructuredLogger:
    """Structured logging wrapper with fallback to standard logging."""

    def __init__(self, name: str, level: str = 'INFO'):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            level: Logging level
        """
        self.name = name
        self.level = level
        self._logger = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Set up the appropriate logger based on availability."""
        if HAS_STRUCTLOG:
            self._setup_structlog()
        else:
            self._setup_standard_logger()

    def _setup_structlog(self) -> None:
        """Set up structlog-based logging."""
        try:
            # Configure structlog
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
            )

            self._logger = structlog.get_logger(self.name)
            self._is_structlog = True

        except Exception as e:
            print(
                f"Failed to setup structlog, falling back to standard logging: {e}")
            self._setup_standard_logger()

    def _setup_standard_logger(self) -> None:
        """Set up standard logging as fallback."""
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(
            getattr(logging, self.level.upper(), logging.INFO))

        # Avoid duplicate handlers
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

        self._is_structlog = False

    def _log(self, level: str, message: str, **kwargs) -> None:
        """
        Internal logging method.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional structured data
        """
        if self._is_structlog:
            # Use structlog
            log_method = getattr(
                self._logger, level.lower(), self._logger.info)
            log_method(message, **kwargs)
        else:
            # Use standard logging with formatted extra data
            log_method = getattr(
                self._logger, level.lower(), self._logger.info)

            if kwargs:
                # Format extra data as string
                extra_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                message = f"{message} [{extra_str}]"

            log_method(message)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log('debug', message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log('info', message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log('warning', message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log('error', message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log('critical', message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        if self._is_structlog:
            self._logger.exception(message, **kwargs)
        else:
            self._logger.exception(message)


def configure_structured_logging(
    log_file: Optional[str] = None,
    level: str = 'INFO',
    format_type: str = 'json'
) -> None:
    """
    Configure global structured logging.

    Args:
        log_file: Optional log file path
        level: Logging level
        format_type: Log format ('json', 'logfmt', 'plain')
    """
    if not HAS_STRUCTLOG:
        # Fallback to standard logging configuration
        logging.basicConfig(
            level=getattr(logging, level.upper(), logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file if log_file else None,
        )
        return

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Choose renderer based on format type
    if format_type == 'json':
        processors.append(structlog.processors.JSONRenderer())
    elif format_type == 'logfmt':
        processors.append(structlog.processors.LogfmtRenderer())
    else:  # plain
        processors.append(structlog.processors.KeyValueRenderer())

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Configure structlog for file output
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    else:
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Convenience functions for common logging patterns
def log_performance(operation: str, duration_ms: float, **kwargs) -> None:
    """
    Log performance metrics.

    Args:
        operation: Name of the operation
        duration_ms: Duration in milliseconds
        **kwargs: Additional context
    """
    logger = get_structured_logger('performance')
    logger.info(
        f"Performance: {operation}",
        operation=operation,
        duration_ms=round(duration_ms, 2),
        **kwargs
    )


def log_user_action(action: str, user_id: Optional[str] = None, **kwargs) -> None:
    """
    Log user actions.

    Args:
        action: Action performed
        user_id: Optional user identifier
        **kwargs: Additional context
    """
    logger = get_structured_logger('user_action')
    logger.info(
        f"User action: {action}",
        action=action,
        user_id=user_id,
        **kwargs
    )


def log_error_with_context(error: Exception, context: str, **kwargs) -> None:
    """
    Log errors with context.

    Args:
        error: Exception that occurred
        context: Context where error occurred
        **kwargs: Additional context
    """
    logger = get_structured_logger('error')
    logger.error(
        f"Error in {context}: {error}",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context,
        **kwargs
    )


def log_cache_operation(operation: str, cache_name: str, hit: bool = False,
                        size: Optional[int] = None, **kwargs) -> None:
    """
    Log cache operations.

    Args:
        operation: Cache operation ('get', 'set', 'evict', etc.)
        cache_name: Name of the cache
        hit: Whether it was a cache hit
        size: Current cache size
        **kwargs: Additional context
    """
    logger = get_structured_logger('cache')
    logger.debug(
        f"Cache {operation}: {cache_name}",
        operation=operation,
        cache_name=cache_name,
        hit=hit,
        size=size,
        **kwargs
    )


def log_tts_operation(operation: str, voice: str, text_length: int,
                      duration_ms: Optional[float] = None, **kwargs) -> None:
    """
    Log TTS operations.

    Args:
        operation: TTS operation ('synthesize', 'play', 'stop', etc.)
        voice: Voice used
        text_length: Length of text processed
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional context
    """
    logger = get_structured_logger('tts')
    logger.info(
        f"TTS {operation}",
        operation=operation,
        voice=voice,
        text_length=text_length,
        duration_ms=round(duration_ms, 2) if duration_ms else None,
        **kwargs
    )


# Example usage and testing
if __name__ == "__main__":
    # Configure structured logging
    configure_structured_logging(level='DEBUG', format_type='json')

    # Get logger and test
    logger = get_structured_logger('test')

    logger.info("Application started", version="1.0.0", environment="dev")
    logger.debug("Processing user request", user_id="12345", action="login")
    logger.warning("Rate limit approaching", remaining=5, reset_in=300)
    logger.error("Database connection failed", error_code=500, retry_count=3)

    # Test convenience functions
    log_performance("file_load", 150.5, file_size=1024, file_type="epub")
    log_user_action("chapter_change", user_id="12345",
                    chapter=5, book="sample.epub")
    log_cache_operation("get", "chapter_cache", hit=True, size=25)
    log_tts_operation("synthesize", "zh-TW", 500,
                      duration_ms=1250.5, success=True)

    try:
        raise ValueError("Test error")
    except ValueError as e:
        log_error_with_context(e, "test_function", param1="value1", param2=42)

    print("Structured logging test completed.")
