
"""
Application interface definitions.
"""

from abc import ABC, abstractmethod
from typing import Optional

from speakub.tts.edge_tts_provider import EdgeTTSProvider


class AppInterface(ABC):
    """Interface for the main application."""

    @property
    @abstractmethod
    def tts_engine(self) -> Optional["EdgeTTSProvider"]:
        """Get the TTS engine."""
        pass

    @tts_engine.setter
    @abstractmethod
    def tts_engine(self, value: Optional["EdgeTTSProvider"]) -> None:
        """Set the TTS engine."""
        pass

    @property
    @abstractmethod
    def tts_status(self) -> str:
        """Get the TTS status."""
        pass

    @tts_status.setter
    @abstractmethod
    def tts_status(self, value: str) -> None:
        """Set the TTS status."""
        pass

    @property
    @abstractmethod
    def tts_smooth_mode(self) -> bool:
        """Get the TTS smooth mode."""
        pass

    @tts_smooth_mode.setter
    @abstractmethod
    def tts_smooth_mode(self, value: bool) -> None:
        """Set the TTS smooth mode."""
        pass

    @property
    @abstractmethod
    def tts_volume(self) -> int:
        """Get the TTS volume."""
        pass

    @property
    @abstractmethod
    def tts_rate(self) -> int:
        """Get the TTS rate."""
        pass

    @property
    @abstractmethod
    def tts_pitch(self) -> str:
        """Get the TTS pitch."""
        pass

    @property
    @abstractmethod
    def tts_widget(self) -> Optional["TTSRichWidget"]:
        """Get the TTS widget."""
        pass

    @property
    @abstractmethod
    def now_reading_text(self) -> str:
        """Get the current reading text."""
        pass

    @abstractmethod
    def notify(self, message: str, title: Optional[str] = None, severity: str = "information") -> None:
        """Show a notification."""
        pass

    @abstractmethod
    def run_worker(self, coro, exclusive: bool = False, thread: bool = False):
        """Run a worker coroutine."""
        pass

    @abstractmethod
    def bell(self) -> None:
        """Ring the bell."""
        pass
