
#!/usr/bin/env python3
"""
Input validation utilities for SpeakUB.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import unquote

from speakub.core import SecurityError


class PathValidator:
    """Validates file paths for security."""

    # Maximum path length
    MAX_PATH_LENGTH = 1000

    # Forbidden characters in paths
    FORBIDDEN_CHARS = ['\x00', '\n', '\r', '\t']

    # Forbidden path patterns
    FORBIDDEN_PATTERNS = [
        r'^\.\.',  # Parent directory traversal
        r'/\.\.',  # Parent directory in path
        r'^/',     # Absolute paths
        r'\\',     # Backslashes (Windows path separators)
    ]

    @classmethod
    def validate_epub_path(cls, path: Union[str, Path]) -> Path:
        """
        Validate EPUB file path.

        Args:
            path: Path to validate

        Returns:
            Validated Path object

        Raises:
            SecurityError: If path is invalid
            ValueError: If path is not a string or Path
        """
        if not isinstance(path, (str, Path)):
            raise ValueError("Path must be a string or Path object")

        path_obj = Path(path)

        # Convert to string for validation
        path_str = str(path_obj)

        # Check path length
        if len(path_str) > cls.MAX_PATH_LENGTH:
            raise SecurityError(f"Path too long: {len(path_str)} characters")

        # Check for forbidden characters
        for char in cls.FORBIDDEN_CHARS:
            if char in path_str:
                raise SecurityError(
                    f"Forbidden character in path: {repr(char)}")

        # Check for forbidden patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, path_str):
                raise SecurityError(
                    f"Path contains forbidden pattern: {pattern}")

        # Check if file exists and is readable
        if not path_obj.exists():
            raise SecurityError(f"File does not exist: {path_obj}")

        if not path_obj.is_file():
            raise SecurityError(f"Path is not a file: {path_obj}")

        # Check file extension
        if path_obj.suffix.lower() not in ['.epub']:
            raise SecurityError(f"Invalid file extension: {path_obj.suffix}")

        return path_obj

    @classmethod
    def validate_chapter_src(cls, src: str) -> str:
        """
        Validate chapter source path within EPUB.

        Args:
            src: Chapter source path

        Returns:
            Validated source path

        Raises:
            SecurityError: If source path is invalid
        """
        if not isinstance(src, str):
            raise SecurityError("Chapter source must be a string")

        # Check path length
        if len(src) > cls.MAX_PATH_LENGTH:
            raise SecurityError(
                f"Chapter source too long: {len(src)} characters")

        # Check for forbidden characters
        for char in cls.FORBIDDEN_CHARS:
            if char in src:
                raise SecurityError(
                    f"Forbidden character in chapter source: {repr(char)}")

        # Check for directory traversal
        if '..' in src or src.startswith('/'):
            raise SecurityError(f"Invalid chapter source path: {src}")

        # URL decode and check again
        decoded_src = unquote(src)
        if decoded_src != src:
            # If URL decoding changed the string, validate the decoded version too
            if '..' in decoded_src or decoded_src.startswith('/'):
                raise SecurityError(
                    f"Invalid decoded chapter source path: {decoded_src}")

        return src


class InputValidator:
    """General input validation utilities."""

    @staticmethod
    def validate_string_length(
        value: str,
        min_length: int = 0,
        max_length: int = 1000,
        field_name: str = "value",
        allow_unicode: bool = True,
        allow_newlines: bool = True
    ) -> str:
        """
        Validate string length and content.

        Args:
            value: String to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            field_name: Field name for error messages
            allow_unicode: Whether to allow non-ASCII characters
            allow_newlines: Whether to allow newline characters

        Returns:
            Validated string

        Raises:
            ValueError: If validation fails
            TypeError: If value is not a string
        """
        # Type checking
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string")

        # Length validation
        if len(value) < min_length:
            raise ValueError(
                f"{field_name} too short: {len(value)} < {min_length}")

        if len(value) > max_length:
            raise ValueError(
                f"{field_name} too long: {len(value)} > {max_length}")

        # Character set validation
        if not allow_unicode and not value.isascii():
            raise ValueError(f"{field_name} contains non-ASCII characters")

        # Newline validation
        if not allow_newlines and ('\n' in value or '\r' in value):
            raise ValueError(f"{field_name} contains newline characters")

        # Control character validation (except common whitespace)
        if any(ord(c) < 32 and c not in '\t\n\r' for c in value):
            raise ValueError(f"{field_name} contains control characters")

        return value

    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None,
                               max_value: Optional[Union[int, float]] = None,
                               field_name: str = "value") -> Union[int, float]:
        """
        Validate numeric value is within range.

        Args:
            value: Numeric value to validate
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            field_name: Field name for error messages

        Returns:
            Validated numeric value

        Raises:
            ValueError: If validation fails
            TypeError: If value is not numeric
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be numeric")

        if min_value is not None and value < min_value:
            raise ValueError(f"{field_name} too small: {value} < {min_value}")

        if max_value is not None and value > max_value:
            raise ValueError(f"{field_name} too large: {value} > {max_value}")

        return value

    @staticmethod
    def validate_choice(value: Any, choices: List[Any], field_name: str = "value") -> Any:
        """
        Validate value is in allowed choices.

        Args:
            value: Value to validate
            choices: List of allowed values
            field_name: Field name for error messages

        Returns:
            Validated value

        Raises:
            ValueError: If value is not in choices
        """
        if value not in choices:
            raise ValueError(f"{field_name} must be one of: {choices}")

        return value

    @staticmethod
    def validate_regex(value: str, pattern: str, field_name: str = "value") -> str:
        """
        Validate string matches regex pattern.

        Args:
            value: String to validate
            pattern: Regex pattern
            field_name: Field name for error messages

        Returns:
            Validated string

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        if not re.match(pattern, value):
            raise ValueError(f"{field_name} does not match required pattern")

        return value


class TTSValidator:
    """TTS-specific input validation."""

    # Valid voice name pattern (alphanumeric, hyphens, underscores)
    VOICE_PATTERN = r'^[a-zA-Z0-9_-]+$'

    # Valid rate range (-100 to +100)
    RATE_MIN = -100
    RATE_MAX = 100

    # Valid volume range (0 to 100)
    VOLUME_MIN = 0
    VOLUME_MAX = 100

    # Valid pitch pattern (+/- followed by number and Hz)
    PITCH_PATTERN = r'^[+-]\d+Hz$'

    @classmethod
    def validate_voice(cls, voice: str) -> str:
        """
        Validate TTS voice name.

        Args:
            voice: Voice name to validate

        Returns:
            Validated voice name

        Raises:
            ValueError: If voice name is invalid
        """
        return InputValidator.validate_string_length(
            voice, min_length=1, max_length=100, field_name="voice"
        )

        # Note: We don't enforce the regex pattern here as voice names
        # can be quite varied across different TTS providers

    @classmethod
    def validate_rate(cls, rate: Union[int, float]) -> Union[int, float]:
        """
        Validate TTS speech rate.

        Args:
            rate: Speech rate to validate

        Returns:
            Validated rate

        Raises:
            ValueError: If rate is out of range
        """
        return InputValidator.validate_numeric_range(
            rate, min_value=cls.RATE_MIN, max_value=cls.RATE_MAX, field_name="rate"
        )

    @classmethod
    def validate_volume(cls, volume: Union[int, float]) -> Union[int, float]:
        """
        Validate TTS volume.

        Args:
            volume: Volume to validate

        Returns:
            Validated volume

        Raises:
            ValueError: If volume is out of range
        """
        return InputValidator.validate_numeric_range(
            volume, min_value=cls.VOLUME_MIN, max_value=cls.VOLUME_MAX, field_name="volume"
        )

    @classmethod
    def validate_pitch(cls, pitch: str) -> str:
        """
        Validate TTS pitch.

        Args:
            pitch: Pitch string to validate

        Returns:
            Validated pitch

        Raises:
            ValueError: If pitch format is invalid
        """
        InputValidator.validate_string_length(
            pitch, min_length=1, max_length=10, field_name="pitch"
        )

        return InputValidator.validate_regex(
            pitch, cls.PITCH_PATTERN, field_name="pitch"
        )


class ConfigValidator:
    """Configuration validation utilities."""

    @staticmethod
    def validate_config_section(config: Dict[str, Any], section_name: str,
                                required_keys: List[str], optional_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate configuration section.

        Args:
            config: Configuration dictionary
            section_name: Name of the configuration section
            required_keys: List of required keys
            optional_keys: List of optional keys

        Returns:
            Validated configuration section

        Raises:
            ValueError: If validation fails
        """
        if section_name not in config:
            raise ValueError(f"Missing configuration section: {section_name}")

        section = config[section_name]
        if not isinstance(section, dict):
            raise ValueError(
                f"Configuration section {section_name} must be a dictionary")

        # Check required keys
        for key in required_keys:
            if key not in section:
                raise ValueError(
                    f"Missing required config key: {section_name}.{key}")

        # Check for unknown keys
        allowed_keys = set(required_keys)
        if optional_keys:
            allowed_keys.update(optional_keys)

        for key in section.keys():
            if key not in allowed_keys:
                raise ValueError(f"Unknown config key: {section_name}.{key}")

        return section


# Convenience functions for common validations
def validate_epub_path(path: Union[str, Path]) -> Path:
    """Validate EPUB file path."""
    return PathValidator.validate_epub_path(path)


def validate_chapter_src(src: str) -> str:
    """Validate chapter source path."""
    return PathValidator.validate_chapter_src(src)


def validate_tts_voice(voice: str) -> str:
    """Validate TTS voice name."""
    return TTSValidator.validate_voice(voice)


def validate_tts_rate(rate: Union[int, float]) -> Union[int, float]:
    """Validate TTS speech rate."""
    return TTSValidator.validate_rate(rate)


def validate_tts_volume(volume: Union[int, float]) -> Union[int, float]:
    """Validate TTS volume."""
    return TTSValidator.validate_volume(volume)


def validate_tts_pitch(pitch: str) -> str:
    """Validate TTS pitch."""
    return TTSValidator.validate_pitch(pitch)


# Example usage and testing
if __name__ == "__main__":
    # Test path validation
    try:
        valid_path = validate_epub_path("test.epub")
        print(f"Valid path: {valid_path}")
    except Exception as e:
        print(f"Path validation error: {e}")

    # Test TTS validation
    try:
        valid_voice = validate_tts_voice("zh-TW")
        valid_rate = validate_tts_rate(50)
        valid_volume = validate_tts_volume(80)
        valid_pitch = validate_tts_pitch("+10Hz")
        print(
            f"TTS validation passed: voice={valid_voice}, rate={valid_rate}, volume={valid_volume}, pitch={valid_pitch}")
    except Exception as e:
        print(f"TTS validation error: {e}")

    print("Validation utilities test completed.")
