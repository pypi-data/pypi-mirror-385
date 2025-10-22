
#!/usr/bin/env python3
"""
gTTS Provider - Google Text-to-Speech implementation.
"""

import asyncio
import logging
import os
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import mpv
    MPV_AVAILABLE = True
except ImportError:
    MPV_AVAILABLE = False

from speakub.tts.engine import TTSEngine, TTSState

logger = logging.getLogger(__name__)


class GTTSProvider(TTSEngine):
    """Google Text-to-Speech provider."""

    # 預定義的中文女性語音
    FEMALE_CHINESE_VOICES = [
        {
            "name": "Google TTS - Chinese (Mandarin, Simplified)",
            "short_name": "gtts-zh-CN",
            "gender": "Female",
            "locale": "zh-CN",
            "display_name": "Chinese (Simplified)",
            "local_name": "中文（簡體）",
        },
        {
            "name": "Google TTS - Chinese (Mandarin, Traditional)",
            "short_name": "gtts-zh-TW",
            "gender": "Female",
            "locale": "zh-TW",
            "display_name": "Chinese (Traditional)",
            "local_name": "中文（繁體）",
        },
        {
            "name": "Google TTS - Chinese (Mandarin)",
            "short_name": "gtts-zh",
            "gender": "Female",
            "locale": "zh",
            "display_name": "Chinese (Mandarin)",
            "local_name": "中文（普通話）",
        },
    ]

    def __init__(self):
        """Initialize gTTS provider."""
        super().__init__()
        if not GTTS_AVAILABLE:
            raise ImportError(
                "gtts not installed. Install with: pip install gtts")
        if not MPV_AVAILABLE:
            raise ImportError(
                "python-mpv not installed. Install with: pip install python-mpv")

        # Use MPV player for gTTS instead of pygame
        self.mpv_player = None

        # ⭐ 從配置載入初始語音設定 - 使用全域配置管理器
        from speakub.utils.config import get_config

        initial_voice = get_config("tts.gtts.default_voice", "gtts-zh-TW")
        self._current_voice = initial_voice
        logger.debug(f"gTTS initialized with voice: {initial_voice}")

        # State tracking
        self._audio_state = TTSState.IDLE
        self._state_lock = threading.Lock()
        self._current_audio_file: Optional[str] = None
        self._is_paused: bool = False
        self._shutdown_event = threading.Event()
        self._temp_file_lock = threading.Lock()  # 保護檔案操作

        # ⭐ 從配置載入初始音量和速度 - 使用全域配置管理器
        initial_volume = get_config("tts.volume", 100) / 100.0
        self._current_volume = initial_volume
        logger.debug(f"gTTS initialized with volume: {initial_volume}")

        # 計算初始速度
        initial_rate = get_config("tts.rate", 0)
        self._current_speed = 1.0 + (initial_rate / 100.0)
        logger.debug(f"gTTS initialized with speed: {self._current_speed}")

        # ⭐ 新增：初始化持久 MPV 播放器實例以支援即時音量控制
        try:
            self.mpv_player = mpv.MPV()
            # 設定初始音量和速度
            self.mpv_player.volume = self._current_volume * 100
            self.mpv_player.speed = self._current_speed
            logger.debug(
                "Persistent MPV player initialized for real-time volume control")
        except Exception as e:
            logger.warning(f"Failed to initialize persistent MPV player: {e}")
            self.mpv_player = None

    def _transition_state(self, new_state: TTSState) -> bool:
        """Safe state transition with validation."""
        with self._state_lock:
            valid_transitions = {
                TTSState.IDLE: {TTSState.LOADING, TTSState.ERROR},
                TTSState.LOADING: {TTSState.PLAYING, TTSState.STOPPED, TTSState.ERROR},
                TTSState.PLAYING: {TTSState.PAUSED, TTSState.STOPPED, TTSState.ERROR},
                TTSState.PAUSED: {TTSState.PLAYING, TTSState.STOPPED, TTSState.ERROR},
                TTSState.STOPPED: {TTSState.IDLE, TTSState.LOADING},
                TTSState.ERROR: {TTSState.IDLE, TTSState.STOPPED},
            }
            if new_state in valid_transitions.get(self._audio_state, set()):
                old_state = self._audio_state
                self._audio_state = new_state
                logger.info(
                    f"gTTS state transition: {old_state.value} -> {new_state.value}")
                return True
            else:
                logger.warning(
                    f"Invalid gTTS state transition: {self._audio_state.value} -> {new_state.value}")
                return False

    def _update_state(self, new_state: TTSState) -> None:
        """Update state without validation (for monitoring)."""
        with self._state_lock:
            old_state = self._audio_state
            self._audio_state = new_state
            logger.debug(
                f"TTS state updated: {old_state.value} -> {new_state.value} | "
                f"file={self._current_audio_file or 'None'} | paused={self._is_paused}"
            )

    def get_current_state(self) -> str:
        """Get current state."""
        with self._state_lock:
            return self._audio_state.value

    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text using gTTS.
        Note: gTTS does not support rate, pitch, volume in synthesis.
        These are controlled during playback.
        """
        if not GTTS_AVAILABLE:
            raise RuntimeError("gTTS not available")

        # ⭐ 修復：確保文本不為空
        if not text or not text.strip():
            logger.warning("Empty text provided to synthesize")
            return b""

        if voice == "default":
            voice = self._current_voice

        # Extract language code from voice name
        lang = voice.split('-')[-1]  # e.g., "gtts-zh-TW" -> "TW"
        tld = "com"
        if lang == "TW":
            lang = "zh-TW"  # Keep original format as gTTS expects it
            tld = "com.tw"
        elif lang == "CN":
            lang = "zh-CN"  # Keep original format as gTTS expects it
            tld = "com"
        elif lang == "zh":
            lang = "zh"  # Keep as is for general Chinese
            tld = "com"

        logger.debug(
            f"Synthesizing text: '{text[:50]}...' with voice: {voice}, lang: {lang}")

        # Generate speech with warning suppression
        import warnings
        import logging
        # Temporarily suppress gtts.lang logger warnings
        gtts_logger = logging.getLogger('gtts.lang')
        original_level = gtts_logger.level
        gtts_logger.setLevel(logging.ERROR)  # Suppress warnings

        try:
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        finally:
            # Restore original logging level
            gtts_logger.setLevel(original_level)

        # Save to temporary file and read bytes
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_file = f.name
            tts.save(temp_file)

        try:
            # ⭐ 修復：確保文件被完整寫入
            with open(temp_file, 'rb') as f:
                audio_data = f.read()

            # ⭐ 修復：驗證音頻數據是否有效
            if len(audio_data) == 0:
                logger.error("Generated audio file is empty")
                raise RuntimeError("Failed to generate audio: empty file")

            logger.debug(f"Generated audio file size: {len(audio_data)} bytes")

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

        return audio_data

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available gTTS voices (pre-defined)."""
        return self.FEMALE_CHINESE_VOICES.copy()

    def get_voices_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get voices for a specific language."""
        return [
            voice for voice in self.FEMALE_CHINESE_VOICES
            if voice["locale"].startswith(language)
        ]

    def set_voice(self, voice_name: str) -> bool:
        """Set the current voice."""
        if not voice_name or not voice_name.startswith("gtts-"):
            return False
        # Validate voice
        valid_voices = [v["short_name"] for v in self.FEMALE_CHINESE_VOICES]
        if voice_name in valid_voices:
            self._current_voice = voice_name
            return True
        return False

    def get_current_voice(self) -> str:
        """Get the currently selected voice."""
        return self._current_voice

    async def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data using MPV player.
        ⭐ 核心修復：修正檔案生命週期管理
        - 新段落：總是建立新檔案
        - 暫停恢復：重用現有檔案
        """
        logger.debug("Starting new audio segment playback")

        # ⭐ 重要：在開始新播放前確保之前的播放已完成
        # 如果正在播放，等待完成
        if self.get_current_state() == "playing":
            logger.debug("Waiting for current playback to complete...")
            # 為了確保順序播放，我們選擇等待

        # 重置停止標誌（為新播放做準備）
        self._shutdown_event.clear()

        # Update state: starting new playback
        self._update_state(TTSState.LOADING)

        # ⭐ 關鍵修改：檔案生命週期管理
        with self._temp_file_lock:
            # 只有在非暫停狀態時才建立新檔案
            if not self._is_paused or not self._current_audio_file:
                # 清理舊檔案（如果有）
                self._cleanup_current_file()

                # 創建新臨時檔案
                fd, temp_path = tempfile.mkstemp(suffix=".mp3")
                try:
                    with os.fdopen(fd, "wb") as f:
                        f.write(audio_data)
                    self._current_audio_file = temp_path
                    logger.debug(f"Created new audio segment: {temp_path}")
                except Exception as e:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    raise e
            else:
                # 暫停恢復：重用現有檔案
                logger.debug(
                    f"Reusing existing audio file: {self._current_audio_file}")

        # Update state: ready to play
        self._update_state(TTSState.PLAYING)

        # Reset pause flag for new segment
        self._is_paused = False

        # Play the audio segment (blocks until complete)
        await asyncio.to_thread(self._play_and_wait)

        # Clean up after playback completes (only if not paused)
        if not self._is_paused:
            self._cleanup_current_file()
            self._update_state(TTSState.IDLE)
            logger.debug("Audio segment completed, ready for next segment")

    def _play_and_wait(self) -> None:
        """
        Play audio and wait for completion using a robust polling loop.
        This correctly handles the pause/resume cycle by not blocking indefinitely.
        """
        try:
            if not self.mpv_player:
                self.mpv_player = mpv.MPV()
                self.mpv_player.volume = self._current_volume * 100
                self.mpv_player.speed = self._current_speed

            self.mpv_player.loadfile(self._current_audio_file)
            self.mpv_player.pause = False

            start_time = time.time()
            logger.debug(
                f"gTTS: Starting playback at {time.ctime(start_time)}")

            # 主動詢問迴圈，代替 wait_for_playback()
            while not self._shutdown_event.is_set():
                if self.mpv_player.idle_active:
                    logger.debug("gTTS: Playback completed (player is idle).")
                    break

                if self.get_current_state() == "stopped":
                    logger.debug("gTTS: Playback interrupted by stop signal.")
                    break

                if self.get_current_state() == "paused":
                    logger.debug(
                        "gTTS: Playback paused, exiting loop for resume.")
                    break

                time.sleep(0.1)  # 短暫休眠，避免過度消耗 CPU

            elapsed = time.time() - start_time
            logger.debug(f"gTTS: Playback loop finished after {elapsed:.2f}s")

        except Exception as e:
            logger.error(f"Error in MPV playback for gTTS: {e}")
            raise

    def _get_status(self) -> dict:
        """Get current player status for debugging."""
        return {
            "current_file": self._current_audio_file,
            "is_playing": self.get_current_state() == "playing",
            "is_paused": self._is_paused,
            "mpv_available": self.mpv_player is not None,
        }

    def _cleanup_current_file(self) -> None:
        """Clean up current temporary file."""
        if self._current_audio_file and os.path.exists(self._current_audio_file):
            try:
                os.unlink(self._current_audio_file)
                logger.debug(
                    f"Cleaned up temp file: {self._current_audio_file}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")
        self._current_audio_file = None

    def pause(self) -> None:
        """Pause audio playback."""
        if self.mpv_player and self.get_current_state() == "playing":
            try:
                self.mpv_player.pause = True  # type: ignore
                self._is_paused = True
                # ⭐ 關鍵修改：暫停時不清理檔案，保留給 resume 使用
                logger.debug("gTTS playback paused successfully")
                self._transition_state(TTSState.PAUSED)
            except Exception as e:
                logger.warning(f"Failed to pause MPV player: {e}")
                self._is_paused = False
        else:
            logger.warning("Cannot pause: no active playback")

    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        return (
            self.mpv_player is not None
            and self._is_paused
            and self._current_audio_file is not None
            and os.path.exists(self._current_audio_file)
        )

    def resume(self) -> None:
        """Resume audio playback."""
        logger.debug(f"gTTS resume called: mpv_player={self.mpv_player is not None}, "
                     f"_is_paused={self._is_paused}, state={self.get_current_state()}")

        if not self.can_resume():
            logger.warning("Cannot resume: conditions not met")
            return

        try:
            # MPV 已經載入檔案，只需要取消暫停
            self.mpv_player.pause = False
            self._is_paused = False

            # 更新狀態 - 直接使用 _update_state 因為狀態轉換可能會失敗
            self._update_state(TTSState.PLAYING)
            logger.debug("gTTS playback resumed successfully")

        except Exception as e:
            logger.warning(f"Failed to resume MPV player: {e}")
            self._is_paused = True

    def stop(self) -> None:
        """Stop audio playback."""
        logger.debug("Stopping gTTS playback...")

        # 清除暫停標誌
        self._is_paused = False

        if self._transition_state(TTSState.STOPPED):
            if self.mpv_player:
                try:
                    # 停止播放
                    self.mpv_player.stop()
                    # 短暫等待確保停止完成
                    time.sleep(0.1)
                    # 終止播放器
                    self.mpv_player.terminate()
                    logger.debug("MPV player terminated")
                except Exception as e:
                    logger.warning(f"Error terminating MPV player: {e}")
                finally:
                    self.mpv_player = None

            # 清理臨時檔案
            self._cleanup_current_file()
            logger.debug("gTTS playback stopped successfully")

    def seek(self, position: int) -> None:
        """Seek not supported in gTTS."""
        logger.warning("Seek not supported in gTTS provider")

    def set_volume(self, volume: float) -> None:
        """Set playback volume."""
        # 儲存音量設定（0.0-1.0）
        self._current_volume = max(0.0, min(1.0, volume))
        logger.debug(
            f"gTTS volume set to {self._current_volume} (will be {self._current_volume * 100}% in MPV)")

        # 如果正在播放，立即更新
        if self.mpv_player:
            try:
                self.mpv_player.volume = self._current_volume * 100
                logger.debug(
                    f"Updated active MPV player volume to {self._current_volume * 100}")
            except Exception as e:
                logger.warning(f"Failed to update MPV volume: {e}")

    def get_volume(self) -> float:
        """Get current volume level."""
        if self.mpv_player:
            vol = getattr(self.mpv_player, 'volume', None)
            if vol is not None and isinstance(vol, (int, float)):
                return float(vol) / 100  # Convert back to 0-1 scale
        return self._current_volume

    def set_speed(self, speed: float) -> None:
        """Set playback speed (this is how we control rate in gTTS)."""
        self._current_speed = speed
        if self.mpv_player:
            # MPV speed is absolute, not percentage-based like pygame
            # speed parameter here is already the absolute speed value (0.5-2.2)
            # When UI shows 100%, this corresponds to speed = 2.0 for MPV
            self.mpv_player.speed = speed

    def get_speed(self) -> float:
        """Get current playback speed."""
        if self.mpv_player:
            speed = getattr(self.mpv_player, 'speed', None)
            if speed is not None and isinstance(speed, (int, float)):
                return float(speed)
        return self._current_speed

    def speak_text_sync(self, text: str, **kwargs) -> None:
        """Synchronous text-to-speech (blocking)."""
        try:
            # Run async operations in sync context
            asyncio.run(self._speak_text_async(text, **kwargs))
        except Exception as e:
            logger.error(f"Error in speak_text_sync: {e}")
            raise

    async def _speak_text_async(self, text: str, **kwargs) -> None:
        """Async helper for speak_text_sync."""
        # Use current voice for synthesis
        audio_data = await self.synthesize(text, self._current_voice, **kwargs)
        await self.play_audio(audio_data)
