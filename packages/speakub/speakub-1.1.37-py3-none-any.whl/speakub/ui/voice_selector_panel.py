

from typing import Any, Dict, List

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Static


class VoiceSelectorPanel(Vertical):
    """A side panel for selecting TTS voices."""

    class VoiceSelected(Message):
        """Sent when a voice is selected."""

        def __init__(self, voice_short_name: str) -> None:
            self.voice_short_name = voice_short_name
            super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the voice selector panel components."""
        yield Static(
            "TTS Voice Selection", classes="panel-title",
            id="voice-panel-title"
        )

        # Add engine selector buttons
        with Horizontal(id="engine-selector"):
            yield Button("Edge-TTS", id="btn-edge-tts", variant="primary")
            yield Button("gTTS", id="btn-gtts")

        yield DataTable(id="voice-table", cursor_type="row")

    def on_mount(self) -> None:
        """Set up the table columns."""
        table = self.query_one(DataTable)
        table.add_columns("Voice Name")

        # Initialize filter state
        self._filter_enabled = True

    # --- Key modification 1: Add current_voice_short_name parameter ---
    def update_voices(
        self, voices: List[Dict[str, Any]], current_voice_short_name: str
    ) -> None:
        """Populate the table with available voices and mark the current voice."""
        table = self.query_one(DataTable)
        table.clear()

        sorted_voices = sorted(voices, key=lambda v: v.get("short_name", ""))

        for voice in sorted_voices:
            short_name = voice.get("short_name", "N/A")

            # --- Key modification 2: Check if it's the current voice and add marker ---
            display_text = ""
            if short_name == current_voice_short_name:
                # If it's the current voice, add marker at the front
                display_text = f"☛ {short_name}"
            else:
                # Otherwise, add spaces to maintain alignment
                display_text = f"  {short_name}"

            # key still uses original short_name
            table.add_row(display_text, key=short_name)

    async def on_button_pressed(self, event) -> None:
        """Handle engine selection button press."""
        if event.button.id == "btn-edge-tts":
            self._switch_engine("edge-tts")
        elif event.button.id == "btn-gtts":
            self._switch_engine("gtts")

    def _switch_engine(self, engine: str) -> None:
        """Switch TTS engine and update UI."""
        # ⭐ 關鍵修改：檢查 TTS 狀態，播放中切換需確認
        if hasattr(self.app, 'tts_status') and self.app.tts_status in ["PLAYING", "PAUSED"]:
            # 顯示警告訊息並停止播放
            self.app.notify(
                "Switching engine will stop current playback",
                severity="warning"
            )
            # 自動停止播放，避免狀態不一致
            if hasattr(self.app, 'tts_integration'):
                self.app.tts_integration.stop_speaking(is_pause=False)

        # Update button styles
        edge_btn = self.query_one("#btn-edge-tts", Button)
        gtts_btn = self.query_one("#btn-gtts", Button)

        if engine == "edge-tts":
            edge_btn.variant = "primary"
            gtts_btn.variant = "default"
        else:
            edge_btn.variant = "default"
            gtts_btn.variant = "primary"

        # Update configuration and switch engine
        from speakub.utils.config import ConfigManager
        config_mgr = ConfigManager()
        config_mgr.set_override("tts.preferred_engine", engine)
        config_mgr.save_to_file()  # Save to disk

        # Reinitialize TTS engine with new configuration
        if hasattr(self.app, 'tts_integration'):
            import asyncio
            asyncio.create_task(self._reinitialize_tts_engine(engine))

    async def _reinitialize_tts_engine(self, engine: str) -> None:
        """Reinitialize TTS engine with new configuration."""
        try:
            # Stop current TTS if playing
            if hasattr(self.app, 'tts_status') and self.app.tts_status in ["PLAYING", "PAUSED"]:
                if hasattr(self.app, 'tts_integration'):
                    self.app.tts_integration.stop_speaking(is_pause=False)

            # Re-setup TTS with new engine
            if hasattr(self.app, 'tts_integration'):
                await self.app.tts_integration.setup_tts()

            # Update voices for the new engine
            await self._update_voices_for_engine(engine)

            self.app.notify(
                f"Switched to {engine.upper()} engine", severity="information")

        except Exception as e:
            self.app.notify(f"Failed to switch engine: {e}", severity="error")

    async def _update_voices_for_engine(self, engine: str) -> None:
        """Update voices list for the specified engine."""
        try:
            # Get voices for the new engine
            if engine == "gtts":
                # Import GTTSProvider and get voices
                try:
                    from speakub.tts.gtts_provider import GTTSProvider
                    gtts_provider = GTTSProvider()
                    voices = await gtts_provider.get_available_voices()
                    # Get current voice from config
                    from speakub.utils.config import ConfigManager
                    config_mgr = ConfigManager()
                    current_voice = config_mgr.get(
                        "tts.gtts.default_voice", "gtts-zh-TW")
                except Exception as e:
                    self.app.notify(
                        f"Failed to load gTTS voices: {e}", severity="error")
                    return
            else:
                # For Edge-TTS, we need to get from the app's TTS engine
                if hasattr(self.app, 'tts_engine') and self.app.tts_engine:
                    voices = await self.app.tts_engine.get_available_voices()
                    current_voice = self.app.tts_engine.get_current_voice()
                else:
                    self.app.notify("No TTS engine available",
                                    severity="warning")
                    return

            # Apply filter if enabled and for Edge-TTS
            if self._filter_enabled and engine == "edge-tts":
                from speakub.utils.voice_filter_utils import filter_female_chinese_voices
                voices = filter_female_chinese_voices(voices)

            # Update the voice table
            self.update_voices(voices, current_voice)

        except Exception as e:
            self.app.notify(f"Error updating voices: {e}", severity="error")

    async def on_data_table_row_selected(self, event) -> None:
        """Handle voice selection event."""
        if event.row_key.value:
            self.post_message(self.VoiceSelected(event.row_key.value))
