

#!/usr/bin/env python3
"""
Unified exception handling for SpeakUB.
"""

import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SpeakUBException(Exception):
    """Base exception with logging support"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = time.time()
        logger.error(f"{self.__class__.__name__}: {message}",
                     extra={"details": self.details})


class SpeakUBError(SpeakUBException):
    """Base exception for SpeakUB errors."""


class NetworkError(SpeakUBError):
    """Network-related errors."""


class TTSError(SpeakUBError):
    """TTS-related errors."""


class ParseError(SpeakUBError):
    """Parsing-related errors."""


class ConfigurationError(SpeakUBError):
    """Configuration-related errors."""


class FileSizeError(SpeakUBError):
    """File size-related errors."""


class SecurityError(SpeakUBError):
    """Security-related errors."""


class NetworkException(SpeakUBException):
    """Network-related exceptions."""


class ParsingException(SpeakUBException):
    """Parsing-related exceptions."""


class TTSException(SpeakUBException):
    """TTS-related exceptions."""


class CacheException(SpeakUBException):
    """Cache-related exceptions."""
