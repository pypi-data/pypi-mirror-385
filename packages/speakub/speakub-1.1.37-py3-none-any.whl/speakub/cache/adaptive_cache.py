
"""
Adaptive cache implementation extracted from content_renderer.
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AdaptiveCache:
    """Adaptive caching with memory and size limits."""

    def __init__(self, max_size: int, ttl: int = 300,
                 max_memory_mb: int = 100):
        self.max_size = max_size
        self.ttl = ttl
        self.max_memory_mb = max_memory_mb
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._cleanup_interval = 60  # seconds
        self._last_cleanup = time.time()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if it exists and hasn't expired."""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                self.access_times[key] = time.time()
                self._hit_count += 1
                return entry['value']
            else:
                # Expired entry
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]

        self._miss_count += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cache value."""
        current_time = time.time()

        # Check if we need cleanup
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_expired()

        # Check memory usage (rough estimate)
        if self._estimate_memory_usage() > self.max_memory_mb * 1024 * 1024:
            self._evict_least_recently_used()

        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_least_recently_used()

        self.cache[key] = {
            'value': value,
            'timestamp': current_time
        }
        self.access_times[key] = current_time

    def get_stats(self) -> Dict[str, float]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if time.time() - entry['timestamp'] >= self.ttl
        )

        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0

        return {
            'size': total_entries,
            'max_size': self.max_size,
            'expired_entries': expired_entries,
            'hit_rate': hit_rate,
            'hits': self._hit_count,
            'misses': self._miss_count,
            'memory_usage_mb': self._estimate_memory_usage() / (1024 * 1024)
        }

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]

        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]

        self._last_cleanup = current_time

    def _evict_least_recently_used(self) -> None:
        """Evict least recently used entries."""
        if not self.access_times:
            return

        # Find least recently used key
        lru_key = min(self.access_times, key=self.access_times.get)

        del self.cache[lru_key]
        del self.access_times[lru_key]

    def _estimate_memory_usage(self) -> int:
        """Rough estimate of memory usage in bytes."""
        # Very rough estimate: assume average 1KB per entry
        return len(self.cache) * 1024

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
