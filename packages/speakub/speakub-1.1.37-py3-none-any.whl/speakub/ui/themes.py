
#!/usr/bin/env python3
"""
Theme management system for SpeakUB.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages UI themes for SpeakUB."""

    # Default themes
    DEFAULT_THEMES = {
        'default': {
            'name': 'Default',
            'description': 'Classic SpeakUB theme',
            'colors': {
                'primary': '#007acc',
                'secondary': '#cccccc',
                'accent': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
                'success': '#4caf50',
                'surface': '#ffffff',
                'background': '#f5f5f5',
                'text': '#333333',
                'text_secondary': '#666666',
                'border': '#dddddd',
                'boost': '#e8f4fd',
            },
            'fonts': {
                'family': 'monospace',
                'size': 12,
            }
        },

        'dark': {
            'name': 'Dark',
            'description': 'Dark theme for low-light environments',
            'colors': {
                'primary': '#61dafb',
                'secondary': '#282c34',
                'accent': '#98c379',
                'warning': '#e5c07b',
                'error': '#e06c75',
                'success': '#98c379',
                'surface': '#21252b',
                'background': '#1e2127',
                'text': '#abb2bf',
                'text_secondary': '#5c6370',
                'border': '#3e4451',
                'boost': '#2c313c',
            },
            'fonts': {
                'family': 'monospace',
                'size': 12,
            }
        },

        'high_contrast': {
            'name': 'High Contrast',
            'description': 'High contrast theme for accessibility',
            'colors': {
                'primary': '#ffffff',
                'secondary': '#ffff00',
                'accent': '#00ff00',
                'warning': '#ffff00',
                'error': '#ff0000',
                'success': '#00ff00',
                'surface': '#000000',
                'background': '#000000',
                'text': '#ffffff',
                'text_secondary': '#ffff00',
                'border': '#ffffff',
                'boost': '#333333',
            },
            'fonts': {
                'family': 'monospace',
                'size': 14,  # Slightly larger for better readability
            }
        },

        'solarized_light': {
            'name': 'Solarized Light',
            'description': 'Light theme based on Solarized color palette',
            'colors': {
                'primary': '#268bd2',
                'secondary': '#eee8d5',
                'accent': '#2aa198',
                'warning': '#b58900',
                'error': '#dc322f',
                'success': '#859900',
                'surface': '#fdf6e3',
                'background': '#eee8d5',
                'text': '#586e75',
                'text_secondary': '#93a1a1',
                'border': '#93a1a1',
                'boost': '#f5efd8',
            },
            'fonts': {
                'family': 'monospace',
                'size': 12,
            }
        },

        'solarized_dark': {
            'name': 'Solarized Dark',
            'description': 'Dark theme based on Solarized color palette',
            'colors': {
                'primary': '#268bd2',
                'secondary': '#073642',
                'accent': '#2aa198',
                'warning': '#b58900',
                'error': '#dc322f',
                'success': '#859900',
                'surface': '#002b36',
                'background': '#073642',
                'text': '#93a1a1',
                'text_secondary': '#586e75',
                'border': '#586e75',
                'boost': '#0f4a5c',
            },
            'fonts': {
                'family': 'monospace',
                'size': 12,
            }
        },
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize theme manager.

        Args:
            config_dir: Directory to store custom themes
        """
        if config_dir is None:
            config_dir = Path.home() / '.config' / 'speakub'

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.custom_themes_file = self.config_dir / 'themes.json'
        self.current_theme = 'default'

        # Available themes: defaults + custom
        self.themes = self.DEFAULT_THEMES.copy()
        self.custom_themes: Dict[str, Dict] = {}

        # Load custom themes
        self._load_custom_themes()

    def get_theme(self, theme_name: Optional[str] = None) -> Dict:
        """
        Get theme configuration.

        Args:
            theme_name: Name of theme to get (uses current if None)

        Returns:
            Theme configuration dictionary

        Raises:
            KeyError: If theme doesn't exist
        """
        name = theme_name or self.current_theme

        if name not in self.themes:
            raise KeyError(f"Theme '{name}' not found")

        return self.themes[name]

    def set_current_theme(self, theme_name: str) -> bool:
        """
        Set the current theme.

        Args:
            theme_name: Name of theme to set as current

        Returns:
            True if theme was set successfully

        Raises:
            KeyError: If theme doesn't exist
        """
        if theme_name not in self.themes:
            raise KeyError(f"Theme '{theme_name}' not found")

        self.current_theme = theme_name
        logger.info(f"Theme changed to: {theme_name}")
        return True

    def get_current_theme(self) -> str:
        """Get the name of the current theme."""
        return self.current_theme

    def get_available_themes(self) -> Dict[str, Dict]:
        """
        Get all available themes.

        Returns:
            Dictionary of theme_name -> theme_info
        """
        return self.themes.copy()

    def create_custom_theme(self, name: str, base_theme: str = 'default',
                            overrides: Optional[Dict] = None) -> bool:
        """
        Create a custom theme.

        Args:
            name: Name for the custom theme
            base_theme: Base theme to inherit from
            overrides: Theme property overrides

        Returns:
            True if theme was created successfully

        Raises:
            KeyError: If base theme doesn't exist
            ValueError: If theme name is invalid
        """
        if name in self.themes:
            raise ValueError(f"Theme '{name}' already exists")

        if base_theme not in self.themes:
            raise KeyError(f"Base theme '{base_theme}' not found")

        # Create theme by copying base and applying overrides
        custom_theme = self.themes[base_theme].copy()

        if overrides:
            # Deep merge overrides
            self._deep_update_theme(custom_theme, overrides)

        custom_theme['name'] = name
        custom_theme['custom'] = True
        custom_theme['base'] = base_theme

        # Add to themes and custom themes
        self.themes[name] = custom_theme
        self.custom_themes[name] = custom_theme

        logger.info(f"Custom theme '{name}' created based on '{base_theme}'")
        return True

    def update_custom_theme(self, name: str, updates: Dict) -> bool:
        """
        Update a custom theme.

        Args:
            name: Name of custom theme to update
            updates: Theme property updates

        Returns:
            True if theme was updated successfully

        Raises:
            KeyError: If theme doesn't exist or isn't custom
            ValueError: If updates are invalid
        """
        if name not in self.themes:
            raise KeyError(f"Theme '{name}' not found")

        if name not in self.custom_themes:
            raise ValueError(f"Theme '{name}' is not a custom theme")

        # Apply updates
        self._deep_update_theme(self.themes[name], updates)
        self.custom_themes[name] = self.themes[name]

        logger.info(f"Custom theme '{name}' updated")
        return True

    def delete_custom_theme(self, name: str) -> bool:
        """
        Delete a custom theme.

        Args:
            name: Name of custom theme to delete

        Returns:
            True if theme was deleted successfully

        Raises:
            KeyError: If theme doesn't exist
            ValueError: If trying to delete a default theme
        """
        if name not in self.themes:
            raise KeyError(f"Theme '{name}' not found")

        if name not in self.custom_themes:
            raise ValueError(f"Cannot delete default theme '{name}'")

        # If this was the current theme, switch to default
        if self.current_theme == name:
            self.current_theme = 'default'

        # Remove from themes and custom themes
        del self.themes[name]
        del self.custom_themes[name]

        logger.info(f"Custom theme '{name}' deleted")
        return True

    def _deep_update_theme(self, theme: Dict, updates: Dict) -> None:
        """
        Deep update theme properties.

        Args:
            theme: Theme to update
            updates: Updates to apply
        """
        for key, value in updates.items():
            if key in theme and isinstance(theme[key], dict) and isinstance(value, dict):
                self._deep_update_theme(theme[key], value)
            else:
                theme[key] = value

    def save_custom_themes(self) -> bool:
        """
        Save custom themes to file.

        Returns:
            True if saved successfully
        """
        try:
            with open(self.custom_themes_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_themes, f, indent=2, ensure_ascii=False)

            logger.debug(f"Custom themes saved to {self.custom_themes_file}")
            return True

        except (IOError, OSError) as e:
            logger.error(f"Failed to save custom themes: {e}")
            return False

    def _load_custom_themes(self) -> None:
        """Load custom themes from file."""
        if not self.custom_themes_file.exists():
            return

        try:
            with open(self.custom_themes_file, 'r', encoding='utf-8') as f:
                self.custom_themes = json.load(f)

            # Add custom themes to main themes dict
            self.themes.update(self.custom_themes)

            logger.debug(f"Loaded {len(self.custom_themes)} custom themes")

        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load custom themes: {e}")
            self.custom_themes = {}

    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """
        Export a theme to a file.

        Args:
            theme_name: Name of theme to export
            file_path: Path to export file

        Returns:
            True if exported successfully

        Raises:
            KeyError: If theme doesn't exist
        """
        if theme_name not in self.themes:
            raise KeyError(f"Theme '{theme_name}' not found")

        try:
            export_data = {
                'theme_name': theme_name,
                'theme_data': self.themes[theme_name],
                'exported_by': 'SpeakUB ThemeManager',
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Theme '{theme_name}' exported to {file_path}")
            return True

        except (IOError, OSError) as e:
            logger.error(f"Failed to export theme: {e}")
            return False

    def import_theme(self, file_path: str, name: Optional[str] = None) -> bool:
        """
        Import a theme from a file.

        Args:
            file_path: Path to theme file
            name: Name for imported theme (uses file name if None)

        Returns:
            True if imported successfully

        Raises:
            ValueError: If theme data is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            if 'theme_data' not in import_data:
                raise ValueError("Invalid theme file format")

            theme_data = import_data['theme_data']

            # Validate theme data
            self._validate_theme_data(theme_data)

            # Determine theme name
            if name is None:
                name = import_data.get('theme_name', Path(file_path).stem)

            # Avoid overwriting existing themes
            original_name = name
            counter = 1
            while name in self.themes:
                name = f"{original_name}_{counter}"
                counter += 1

            # Add as custom theme
            theme_data['name'] = name
            theme_data['custom'] = True
            theme_data['imported'] = True

            self.themes[name] = theme_data
            self.custom_themes[name] = theme_data

            logger.info(f"Theme '{name}' imported from {file_path}")
            return True

        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to import theme: {e}")
            return False
        except ValueError as e:
            logger.error(f"Invalid theme data: {e}")
            return False

    def _validate_theme_data(self, theme_data: Dict) -> None:
        """
        Validate theme data structure.

        Args:
            theme_data: Theme data to validate

        Raises:
            ValueError: If theme data is invalid
        """
        required_keys = ['name', 'colors', 'fonts']

        for key in required_keys:
            if key not in theme_data:
                raise ValueError(f"Missing required theme key: {key}")

        # Validate colors
        if not isinstance(theme_data.get('colors'), dict):
            raise ValueError("Theme colors must be a dictionary")

        required_colors = ['primary', 'surface', 'text']
        for color in required_colors:
            if color not in theme_data['colors']:
                raise ValueError(f"Missing required color: {color}")

        # Validate fonts
        if not isinstance(theme_data.get('fonts'), dict):
            raise ValueError("Theme fonts must be a dictionary")

    def get_theme_css_variables(self, theme_name: Optional[str] = None) -> str:
        """
        Generate CSS custom properties for a theme.

        Args:
            theme_name: Name of theme (uses current if None)

        Returns:
            CSS string with custom properties
        """
        theme = self.get_theme(theme_name)

        css_lines = [":root {"]
        for color_name, color_value in theme['colors'].items():
            css_lines.append(f"  --color-{color_name}: {color_value};")

        css_lines.append("}")
        return "\n".join(css_lines)

    def preview_theme(self, theme_name: str) -> str:
        """
        Generate a text preview of a theme.

        Args:
            theme_name: Name of theme to preview

        Returns:
            Formatted text preview
        """
        theme = self.get_theme(theme_name)

        preview = f"Theme: {theme['name']}\n"
        preview += f"Description: {theme.get('description', 'No description')}\n\n"

        preview += "Colors:\n"
        for color_name, color_value in theme['colors'].items():
            preview += f"  {color_name}: {color_value}\n"

        preview += "\nFonts:\n"
        for font_prop, font_value in theme['fonts'].items():
            preview += f"  {font_prop}: {font_value}\n"

        return preview
