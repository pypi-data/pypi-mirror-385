

#!/usr/bin/env python3
# Action handlers for SpeakUB Application

import logging
from typing import TYPE_CHECKING, Optional

from speakub.utils.config import save_tts_config

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from speakub.ui.app import EPUBReaderApp


class SpeakUBActions:
    """Handles user actions for the SpeakUB application."""

    def __init__(self, app: "EPUBReaderApp"):
        self.app = app

    def _save_tts_config(self) -> None:
        """Save current TTS configuration to config file."""
        try:
            tts_config = {
                "rate": self.app.tts_rate,
                "volume": self.app.tts_volume,
                "pitch": self.app.tts_pitch,
                "smooth_mode": self.app.tts_smooth_mode,
            }
            save_tts_config(tts_config)
        except Exception as e:
            self.app.notify(
                f"Failed to save TTS config: {e}", severity="warning")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app._save_progress()
        self.app._cleanup()
        self.app.exit()

    def action_switch_focus(self) -> None:
        """Switch focus between panels."""
        self.app._update_user_activity()
        focus_order = ["toc", "content"]
        idx = (focus_order.index(self.app.current_focus) + 1) % len(focus_order)
        self.app.current_focus = focus_order[idx]
        self.app._update_panel_focus()

    def action_toggle_smooth_tts(self) -> None:
        """Toggle smooth TTS mode."""
        self.app._update_user_activity()

        # ⭐ 檢查引擎類型 - 使用全域配置管理器
        from speakub.utils.config import get_config
        current_engine = get_config("tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            self.app.notify(
                "Smooth mode is not available for gTTS engine",
                severity="warning"
            )
            return

        # 原有的 Edge-TTS smooth mode 邏輯
        if self.app.tts_status != "STOPPED":
            self.app.stop_speaking()
        self.app.tts_smooth_mode = not self.app.tts_smooth_mode
        self._save_tts_config()
        self.app.notify(
            f"Smooth TTS Mode: {'ON' if self.app.tts_smooth_mode else 'OFF'}"
        )

    def action_toggle_toc(self) -> None:
        """Toggle table of contents visibility."""
        self.app._update_user_activity()
        self.app.toc_visible = not self.app.toc_visible
        self.app.query_one("#toc-panel").display = self.app.toc_visible

    def action_toggle_tts(self) -> None:
        """Toggle TTS panel visibility."""
        self.app._update_user_activity()
        self.app.tts_visible = not self.app.tts_visible
        self.app.query_one("#tts-footer").display = self.app.tts_visible

    def action_increase_volume(self) -> None:
        """Increase TTS volume."""
        self.app._update_user_activity()
        self.app.tts_volume = min(100, self.app.tts_volume + 10)
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_decrease_volume(self) -> None:
        """Decrease TTS volume."""
        self.app._update_user_activity()
        self.app.tts_volume = max(0, self.app.tts_volume - 10)
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_increase_speed(self) -> None:
        """Increase TTS speed."""
        self.app._update_user_activity()

        # Check current engine type
        from speakub.utils.config import ConfigManager
        config_mgr = ConfigManager()
        current_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS: adjust playback speed
            if self.app.tts_engine and hasattr(self.app.tts_engine, "get_speed"):
                current_speed = self.app.tts_engine.get_speed()
                new_speed = min(2.0, current_speed + 0.1)
                self.app.tts_engine.set_speed(new_speed)
                # Update rate to keep UI consistent
                self.app.tts_rate = int((new_speed - 1.0) * 100)
        else:
            # Edge-TTS: use traditional rate
            self.app.tts_rate = min(200, self.app.tts_rate + 10)

        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_decrease_speed(self) -> None:
        """Decrease TTS speed."""
        self.app._update_user_activity()

        # Check current engine type
        from speakub.utils.config import ConfigManager
        config_mgr = ConfigManager()
        current_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS: adjust playback speed
            if self.app.tts_engine and hasattr(self.app.tts_engine, "get_speed"):
                current_speed = self.app.tts_engine.get_speed()
                new_speed = max(0.5, current_speed - 0.1)
                self.app.tts_engine.set_speed(new_speed)
                # Update rate to keep UI consistent
                self.app.tts_rate = int((new_speed - 1.0) * 100)
        else:
            # Edge-TTS: use traditional rate
            self.app.tts_rate = max(-100, self.app.tts_rate - 10)

        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_increase_pitch(self) -> None:
        """Increase TTS pitch."""
        self.app._update_user_activity()

        # Check current engine type
        from speakub.utils.config import ConfigManager
        config_mgr = ConfigManager()
        current_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS does not support pitch adjustment
            self.app.notify("gTTS does not support pitch adjustment",
                            severity="warning")
            return

        # Edge-TTS: use traditional pitch
        val = int(self.app.tts_pitch.replace("+", "").replace("Hz", ""))
        new_val = min(50, val + 5)
        self.app.tts_pitch = f"+{new_val}Hz" if new_val >= 0 else f"{new_val}Hz"
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_decrease_pitch(self) -> None:
        """Decrease TTS pitch."""
        self.app._update_user_activity()

        # Check current engine type
        from speakub.utils.config import ConfigManager
        config_mgr = ConfigManager()
        current_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS does not support pitch adjustment
            self.app.notify("gTTS does not support pitch adjustment",
                            severity="warning")
            return

        # Edge-TTS: use traditional pitch
        val = int(self.app.tts_pitch.replace("Hz", ""))
        new_val = val - 5
        self.app.tts_pitch = f"+{new_val}Hz" if new_val >= 0 else f"{new_val}Hz"
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_content_up(self) -> None:
        """Move content cursor up."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_start = self.app.viewport_content.move_cursor_up()
        if at_chapter_start:
            prev_chapter = self.find_prev_chapter()
            if prev_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        prev_chapter, from_end=True)
                )
        self.app._update_content_display()

    def action_content_down(self) -> None:
        """Move content cursor down."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_end = self.app.viewport_content.move_cursor_down()
        if at_chapter_end:
            next_chapter = self.find_next_chapter()
            if next_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        next_chapter, from_start=True)
                )
        self.app._update_content_display()

    def action_content_page_up(self) -> None:
        """Move content cursor up by page."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_start = self.app.viewport_content.page_up()
        if at_chapter_start:
            prev_chapter = self.find_prev_chapter()
            if prev_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        prev_chapter, from_end=True)
                )
        self.app._update_content_display()

    def action_content_page_down(self) -> None:
        """Move content cursor down by page."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_end = self.app.viewport_content.page_down()
        if at_chapter_end:
            next_chapter = self.find_next_chapter()
            if next_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        next_chapter, from_start=True)
                )
        self.app._update_content_display()

    def action_content_home(self) -> None:
        """Jump to chapter start."""
        if self.app.viewport_content:
            self.app._update_user_activity()
            if self.app.tts_status == "PLAYING":
                self.app.stop_speaking()
            self.app.viewport_content.jump_to_page(0)
            self.app._update_content_display()

    def action_content_end(self) -> None:
        """Jump to chapter end."""
        if self.app.viewport_content:
            self.app._update_user_activity()
            if self.app.tts_status == "PLAYING":
                self.app.stop_speaking()
            info = self.app.viewport_content.get_viewport_info()
            self.app.viewport_content.jump_to_page(info["total_pages"] - 1)
            lines = len(self.app.viewport_content.get_current_viewport_lines())
            self.app.viewport_content.cursor_in_page = max(0, lines - 1)
            self.app._update_content_display()

    def action_tts_play_pause(self):
        """簡化的播放/暫停邏輯，統一使用 PlaybackManager"""
        self.app._update_user_activity()

        if self.app.tts_status == "PLAYING":
            # 播放中 → 暫停
            self.app.tts_integration.playback_manager.stop_playback(
                is_pause=True)
            self.app.tts_status = "PAUSED"

        elif self.app.tts_status == "PAUSED":
            # 暫停中 → 恢復
            if self.app.tts_integration.network_manager.network_error_occurred:
                self.app.tts_integration.network_manager.reset_network_error_state()
            self.app.tts_integration.playback_manager.start_playback()

        elif self.app.tts_status == "STOPPED":
            # 停止狀態 → 開始播放
            if self.app.tts_integration.network_manager.network_error_occurred:
                self.app.tts_integration.network_manager.reset_network_error_state()
            self.app.tts_integration.playlist_manager.generate_playlist()
            if self.app.tts_integration.playlist_manager.has_items():
                self.app.tts_integration.playback_manager.start_playback()
            else:
                # 查找下一章節
                import functools
                from speakub.tts.ui.runners import find_and_play_next_chapter_worker
                worker_func = functools.partial(
                    find_and_play_next_chapter_worker, self.app.tts_integration
                )
                self.app.run_worker(worker_func, exclusive=True, thread=True)

    def action_tts_stop(self):
        """Stop TTS."""
        self.app.stop_speaking(is_pause=False)

    def find_next_chapter(self) -> Optional[dict]:
        """Find the next chapter."""
        return self.app.epub_manager.get_next_chapter()

    def find_prev_chapter(self) -> Optional[dict]:
        """Find the previous chapter."""
        return self.app.epub_manager.get_previous_chapter()
