
"""
Configuration service for centralized configuration management.
"""

from typing import Any, Dict, Optional

from speakub.utils.config import ConfigManager


class ConfigurationService:
    """Centralized configuration service."""

    def __init__(self):
        self._config_mgr = ConfigManager()

    def get(self, key: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config_mgr.get(key, default)

    def set_override(self, key: str, value: Any) -> None:
        """Set configuration override."""
        self._config_mgr.set_override(key, value)

    def clear_override(self, key: str) -> None:
        """Clear configuration override."""
        self._config_mgr.clear_override(key)

    def save_to_file(self) -> None:
        """Save configuration to file."""
        self._config_mgr.save_to_file()

    def reload(self) -> None:
        """Reload configuration."""
        self._config_mgr.reload()

    def get_tts_config(self) -> Dict[str, Any]:
        """Get TTS configuration."""
        return self._config_mgr.get("tts", {})

    def save_tts_config(self, tts_config: Dict[str, Any]) -> None:
        """Save TTS configuration."""
        from speakub.utils.config import save_tts_config
        save_tts_config(tts_config)

    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration."""
        from speakub.utils.config import get_network_config
        return get_network_config()

    def get_cache_config(self) -> Dict[str, int]:
        """Get cache configuration."""
        from speakub.utils.config import get_cache_config
        return get_cache_config()
