
#!/usr/bin/env python3
"""
Keyboard shortcuts management for SpeakUB.
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class KeybindingManager:
    """Manages keyboard shortcuts and custom keybindings."""

    DEFAULT_BINDINGS = {
        # Playback controls
        "space": "tts_play_pause",
        "s": "tts_stop",

        # Navigation
        "tab": "switch_focus",
        "f1": "toggle_toc",
        "f2": "toggle_tts",
        "v": "toggle_voice_panel",

        # Content scrolling
        "j": "content_down",
        "k": "content_up",
        "page_down": "content_page_down",
        "page_up": "content_page_up",
        "home": "content_home",
        "end": "content_end",

        # Volume and speed controls
        "+": "increase_volume",
        "=": "increase_volume",
        "-": "decrease_volume",
        "]": "increase_speed",
        "[": "decrease_speed",
        "p": "increase_pitch",
        "o": "decrease_pitch",

        # TTS modes
        "m": "toggle_smooth_tts",

        # Application
        "q": "quit",
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize keybinding manager.

        Args:
            config_dir: Directory to store custom keybindings
        """
        if config_dir is None:
            config_dir = Path.home() / '.config' / 'speakub'

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.custom_bindings_file = self.config_dir / 'keybindings.json'

        # Current bindings: defaults + custom overrides
        self.bindings = self.DEFAULT_BINDINGS.copy()
        self.custom_bindings: Dict[str, str] = {}

        # Action handlers
        self.action_handlers: Dict[str, Callable] = {}

        # Load custom bindings
        self._load_custom_bindings()

    def register_action(self, action_name: str, handler: Callable) -> None:
        """
        Register an action handler.

        Args:
            action_name: Name of the action
            handler: Function to call when action is triggered
        """
        self.action_handlers[action_name] = handler

    def bind_key(self, key: str, action: str) -> bool:
        """
        Bind a key to an action.

        Args:
            key: Key combination (e.g., 'ctrl+c', 'f1')
            action: Action name to bind to

        Returns:
            True if binding was successful
        """
        # Validate action exists
        if action not in self.action_handlers and action not in self.DEFAULT_BINDINGS.values():
            logger.warning(f"Unknown action: {action}")
            return False

        # Remove any existing binding for this key
        self._unbind_key(key)

        # Add new binding
        self.custom_bindings[key] = action
        self.bindings[key] = action

        logger.debug(f"Bound key '{key}' to action '{action}'")
        return True

    def unbind_key(self, key: str) -> bool:
        """
        Remove a custom key binding.

        Args:
            key: Key to unbind

        Returns:
            True if key was unbound
        """
        if key in self.custom_bindings:
            action = self.custom_bindings[key]
            del self.custom_bindings[key]

            # Restore default binding if it exists
            if key in self.DEFAULT_BINDINGS:
                self.bindings[key] = self.DEFAULT_BINDINGS[key]
            else:
                del self.bindings[key]

            logger.debug(f"Unbound key '{key}' from action '{action}'")
            return True

        return False

    def _unbind_key(self, key: str) -> None:
        """Internal method to remove a key binding."""
        if key in self.custom_bindings:
            del self.custom_bindings[key]

        if key in self.bindings:
            del self.bindings[key]

    def get_action_for_key(self, key: str) -> Optional[str]:
        """
        Get the action bound to a key.

        Args:
            key: Key combination

        Returns:
            Action name or None if not bound
        """
        return self.bindings.get(key)

    def get_key_for_action(self, action: str) -> Optional[str]:
        """
        Get the key bound to an action.

        Args:
            action: Action name

        Returns:
            Key combination or None if not bound
        """
        for key, bound_action in self.bindings.items():
            if bound_action == action:
                return key
        return None

    def execute_action(self, key: str) -> bool:
        """
        Execute the action bound to a key.

        Args:
            key: Key that was pressed

        Returns:
            True if action was executed
        """
        action = self.get_action_for_key(key)
        if action and action in self.action_handlers:
            try:
                self.action_handlers[action]()
                return True
            except Exception as e:
                logger.error(f"Error executing action '{action}': {e}")
                return False

        return False

    def reset_to_defaults(self) -> None:
        """Reset all bindings to defaults."""
        self.custom_bindings.clear()
        self.bindings = self.DEFAULT_BINDINGS.copy()
        logger.info("Keybindings reset to defaults")

    def save_custom_bindings(self) -> bool:
        """
        Save custom keybindings to file.

        Returns:
            True if saved successfully
        """
        try:
            with open(self.custom_bindings_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_bindings, f,
                          indent=2, ensure_ascii=False)

            logger.debug(
                f"Custom keybindings saved to {self.custom_bindings_file}")
            return True

        except (IOError, OSError) as e:
            logger.error(f"Failed to save keybindings: {e}")
            return False

    def _load_custom_bindings(self) -> None:
        """Load custom keybindings from file."""
        if not self.custom_bindings_file.exists():
            return

        try:
            with open(self.custom_bindings_file, 'r', encoding='utf-8') as f:
                self.custom_bindings = json.load(f)

            # Apply custom bindings
            self.bindings.update(self.custom_bindings)

            logger.debug(
                f"Loaded {len(self.custom_bindings)} custom keybindings")

        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load custom keybindings: {e}")
            self.custom_bindings = {}

    def get_all_bindings(self) -> Dict[str, str]:
        """
        Get all current key bindings.

        Returns:
            Dictionary of key -> action mappings
        """
        return self.bindings.copy()

    def get_custom_bindings(self) -> Dict[str, str]:
        """
        Get only custom key bindings.

        Returns:
            Dictionary of custom key -> action mappings
        """
        return self.custom_bindings.copy()

    def validate_key_format(self, key: str) -> bool:
        """
        Validate key format.

        Args:
            key: Key combination to validate

        Returns:
            True if format is valid
        """
        # Basic validation - can be extended for more complex key combinations
        if not key or not isinstance(key, str):
            return False

        # Check for basic key patterns
        valid_patterns = [
            r'^[a-zA-Z0-9]$',  # Single character
            r'^f[0-9]+$',      # Function keys
            r'^page_up$',      # Special keys
            r'^page_down$',
            r'^home$',
            r'^end$',
            r'^space$',
            r'^tab$',
            r'^enter$',
            r'^escape$',
        ]

        import re
        return any(re.match(pattern, key.lower()) for pattern in valid_patterns)

    def get_binding_conflicts(self) -> Dict[str, list]:
        """
        Check for binding conflicts.

        Returns:
            Dictionary of conflicting keys and their actions
        """
        conflicts = {}
        key_to_actions = {}

        for key, action in self.bindings.items():
            if key not in key_to_actions:
                key_to_actions[key] = []
            key_to_actions[key].append(action)

        for key, actions in key_to_actions.items():
            if len(actions) > 1:
                conflicts[key] = actions

        return conflicts

    def export_bindings(self, file_path: str) -> bool:
        """
        Export all bindings to a file.

        Args:
            file_path: Path to export file

        Returns:
            True if exported successfully
        """
        try:
            export_data = {
                'defaults': self.DEFAULT_BINDINGS,
                'custom': self.custom_bindings,
                'current': self.bindings,
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Keybindings exported to {file_path}")
            return True

        except (IOError, OSError) as e:
            logger.error(f"Failed to export keybindings: {e}")
            return False

    def import_bindings(self, file_path: str) -> bool:
        """
        Import bindings from a file.

        Args:
            file_path: Path to import file

        Returns:
            True if imported successfully
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # Load custom bindings
            if 'custom' in import_data:
                self.custom_bindings = import_data['custom']
                self.bindings = self.DEFAULT_BINDINGS.copy()
                self.bindings.update(self.custom_bindings)

            logger.info(f"Keybindings imported from {file_path}")
            return True

        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to import keybindings: {e}")
            return False
