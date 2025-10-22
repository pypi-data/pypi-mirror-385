

#!/usr/bin/env python3
"""
TTS integration for SpeakUB
"""

from speakub.utils.text_utils import correct_chinese_pronunciation
from speakub.ui.protocols import AppInterface
from speakub.tts.ui.runners import find_and_play_next_chapter_worker
from speakub.tts.ui.network import NetworkManager
from speakub.tts.playlist_manager import PlaylistManager
from speakub.tts.playback_manager import PlaybackManager
import functools
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

# TTS availability check
try:
    import edge_tts  # noqa: F401

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# gTTS availability check
try:
    from gtts import gTTS  # noqa: F401
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


if TTS_AVAILABLE:
    try:
        from speakub.tts.edge_tts_provider import EdgeTTSProvider
    except Exception:
        EdgeTTSProvider = None

if GTTS_AVAILABLE:
    try:
        from speakub.tts.gtts_provider import GTTSProvider
    except Exception:
        GTTSProvider = None


class TTSIntegration:
    """Handles TTS functionality integration."""

    def __init__(self, app: AppInterface):
        self.app = app

        # Runtime check to ensure the app object conforms to the protocol.
        # This will raise an error if EPUBReaderApp does not correctly implement the properties.
        if not isinstance(app, AppInterface):
            raise ValueError(
                "The 'app' object does not conform to AppInterface protocol."
            )

        self.tts_thread: Optional[threading.Thread] = None
        self.tts_pre_synthesis_thread: Optional[threading.Thread] = None
        self.tts_lock = threading.RLock()
        self.tts_stop_requested = threading.Event()
        with self.tts_lock:
            self.tts_thread_active = False
            self.last_tts_error = None

        self.tts_synthesis_ready = threading.Event()
        self.tts_playback_ready = threading.Event()
        self.tts_data_available = threading.Event()

        self.network_manager = NetworkManager(app)

        # Initialize managers
        self.playlist_manager = PlaylistManager(self)
        self.playback_manager = PlaybackManager(self, self.playlist_manager)

        # Backward compatibility properties
        self.network_error_occurred = self.network_manager.network_error_occurred
        self.network_error_notified = self.network_manager.network_error_notified
        self.network_recovery_notified = self.network_manager.network_recovery_notified

    def reset_network_error_state(self) -> None:
        """Reset network error state (backward compatibility)."""
        self.network_manager.reset_network_error_state()

    async def setup_tts(self) -> None:
        """Set up TTS engine based on configuration."""
        from speakub.utils.config import ConfigManager
        config_mgr = ConfigManager()
        preferred_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

        try:
            if preferred_engine == "gtts" and GTTS_AVAILABLE and GTTSProvider:
                self.app.tts_engine = GTTSProvider()
                logger.info("Using gTTS engine")
            elif TTS_AVAILABLE and EdgeTTSProvider:
                self.app.tts_engine = EdgeTTSProvider()
                logger.info("Using Edge-TTS engine")
            else:
                logger.warning("No TTS engine available")
                return

            if hasattr(self.app.tts_engine, "start_async_loop"):
                self.app.tts_engine.start_async_loop()
        except Exception as e:
            logger.error(f"Failed to setup TTS: {e}")
            self.app.bell()

    async def update_tts_progress(self) -> None:
        """Update TTS progress display."""
        try:
            from textual.widgets import Static

            status_widget = self.app.query_one("#tts-status", Static)
            status = self.app.tts_status.upper()
            smooth = " (Smooth)" if self.app.tts_smooth_mode else ""
            status_text = f"TTS: {status}{smooth}"
            status_widget.update(status_text)

            controls_widget = self.app.query_one("#tts-controls", Static)
            percent = None
            if status == "PLAYING" and self.playlist_manager.has_items():
                total = self.playlist_manager.get_playlist_length()
                current = self.playlist_manager.get_current_index()
                if total > 0 and current < total:
                    percent = int((current / total) * 100)
            p_disp = f"{percent}%" if percent is not None else "--"
            v_disp = f"{self.app.tts_volume}"
            s_disp = f"{self.app.tts_rate:+}"
            controls_text = f"{p_disp} | Vol: {v_disp}% | Speed: {s_disp}% | Pitch: {self.app.tts_pitch}"
            controls_widget.update(controls_text)

            page_widget = self.app.query_one("#tts-page", Static)
            page_text = ""
            if self.app.viewport_content:
                info = self.app.viewport_content.get_viewport_info()
                page_text = f"Page {info['current_page'] + 1}/{info['total_pages']}"
            page_widget.update(page_text)

            # Add debug info for current audio file
            try:
                if self.app.tts_engine and hasattr(self.app.tts_engine, "audio_player"):
                    audio_status = self.app.tts_engine.audio_player.get_status()
                    current_file = audio_status.get("current_file", "None")
                    if current_file and current_file != "None":
                        # Extract just the filename from the path for display
                        import os

                        filename = os.path.basename(current_file)
                        debug_info = f"File: {filename}"
                        # Update the TTS panel with debug info if it exists
                        try:
                            tts_panel = self.app.query_one(
                                "#tts-panel", type=type(None)
                            )
                            if tts_panel and hasattr(tts_panel, "update_status"):
                                # Get current status and add debug info
                                current_status = status_text
                                tts_panel.update_status(
                                    current_status, debug_info)
                        except Exception:
                            pass  # Ignore if panel doesn't exist or doesn't support debug info
            except Exception:
                pass  # Ignore debug info errors

        except Exception:
            import logging

            logging.exception("Error updating TTS progress display")

    def handle_tts_play_pause(self) -> None:
        """Handle TTS play/pause action."""
        with self.tts_lock:
            if self.app.tts_status == "PLAYING":
                self.playback_manager.stop_playback(is_pause=True)
                self.app.tts_status = "PAUSED"
            elif self.app.tts_status == "PAUSED":
                if self.network_manager.network_error_occurred:
                    self.network_manager.reset_network_error_state()
                    self.app.notify(
                        "Restarting TTS playback...",
                        title="TTS Resume",
                        severity="information",
                    )
                self.playback_manager.start_playback()
            elif self.app.tts_status == "STOPPED":
                if self.network_manager.network_error_occurred:
                    self.network_manager.reset_network_error_state()
                self.playlist_manager.generate_playlist()
                if self.playlist_manager.has_items():
                    self.playback_manager.start_playback()
                else:
                    worker_func = functools.partial(
                        find_and_play_next_chapter_worker, self
                    )
                    self.app.run_worker(
                        worker_func, exclusive=True, thread=True)

    def stop_speaking(self, is_pause: bool = False) -> None:
        """Stop TTS playback."""
        self.playback_manager.stop_playback(is_pause=is_pause)
        if not is_pause:
            self.playlist_manager.reset()
            self.last_tts_error = None

    def start_tts_thread(self) -> None:
        """Start TTS playback thread (backward compatibility)."""
        self.playback_manager.start_playback()

    def prepare_tts_playlist(self) -> None:
        """Prepare TTS playlist (backward compatibility)."""
        self.playlist_manager.generate_playlist()

    def speak_with_engine(self, text: str) -> None:
        """Speak text using TTS engine."""
        if not self.app.tts_engine:
            return
        try:
            corrected_text = correct_chinese_pronunciation(text)

            # Check engine type for parameter handling
            from speakub.utils.config import ConfigManager
            config_mgr = ConfigManager()
            current_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

            if current_engine == "gtts":
                # gTTS: use playback speed for rate control
                speed = self._calculate_gtts_speed()
                logger.debug(
                    f"gTTS: Setting speed to {speed:.3f}x for rate {self.app.tts_rate:+}%")
                self.app.tts_engine.set_speed(speed)
                volume = self.app.tts_volume / 100.0
                self.app.tts_engine.set_volume(volume)
                kwargs = {}
            else:
                # Edge-TTS: use traditional parameters
                rate = f"{self.app.tts_rate:+}%"
                volume = f"{self.app.tts_volume - 100:+}%"
                kwargs = {"rate": rate, "volume": volume,
                          "pitch": self.app.tts_pitch}

            if hasattr(self.app.tts_engine, "speak_text_sync"):
                # For EdgeTTS, use async play_audio method
                if hasattr(self.app.tts_engine, "synthesize") and hasattr(self.app.tts_engine, "play_audio"):
                    # Async path for EdgeTTS
                    import asyncio
                    audio_data = asyncio.run(
                        self.app.tts_engine.synthesize(corrected_text, **kwargs))
                    asyncio.run(self.app.tts_engine.play_audio(audio_data))
                else:
                    # Fallback to sync method for gTTS
                    self.app.tts_engine.speak_text_sync(
                        corrected_text, **kwargs)
        except Exception as e:
            raise e

    def _calculate_gtts_speed(self) -> float:
        """
        Calculate playback speed for gTTS based on rate setting.

        基於 Edge-TTS 語速匹配校準（最新實測數據）：
        - Edge-TTS rate = 30% 對應 MPV 播放速度約 1.7~1.8x
        - 因此 Edge-TTS 的 rate 變化對 MPV speed 的影響是 2.5 倍

        rate 範圍: -100 to +100
        speed 範圍: 0.5 to 3.0 (MPV supports up to 3.0x speed, content still understandable)

        計算公式: speed = 1.0 + (rate / 100.0) * 2.5

        範例:
        rate = 0   -> speed = 1.0   (正常)
        rate = +30 -> speed = 1.75  (與 Edge-TTS +30% 匹配，1.7~1.8x 範圍內)
        rate = +50 -> speed = 1.0 + 0.5 * 2.5 = 2.25
        rate = +100 -> speed = 1.0 + 1.0 * 2.5 = 3.5 (但會被限制為 3.0)
        rate = -50 -> speed = 1.0 + (-0.5) * 2.5 = -0.25 (但會被限制為 0.5)
        """
        rate = self.app.tts_rate
        # 基於最新實測校準數據計算轉換係數
        # Edge-TTS 30% 對應 MPV 1.75x，所以係數為 (1.75-1.0)/0.3 ≈ 2.5
        conversion_factor = 2.5
        speed = 1.0 + (rate / 100.0) * conversion_factor
        return max(0.5, min(3.0, speed))

    def cleanup(self) -> None:
        """Clean up TTS resources."""
        # Shut down the playback manager and its thread pool first
        import logging

        try:
            self.playback_manager.shutdown()
        except Exception as e:
            logging.error(f"Error shutting down playback manager: {e}")

        if self.app.tts_status in ["PLAYING", "PAUSED"]:
            try:
                self.stop_speaking(is_pause=False)
            except Exception as e:
                logging.warning(f"Error during stop_speaking on cleanup: {e}")

        # Clean up TTS engine resources
        if self.app.tts_engine:
            try:
                # For gTTS, ensure MPV player is properly terminated
                if hasattr(self.app.tts_engine, "mpv_player") and self.app.tts_engine.mpv_player:
                    try:
                        self.app.tts_engine.mpv_player.stop()
                        self.app.tts_engine.mpv_player.terminate()
                    except Exception as e:
                        logging.warning(f"Error terminating MPV player: {e}")
                    finally:
                        self.app.tts_engine.mpv_player = None

                # Clean up temporary files
                if hasattr(self.app.tts_engine, "_cleanup_current_file"):
                    try:
                        self.app.tts_engine._cleanup_current_file()
                    except Exception as e:
                        logging.warning(f"Error cleaning up temp files: {e}")

                if hasattr(self.app.tts_engine, "stop_async_loop"):
                    try:
                        self.app.tts_engine.stop_async_loop()
                    except Exception as e:
                        logging.warning(
                            f"Error stopping tts_engine async loop: {e}")
            except Exception as e:
                logging.warning(f"Error during TTS engine cleanup: {e}")

        if self.app.tts_widget:
            try:
                self.app.tts_widget.cleanup()
            except Exception as e:
                logging.warning(f"Error cleaning up tts_widget: {e}")
