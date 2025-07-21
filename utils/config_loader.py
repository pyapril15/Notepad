"""
Configuration Loader - Handles application settings and session management
"""

import json
import os
from pathlib import Path


class ConfigLoader:
    """Handles configuration loading and saving"""

    def __init__(self):
        self.config_dir = Path.home() / '.modern_notepad'
        self.config_file = self.config_dir / 'config.json'
        self.session_file = self.config_dir / 'session.json'

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        # Default configuration - ENSURE ALL VALUES ARE PROPER TYPES
        self.default_config = {
            # String values
            'theme': 'light',
            'font_family': 'Consolas',
            'encoding': 'utf-8',
            'window_geometry': '1000x700',
            'spell_language': 'English',
            'log_level': 'INFO',

            # Integer values - EXPLICITLY SET AS INTEGERS
            'font_size': 12,
            'autosave_interval': 300,  # 5 minutes
            'tab_size': 4,
            'max_recent_files': 10,
            'large_file_threshold': 10,

            # Boolean values - EXPLICITLY SET AS BOOLEANS
            'word_wrap': True,
            'line_numbers': True,
            'status_bar': True,
            'autosave_enabled': True,
            'spell_check_enabled': True,
            'syntax_highlighting': True,
            'show_whitespace': False,
            'highlight_current_line': True,
            'auto_indent': True,
            'smart_indent': True,
            'show_line_endings': False,
            'backup_files': True,
            'confirm_exit': True,
            'restore_session': True,
            'enable_logging': True,

            # List values
            'recent_files': []
        }

        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge with defaults to ensure all keys exist
                config = self.default_config.copy()
                config.update(loaded_config)
                return config
            else:
                return self.default_config.copy()
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key, default=None):
        """Get configuration value with validation"""
        value = self.config.get(key, default)

        # If we get an empty string and default is not a string, return default
        if value == "" and default is not None and not isinstance(default, str):
            return default

        # If we get None and have a default, return default
        if value is None and default is not None:
            return default

        return value

    def set(self, key, value):
        """Set configuration value and save"""
        self.config[key] = value
        self.save_config()

    def get_all(self):
        """Get all configuration"""
        return self.config.copy()

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save_config()

    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        recent_files = self.config.get('recent_files', [])

        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning
        recent_files.insert(0, file_path)

        # Limit to max recent files
        max_recent = self.config.get('max_recent_files', 10)
        recent_files = recent_files[:max_recent]

        self.set('recent_files', recent_files)

    def remove_recent_file(self, file_path):
        """Remove file from recent files list"""
        recent_files = self.config.get('recent_files', [])
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.set('recent_files', recent_files)

    def clear_recent_files(self):
        """Clear all recent files"""
        self.set('recent_files', [])

    def save_session(self, session_data):
        """Save session data"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def get_session(self):
        """Get session data"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading session: {e}")
            return {}

    def clear_session(self):
        """Clear session data"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing session: {e}")
            return False

    def export_config(self, file_path):
        """Export configuration to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, file_path):
        """Import configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            # Validate and merge with current config
            for key, value in imported_config.items():
                if key in self.default_config:
                    self.config[key] = value

            self.save_config()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False

    def get_theme_path(self, theme_name):
        """Get path to theme file"""
        return Path('themes') / f'{theme_name}.json'

    def get_available_themes(self):
        """Get list of available themes"""
        themes_dir = Path('themes')
        if not themes_dir.exists():
            return ['light', 'dark']

        themes = []
        for theme_file in themes_dir.glob('*.json'):
            themes.append(theme_file.stem)

        return themes if themes else ['light', 'dark']

    def create_default_themes(self):
        """Create default theme files if they don't exist"""
        themes_dir = Path('themes')
        themes_dir.mkdir(exist_ok=True)

        # Light theme
        light_theme = {
            "name": "Light",
            "text_widget": {
                "background": "#ffffff",
                "foreground": "#000000",
                "cursor": "#000000",
                "selection": "#0078d4",
                "selection_foreground": "#ffffff"
            },
            "line_numbers": {
                "background": "#f5f5f5",
                "foreground": "#666666"
            },
            "syntax": {
                "keyword": "#0000ff",
                "string": "#008000",
                "comment": "#808080",
                "number": "#ff0000",
                "operator": "#000080",
                "builtin": "#800080"
            },
            "ui": {
                "background": "#f0f0f0",
                "foreground": "#000000",
                "highlight": "#e0e0e0"
            }
        }

        # Dark theme
        dark_theme = {
            "name": "Dark",
            "text_widget": {
                "background": "#1e1e1e",
                "foreground": "#d4d4d4",
                "cursor": "#ffffff",
                "selection": "#264f78",
                "selection_foreground": "#ffffff"
            },
            "line_numbers": {
                "background": "#252526",
                "foreground": "#858585"
            },
            "syntax": {
                "keyword": "#569cd6",
                "string": "#ce9178",
                "comment": "#6a9955",
                "number": "#b5cea8",
                "operator": "#d4d4d4",
                "builtin": "#dcdcaa"
            },
            "ui": {
                "background": "#2d2d30",
                "foreground": "#cccccc",
                "highlight": "#3e3e42"
            }
        }

        # Save themes
        light_file = themes_dir / 'light.json'
        dark_file = themes_dir / 'dark.json'

        if not light_file.exists():
            with open(light_file, 'w', encoding='utf-8') as f:
                json.dump(light_theme, f, indent=2)

        if not dark_file.exists():
            with open(dark_file, 'w', encoding='utf-8') as f:
                json.dump(dark_theme, f, indent=2)

    def validate_config(self):
        """Validate configuration and fix any issues"""
        fixed = False

        # Ensure all required keys exist
        for key, default_value in self.default_config.items():
            if key not in self.config:
                self.config[key] = default_value
                fixed = True

        # Validate data types
        if not isinstance(self.config.get('recent_files'), list):
            self.config['recent_files'] = []
            fixed = True

        if not isinstance(self.config.get('font_size'), int):
            self.config['font_size'] = 12
            fixed = True

        # Remove non-existent recent files
        recent_files = self.config.get('recent_files', [])
        valid_files = [f for f in recent_files if os.path.exists(f)]
        if len(valid_files) != len(recent_files):
            self.config['recent_files'] = valid_files
            fixed = True

        if fixed:
            self.save_config()

        return fixed
