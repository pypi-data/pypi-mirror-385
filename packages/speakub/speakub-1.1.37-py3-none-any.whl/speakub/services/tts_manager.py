
"""
TTS Manager service for handling TTS operations.
"""

import asyncio
import logging
from typing import Optional

from speakub.interfaces.app_interface import AppInterface
from speakub.services.configuration_service import ConfigurationService
from speakub.tts.engine import TTSEngine
from speakub.utils.text_utils import correct_chinese_pronunciation

logger = logging.getLogger(__name__)


class TTSManager:
    """Manages TTS operations and engine lifecycle."""

    def __init__(self, app: AppInterface):
        self.app = app
        self.config_service = ConfigurationService()
        self._tts_engine: Optional[TTSEngine] = None

    @property
    def tts_engine(self) -> Optional[TTSEngine]:
        """Get the TTS engine."""
        return self._tts_engine

    @tts_engine.setter
    def tts_engine(self, value: Optional[TTSEngine]) -> None:
        """Set the TTS engine."""
        self._tts_engine = value

    async def setup_tts_engine(self) -> None:
        """Set up TTS engine based on configuration."""
        preferred_engine = self.config_service.get(
            "tts.preferred_engine", "edge-tts")

        try:
            if preferred_engine == "gtts":
                # Check if gTTS is available
                try:
                    from gtts import gTTS  # noqa: F401
                    from speakub.tts.gtts_provider import GTTSProvider
                    self.tts_engine = GTTSProvider()
                    logger.info("Using gTTS engine")
                except ImportError:
                    logger.warning(
                        "gTTS not available, falling back to Edge-TTS")
                    self._setup_edge_tts()
            else:
                self._setup_edge_tts()

            if self.tts_engine and hasattr(self.tts_engine, "start_async_loop"):
                self.tts_engine.start_async_loop()

        except Exception as e:
            logger.error(f"Failed to setup TTS: {e}")
            self.app.bell()

    def _setup_edge_tts(self) -> None:
        """Set up Edge-TTS engine."""
        try:
            import edge_tts  # noqa: F401
            from speakub.tts.edge_tts_provider import EdgeTTSProvider
            self.tts_engine = EdgeTTSProvider()
            logger.info("Using Edge-TTS engine")
        except ImportError:
            logger.warning("Edge-TTS not available")

    async def speak_text(self, text: str) -> None:
        """Speak text using the configured TTS engine."""
        if not self.tts_engine:
            return

        try:
            corrected_text = correct_chinese_pronunciation(text)
            kwargs = self._get_tts_parameters()

            if hasattr(self.tts_engine, "speak_text_sync"):
                # For EdgeTTS, use async play_audio method
                if hasattr(self.tts_engine, "synthesize") and hasattr(self.tts_engine, "play_audio"):
                    # Async path for EdgeTTS
                    audio_data = await self.tts_engine.synthesize(corrected_text, **kwargs)
                    await self.tts_engine.play_audio(audio_data)
                else:
                    # Fallback to sync method for gTTS
                    self.tts_engine.speak_text_sync(corrected_text, **kwargs)
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            raise

    def _get_tts_parameters(self) -> dict:
        """Get TTS parameters based on engine type."""
        current_engine = self.config_service.get(
            "tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS: use playback speed for rate control
            speed = self._calculate_gtts_speed()
            logger.debug(
                f"gTTS: Setting speed to {speed:.3f}x for rate {self.app.tts_rate:+}%")
            if hasattr(self.tts_engine, "set_speed"):
                self.tts_engine.set_speed(speed)
            if hasattr(self.tts_engine, "set_volume"):
                volume = self.app.tts_volume / 100.0
                self.tts_engine.set_volume(volume)
            return {}
        else:
            # Edge-TTS: use traditional parameters
            rate = f"{self.app.tts_rate:+}%"
            volume = f"{self.app.tts_volume - 100:+}%"
            return {"rate": rate, "volume": volume, "pitch": self.app.tts_pitch}

    def _calculate_gtts_speed(self) -> float:
        """
        Calculate playback speed for gTTS based on rate setting.
        """
        rate = self.app.tts_rate
        conversion_factor = 2.5
        speed = 1.0 + (rate / 100.0) * conversion_factor
        return max(0.5, min(3.0, speed))

    def cleanup(self) -> None:
        """Clean up TTS resources."""
        if self.tts_engine:
            try:
                # Clean up temporary files
                if hasattr(self.tts_engine, "_cleanup_current_file"):
                    self.tts_engine._cleanup_current_file()

                if hasattr(self.tts_engine, "stop_async_loop"):
                    self.tts_engine.stop_async_loop()
            except Exception as e:
                logger.warning(
                    f"Error during TTS engine cleanup: {e}")
