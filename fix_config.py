"""
Configuration Fix Script for Modern Notepad
Run this script to fix configuration issues causing "expected integer but got ''" errors

Usage: python fix_config.py
"""

import json
import os
from pathlib import Path


def fix_config():
    """Fix configuration file with proper data types"""

    config_dir = Path.home() / '.modern_notepad'
    config_file = config_dir / 'config.json'

    print("Modern Notepad Configuration Fix")
    print("=" * 40)

    if not config_file.exists():
        print("No configuration file found. This is normal for first run.")
        return

    try:
        # Load existing config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"Found configuration file: {config_file}")

        # Define proper data types for each setting
        int_settings = {
            'font_size': 12,
            'autosave_interval': 300,
            'max_recent_files': 10,
            'tab_size': 4,
            'large_file_threshold': 10
        }

        bool_settings = {
            'autosave_enabled': True,
            'backup_files': True,
            'restore_session': True,
            'confirm_exit': True,
            'word_wrap': True,
            'line_numbers': True,
            'highlight_current_line': True,
            'show_whitespace': False,
            'auto_indent': True,
            'smart_indent': True,
            'syntax_highlighting': True,
            'spell_check_enabled': True,
            'status_bar': True,
            'show_line_endings': False,
            'enable_logging': True
        }

        str_settings = {
            'theme': 'light',
            'font_family': 'Consolas',
            'encoding': 'utf-8',
            'spell_language': 'English',
            'log_level': 'INFO'
        }

        # Fix integer values
        fixed_count = 0
        for key, default_value in int_settings.items():
            if key in config:
                old_value = config[key]
                if old_value == "" or old_value is None:
                    config[key] = default_value
                    print(f"Fixed {key}: '{old_value}' → {default_value}")
                    fixed_count += 1
                else:
                    try:
                        config[key] = int(old_value)
                    except (ValueError, TypeError):
                        config[key] = default_value
                        print(f"Fixed {key}: '{old_value}' → {default_value}")
                        fixed_count += 1

        # Fix boolean values
        for key, default_value in bool_settings.items():
            if key in config:
                old_value = config[key]
                if old_value == "" or old_value is None:
                    config[key] = default_value
                    print(f"Fixed {key}: '{old_value}' → {default_value}")
                    fixed_count += 1
                else:
                    try:
                        config[key] = bool(old_value) if old_value not in ["", "false", "False", "0"] else False
                    except (ValueError, TypeError):
                        config[key] = default_value
                        print(f"Fixed {key}: '{old_value}' → {default_value}")
                        fixed_count += 1

        # Fix string values
        for key, default_value in str_settings.items():
            if key in config:
                old_value = config[key]
                if old_value is None:
                    config[key] = default_value
                    print(f"Fixed {key}: None → '{default_value}'")
                    fixed_count += 1
                else:
                    config[key] = str(old_value)

        # Ensure recent_files is a list
        if 'recent_files' in config:
            if not isinstance(config['recent_files'], list):
                config['recent_files'] = []
                print("Fixed recent_files: converted to empty list")
                fixed_count += 1

        # Save fixed configuration
        if fixed_count > 0:
            # Create backup first
            backup_file = config_file.with_suffix('.json.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            # Save fixed config
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"\n✅ Fixed {fixed_count} configuration issues!")
            print(f"📁 Backup saved to: {backup_file}")
            print("🚀 You can now run Modern Notepad successfully!")
        else:
            print("✅ Configuration file is already correct!")

    except json.JSONDecodeError as e:
        print(f"❌ Configuration file is corrupted: {e}")
        print("🔧 Creating new configuration file...")

        # Remove corrupted file
        if config_file.exists():
            backup_file = config_file.with_suffix('.json.corrupted')
            config_file.rename(backup_file)
            print(f"📁 Corrupted file moved to: {backup_file}")

        print("✅ Corrupted configuration removed. Modern Notepad will create a new one.")

    except Exception as e:
        print(f"❌ Error fixing configuration: {e}")
        print("💡 Try deleting the configuration file manually:")
        print(f"   {config_file}")


if __name__ == "__main__":
    fix_config()
    input("\nPress Enter to exit...")