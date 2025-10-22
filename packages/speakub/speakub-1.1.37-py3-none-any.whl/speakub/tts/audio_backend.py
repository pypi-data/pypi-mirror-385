
#!/usr/bin/env python3
"""
Unified Audio Backend for TTS playback.
Provides a consistent interface for audio playback across different TTS engines.
"""

import logging
import os
import tempfile
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional

try:
    import mpv
    MPV_AVAILABLE = True
except ImportError:
    MPV_AVAILABLE = False
    mpv = None

logger = logging.getLogger(__name__)


class AudioBackend(ABC):
    """Abstract base class for audio playback backends."""

    @abstractmethod
    def play_audio_data(self, audio_data: bytes) -> None:
        """Play audio data synchronously."""
        pass

    @abstractmethod
    def pause(self) -> None:
        """Pause audio playback."""
        pass

    @abstractmethod
    def resume(self) -> None:
        """Resume audio playback."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop audio playback."""
        pass

    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0-1.0)."""
        pass

    @abstractmethod
    def get_volume(self) -> float:
        """Get current volume level (0.0-1.0)."""
        return 0.7

    @abstractmethod
    def set_speed(self, speed: float) -> None:
        """Set playback speed (0.5-3.0)."""
        pass

    @abstractmethod
    def get_speed(self) -> float:
        """Get current playback speed."""
        return 1.0

    @abstractmethod
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return False

    @abstractmethod
    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        return False

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass


class MPVAudioBackend(AudioBackend):
    """MPV-based unified audio backend for consistent playback across TTS engines."""

    def __init__(self):
        if not MPV_AVAILABLE:
            raise ImportError(
                "python-mpv not installed. Install with: pip install python-mpv"
            )

        self.mpv_player = None
        self._current_file: Optional[str] = None
        self._is_paused = False
        self._volume = 0.7
        self._speed = 1.0
        self._lock = threading.RLock()
        self._playback_complete_event = threading.Event()
        self._playback_thread: Optional[threading.Thread] = None

    def _ensure_player(self):
        """Ensure MPV player is initialized."""
        with self._lock:
            if self.mpv_player is None:
                self.mpv_player = mpv.MPV()  # type: ignore
                # Set initial values
                self.mpv_player.volume = self._volume * 100
                self.mpv_player.speed = self._speed
                logger.debug("MPV player initialized")

    def play_audio_data(self, audio_data: bytes) -> None:
        """Play audio data using MPV with proper completion handling."""
        with self._lock:
            self._ensure_player()

            # Clean up previous file if exists
            self._cleanup_current_file()

            # Reset completion event
            self._playback_complete_event.clear()

            # Write audio data to temporary file
            fd, temp_file = tempfile.mkstemp(suffix='.mp3')
            try:
                with os.fdopen(fd, 'wb') as f:
                    f.write(audio_data)
                self._current_file = temp_file
                logger.debug(f"Created temp audio file: {temp_file}")

                # Start playback in a separate thread to allow immediate control
                self._playback_thread = threading.Thread(
                    target=self._play_and_wait_for_completion,
                    name="MPVPlaybackThread"
                )
                self._playback_thread.daemon = True
                self._playback_thread.start()

                logger.debug(
                    "Audio playback started (non-blocking with completion tracking)")

            except Exception as e:
                logger.error(f"Error playing audio data: {e}")
                self._cleanup_current_file()
                raise

    def _play_and_wait_for_completion(self) -> None:
        """Play audio and wait for completion using a robust polling loop."""
        try:
            if self.mpv_player and self._current_file:
                self.mpv_player.loadfile(self._current_file)
                self.mpv_player.pause = False
                self._is_paused = False

                logger.debug("EdgeTTS-Backend: Starting playback.")

                # 主動詢問迴圈
                while True:
                    with self._lock:
                        if not self.mpv_player:
                            logger.debug(
                                "EdgeTTS-Backend: Player gone, exiting loop.")
                            break
                        if self.mpv_player.idle_active:
                            logger.debug(
                                "EdgeTTS-Backend: Playback completed (player is idle).")
                            break

                    if not self._current_file:
                        logger.debug(
                            "EdgeTTS-Backend: Playback interrupted by stop (file cleaned).")
                        break

                    # 檢查是否被暫停，如果是則退出迴圈等待恢復
                    if self._is_paused:
                        logger.debug(
                            "EdgeTTS-Backend: Playback paused, exiting loop for resume.")
                        break

                    time.sleep(0.1)

                self._playback_complete_event.set()
                logger.debug("EdgeTTS-Backend: Signaled playback completion.")

        except Exception as e:
            logger.error(f"Error in unified backend playback thread: {e}")
            self._playback_complete_event.set()

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for current playback to complete."""
        return self._playback_complete_event.wait(timeout=timeout)

    def pause(self) -> None:
        """Pause audio playback."""
        with self._lock:
            if self.mpv_player and self._current_file:
                self.mpv_player.pause = True
                self._is_paused = True
                logger.debug("Audio playback paused")

    def resume(self) -> None:
        """Resume audio playback."""
        with self._lock:
            if self.mpv_player and self._current_file and self._is_paused:
                self.mpv_player.pause = False
                self._is_paused = False
                logger.debug("Audio playback resumed")

    def stop(self) -> None:
        """Stop audio playback."""
        with self._lock:
            if self.mpv_player:
                self.mpv_player.stop()
            # Signal completion to unblock any waiting threads
            self._playback_complete_event.set()
            self._is_paused = False
            self._cleanup_current_file()
            logger.debug("Audio playback stopped")

    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0-1.0)."""
        with self._lock:
            self._volume = max(0.0, min(1.0, volume))
            if self.mpv_player:
                self.mpv_player.volume = self._volume * 100
            logger.debug(f"Volume set to {self._volume}")

    def get_volume(self) -> float:
        """Get current volume level (0.0-1.0)."""
        with self._lock:
            return self._volume

    def set_speed(self, speed: float) -> None:
        """Set playback speed (0.5-3.0)."""
        with self._lock:
            self._speed = max(0.5, min(3.0, speed))
            if self.mpv_player:
                self.mpv_player.speed = self._speed
            logger.debug(f"Speed set to {self._speed}")

    def get_speed(self) -> float:
        """Get current playback speed."""
        with self._lock:
            return self._speed

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        with self._lock:
            return (self.mpv_player is not None and
                    self._current_file is not None and
                    not self._is_paused)

    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        with self._lock:
            return (self.mpv_player is not None and
                    self._current_file is not None and
                    self._is_paused)

    def _cleanup_current_file(self) -> None:
        """Clean up the current temporary audio file."""
        if self._current_file and os.path.exists(self._current_file):
            try:
                os.unlink(self._current_file)
                logger.debug(f"Cleaned up temp file: {self._current_file}")
            except Exception as e:
                logger.warning(
                    f"Failed to clean up temp file {self._current_file}: {e}")
        self._current_file = None

    def cleanup(self) -> None:
        """Clean up all resources."""
        with self._lock:
            if self.mpv_player:
                try:
                    self.mpv_player.stop()
                    self.mpv_player.terminate()
                    logger.debug("MPV player terminated")
                except Exception as e:
                    logger.warning(f"Error terminating MPV player: {e}")
                finally:
                    self.mpv_player = None

            self._cleanup_current_file()
            self._is_paused = False
