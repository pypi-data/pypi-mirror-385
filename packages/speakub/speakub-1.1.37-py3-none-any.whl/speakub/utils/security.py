
"""
Security utilities for SpeakUB.
"""

from pathlib import Path
from typing import Union


class PathValidator:
    """Unified path security validation."""

    @staticmethod
    def validate_epub_path(path: Union[str, Path],
                           allow_test_paths: bool = False) -> Path:
        """Validate EPUB file path."""
        resolved = Path(path).resolve()

        # Allow test paths in testing environment
        if allow_test_paths and str(resolved).startswith("/tmp/"):
            pass  # Skip home directory check for tests
        elif not resolved.is_relative_to(Path.home()):
            raise ValueError(f"Path outside home directory: {path}")

        # Must be a file and exist (skip for test paths)
        if not allow_test_paths and not resolved.is_file():
            raise FileNotFoundError(f"EPUB file not found: {path}")

        return resolved

    @staticmethod
    def validate_chapter_path(path: str) -> str:
        """Validate chapter internal path."""
        if ".." in path or path.startswith("/"):
            raise ValueError(f"Path traversal attempt: {path}")

        # Normalize path
        normalized = Path(path).as_posix()
        return normalized
