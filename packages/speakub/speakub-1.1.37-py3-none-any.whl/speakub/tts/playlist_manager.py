

"""
Playlist Manager for TTS in SpeakUB.
Handles playlist generation and indexing.
"""

import logging
from collections import deque
from typing import TYPE_CHECKING, List, Tuple, Union

from speakub.tts.ui.playlist import prepare_tts_playlist, tts_load_next_chapter

if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration

logger = logging.getLogger(__name__)


class PlaylistBuffer:
    """Buffer for playlist items to optimize memory usage and access patterns."""

    def __init__(self, max_size: int = 100, max_memory_mb: int = 50):
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._current_memory = 0
        self.current_index = 0

    def append(self, item: Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]]]) -> None:
        """Add item to buffer, maintaining max size and memory limits."""
        import sys
        item_size = sys.getsizeof(item)

        # Remove old items if necessary to stay within memory limits
        while self._current_memory + item_size > self.max_memory_bytes and self.buffer:
            removed = self.buffer.popleft()
            self._current_memory -= sys.getsizeof(removed)

        self.buffer.append(item)
        self._current_memory += item_size

    def get_item_at(self, index: int) -> Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]], None]:
        """Get item at specific index, handling buffer offset."""
        buffer_index = index - \
            (len(self.buffer) - self.max_size if len(self.buffer) >= self.max_size else 0)
        if 0 <= buffer_index < len(self.buffer):
            return self.buffer[buffer_index]
        return None

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self._current_memory = 0
        self.current_index = 0

    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        return self._current_memory

    def __len__(self) -> int:
        return len(self.buffer)


class PlaylistManager:
    """Manages TTS playlist generation and indexing."""

    def __init__(self, tts_integration: "TTSIntegration"):
        self.tts_integration = tts_integration
        self.app = tts_integration.app
        self.playlist: List[
            Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]]]
        ] = []
        self.current_index: int = 0
        self.buffer = PlaylistBuffer(max_size=50)  # Buffer for recent items

    def generate_playlist(self) -> None:
        """Generate TTS playlist from current content."""
        # The prepare_tts_playlist function will now populate self.playlist directly.
        with self.tts_integration.tts_lock:
            prepare_tts_playlist(self)

    def load_next_chapter(self) -> bool:
        """Load next chapter for TTS."""
        # The tts_load_next_chapter function will now operate on this manager.
        return tts_load_next_chapter(self)

    def get_current_item(
        self,
    ) -> Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]], None]:
        """Get current playlist item."""
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

    def get_item_at(
        self, index: int
    ) -> Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]], None]:
        """Get playlist item at a specific index."""
        if 0 <= index < len(self.playlist):
            return self.playlist[index]
        return None

    def buffer_item(self, item: Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]]]) -> None:
        """Add item to buffer for quick access."""
        self.buffer.append(item)

    def update_item_at(self, index: int, item: Tuple) -> None:
        """Update a playlist item at a specific index, e.g., with synthesized audio."""
        if 0 <= index < len(self.playlist):
            self.playlist[index] = item

    def advance_index(self) -> None:
        """Advance playlist index."""
        self.current_index += 1

    def is_exhausted(self) -> bool:
        """Check if playlist is exhausted."""
        return self.current_index >= len(self.playlist)

    def has_items(self) -> bool:
        """Check if the playlist has any items."""
        return len(self.playlist) > 0

    def get_playlist_length(self) -> int:
        """Return the total number of items in the playlist."""
        return len(self.playlist)

    def get_current_index(self) -> int:
        """Return the current playlist index."""
        return self.current_index

    def reset(self) -> None:
        """Reset playlist and index."""
        self.playlist = []
        self.current_index = 0
        self.buffer.clear()
