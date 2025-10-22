
#!/usr/bin/env python3
"""
TTS synthesis cache for SpeakUB.
Caches synthesized audio to improve performance and reduce API calls.
"""

import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class SynthesisCache:
    """TTS synthesis result cache with LRU eviction."""

    def __init__(self, max_size_mb: int = 100, cache_dir: Optional[str] = None):
        """
        Initialize synthesis cache.

        Args:
            max_size_mb: Maximum cache size in MB
            cache_dir: Cache directory path (defaults to ~/.speakub_tts_cache)
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024

        if cache_dir is None:
            self.cache_dir = Path.home() / '.speakub_tts_cache'
        else:
            self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache index: key -> (file_path, size, access_time)
        self._cache_index: Dict[str, Tuple[Path, int, float]] = {}

        # Load existing cache on initialization
        self._load_cache_index()

        # Clean up on startup
        self._cleanup_cache()

    def _generate_key(self, text: str, voice: str, rate: int, pitch: str = "+0Hz") -> str:
        """
        Generate cache key from synthesis parameters.

        Args:
            text: Text to synthesize
            voice: Voice identifier
            rate: Speech rate
            pitch: Voice pitch

        Returns:
            Cache key string
        """
        # Create a hash of the input parameters
        key_data = f"{text}|{voice}|{rate}|{pitch}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()

    def get_cached_audio(self, text: str, voice: str, rate: int,
                         pitch: str = "+0Hz") -> Optional[bytes]:
        """
        Get cached audio data if available.

        Args:
            text: Text to synthesize
            voice: Voice identifier
            rate: Speech rate
            pitch: Voice pitch

        Returns:
            Cached audio data as bytes, or None if not found
        """
        cache_key = self._generate_key(text, voice, rate, pitch)

        if cache_key not in self._cache_index:
            return None

        file_path, size, _ = self._cache_index[cache_key]

        # Check if file still exists
        if not file_path.exists():
            del self._cache_index[cache_key]
            return None

        try:
            # Update access time
            current_time = os.path.getmtime(file_path)
            self._cache_index[cache_key] = (file_path, size, current_time)

            # Read and return audio data
            with open(file_path, 'rb') as f:
                return f.read()

        except (IOError, OSError) as e:
            logger.warning(
                f"Failed to read cached audio file {file_path}: {e}")
            # Remove corrupted entry
            if cache_key in self._cache_index:
                del self._cache_index[cache_key]
            return None

    def cache_audio(self, text: str, voice: str, rate: int,
                    audio_data: bytes, pitch: str = "+0Hz") -> bool:
        """
        Cache audio data.

        Args:
            text: Text that was synthesized
            voice: Voice identifier used
            rate: Speech rate used
            audio_data: Audio data to cache
            pitch: Voice pitch used

        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = self._generate_key(text, voice, rate, pitch)

        # Check if we would exceed cache size
        data_size = len(audio_data)
        if self._get_current_cache_size() + data_size > self.max_size_bytes:
            self._evict_old_entries(data_size)

        # Generate unique filename
        filename = f"{cache_key}.mp3"
        file_path = self.cache_dir / filename

        try:
            # Write audio data to file
            with open(file_path, 'wb') as f:
                f.write(audio_data)

            # Update cache index
            current_time = os.path.getmtime(file_path)
            self._cache_index[cache_key] = (file_path, data_size, current_time)

            logger.debug(f"Cached TTS audio: {cache_key} ({data_size} bytes)")
            return True

        except (IOError, OSError) as e:
            logger.error(f"Failed to cache audio file {file_path}: {e}")
            # Clean up partial file if it exists
            if file_path.exists():
                try:
                    file_path.unlink()
                except OSError:
                    pass
            return False

    def _load_cache_index(self) -> None:
        """Load existing cache index from disk."""
        index_file = self.cache_dir / 'cache_index.json'

        if not index_file.exists():
            return

        try:
            import json
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            for key, (path_str, size, access_time) in index_data.items():
                file_path = Path(path_str)
                if file_path.exists():
                    self._cache_index[key] = (file_path, size, access_time)
                else:
                    logger.debug(f"Cached file no longer exists: {file_path}")

        except (IOError, OSError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to load cache index: {e}")

    def _save_cache_index(self) -> None:
        """Save cache index to disk."""
        index_file = self.cache_dir / 'cache_index.json'

        try:
            import json
            index_data = {
                key: (str(path), size, access_time)
                for key, (path, size, access_time) in self._cache_index.items()
            }

            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

        except (IOError, OSError) as e:
            logger.error(f"Failed to save cache index: {e}")

    def _get_current_cache_size(self) -> int:
        """Get current total cache size in bytes."""
        return sum(size for _, size, _ in self._cache_index.values())

    def _evict_old_entries(self, required_space: int) -> None:
        """
        Evict old entries to make space for new data.

        Args:
            required_space: Space needed in bytes
        """
        # Sort by access time (oldest first)
        sorted_entries = sorted(
            self._cache_index.items(),
            key=lambda x: x[1][2]  # access_time
        )

        freed_space = 0
        entries_to_remove = []

        for key, (file_path, size, _) in sorted_entries:
            if freed_space >= required_space:
                break

            # Remove file
            try:
                if file_path.exists():
                    file_path.unlink()
                freed_space += size
                entries_to_remove.append(key)
            except OSError as e:
                logger.warning(
                    f"Failed to remove cached file {file_path}: {e}")

        # Remove from index
        for key in entries_to_remove:
            del self._cache_index[key]

        logger.debug(f"Evicted {len(entries_to_remove)} cache entries, "
                     f"freed {freed_space} bytes")

    def _cleanup_cache(self) -> None:
        """Clean up orphaned cache files and invalid entries."""
        # Remove files that exist but aren't in index
        valid_files = {path for path, _, _ in self._cache_index.values()}

        orphaned_files = []
        for file_path in self.cache_dir.glob('*.mp3'):
            if file_path not in valid_files:
                try:
                    file_path.unlink()
                    orphaned_files.append(file_path)
                except OSError:
                    pass

        if orphaned_files:
            logger.debug(f"Removed {len(orphaned_files)} orphaned cache files")

        # Remove index entries for files that no longer exist
        invalid_keys = []
        for key, (file_path, _, _) in self._cache_index.items():
            if not file_path.exists():
                invalid_keys.append(key)

        for key in invalid_keys:
            del self._cache_index[key]

        if invalid_keys:
            logger.debug(f"Removed {len(invalid_keys)} invalid cache entries")

        # Save updated index
        self._save_cache_index()

    def clear_cache(self) -> None:
        """Clear all cached data."""
        # Remove all cache files
        for file_path in self.cache_dir.glob('*.mp3'):
            try:
                file_path.unlink()
            except OSError:
                pass

        # Clear index and remove index file
        self._cache_index.clear()
        index_file = self.cache_dir / 'cache_index.json'
        if index_file.exists():
            try:
                index_file.unlink()
            except OSError:
                pass

        logger.info("TTS synthesis cache cleared")

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_size = self._get_current_cache_size()
        num_entries = len(self._cache_index)

        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'num_entries': num_entries,
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'cache_dir': str(self.cache_dir),
            'hit_rate': 0.0,  # Would need to track hits/misses separately
        }

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self._save_cache_index()
        except Exception:
            pass  # Ignore errors during cleanup
