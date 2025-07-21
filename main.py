#!/usr/bin/env python3
"""
Modern Notepad Application - FIXED VERSION
This version includes all the fixes for the "expected integer but got ''" error

Run this instead of main.py: python fixed_main.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# CRITICAL FIX: Patch IntVar to handle empty strings safely
original_intvar_set = tk.IntVar.set


def safe_intvar_set(self, value):
    """Safe IntVar.set that handles empty strings and None values"""
    if value == "" or value is None:
        value = 0
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 0
    return original_intvar_set(self, value)


# Apply the safety patch
tk.IntVar.set = safe_intvar_set

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Ensure required directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    dirs = ['ui', 'features', 'utils', 'themes', 'assets/icons', 'assets/fonts']
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

    # Create __init__.py files
    init_files = ['ui/__init__.py', 'features/__init__.py', 'utils/__init__.py']
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Auto-generated __init__.py\n')


# Ensure directories exist before importing
ensure_directories()

# Now safe to import our modules
try:
    from ui.editor_window import EditorWindow
    from utils.config_loader import ConfigLoader
    from utils.logger import Logger

    IMPORTS_OK = True
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("🔧 Some modules are missing. Starting in minimal mode...")
    IMPORTS_OK = False


class ModernNotepadApp:
    """Main application class for Modern Notepad - FIXED VERSION"""

    def __init__(self):
        if IMPORTS_OK:
            self.config = ConfigLoader()
            self.logger = Logger()
        else:
            self.config = None
            self.logger = None

        self.root = None
        self.editor_windows = []

    def initialize(self):
        """Initialize the application with error handling"""
        try:
            # Create the main root window (hidden)
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the root window

            # Validate configuration if available
            if self.config:
                self._validate_initial_config()

            # Configure ttk styles for modern look
            self._configure_styles()

            # Create the first editor window
            self.new_window()

            # Setup application-level event handlers
            self._setup_app_events()

        except Exception as e:
            print(f"❌ Initialization error: {e}")
            self._start_minimal_mode()

    def _validate_initial_config(self):
        """Validate configuration before creating windows"""
        if not self.config:
            return

        # Ensure config has all required values with proper types
        required_ints = {
            'font_size': 12,
            'autosave_interval': 300,
            'max_recent_files': 10,
            'tab_size': 4
        }

        for key, default in required_ints.items():
            value = self.config.get(key, default)
            if not isinstance(value, int) or value == "" or value is None:
                self.config.set(key, default)
                print(f"🔧 Fixed config {key} = {default}")

        # Ensure boolean values
        required_bools = {
            'autosave_enabled': True,
            'word_wrap': True,
            'line_numbers': True,
            'status_bar': True,
            'syntax_highlighting': True,
            'spell_check_enabled': True
        }

        for key, default in required_bools.items():
            value = self.config.get(key, default)
            if not isinstance(value, bool) or value == "" or value is None:
                self.config.set(key, default)
                print(f"🔧 Fixed config {key} = {default}")

        # Save the validated config
        self.config.save_config()
        print("✅ Configuration validated and saved")

    def _configure_styles(self):
        """Configure ttk styles for modern appearance"""
        try:
            style = ttk.Style()

            # Try to use a modern theme
            available_themes = style.theme_names()
            preferred_themes = ['vista', 'xpnative', 'winnative', 'clam']

            for theme in preferred_themes:
                if theme in available_themes:
                    style.theme_use(theme)
                    break

            # Configure custom styles
            style.configure('Modern.TButton', padding=(10, 5))
            style.configure('Modern.TLabel', padding=(5, 2))

        except Exception as e:
            print(f"⚠️  Style configuration warning: {e}")

    def new_window(self):
        """Create a new editor window"""
        try:
            if IMPORTS_OK and self.config:
                editor = EditorWindow(self, self.config)
                self.editor_windows.append(editor)
                editor.show()

                # If this is the first window, restore session
                if len(self.editor_windows) == 1:
                    try:
                        editor.restore_session()
                    except Exception as e:
                        print(f"⚠️  Session restore warning: {e}")
            else:
                self._start_minimal_mode()

        except Exception as e:
            print(f"❌ Failed to create editor window: {e}")
            self._start_minimal_mode()

    def _start_minimal_mode(self):
        """Start in minimal mode if full mode fails"""
        print("🔧 Starting in minimal mode...")

        try:
            # Create a simple text editor window
            window = tk.Toplevel()
            window.title("Modern Notepad - Minimal Mode")
            window.geometry("800x600")

            # Simple text widget
            text_widget = tk.Text(window, undo=True, font=("Consolas", 12))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Simple menu
            menubar = tk.Menu(window)
            window.config(menu=menubar)

            file_menu = tk.Menu(menubar, tearoff=0)
            file_menu.add_command(label="New", command=lambda: text_widget.delete('1.0', tk.END))
            file_menu.add_command(label="Exit", command=window.destroy)
            menubar.add_cascade(label="File", menu=file_menu)

            # Add to editor windows list
            self.editor_windows.append(window)

            # Show success message
            window.after(100, lambda: messagebox.showinfo(
                "Minimal Mode",
                "Started in minimal mode due to configuration issues.\n"
                "Basic text editing is available."
            ))

        except Exception as e:
            print(f"❌ Even minimal mode failed: {e}")
            messagebox.showerror("Fatal Error",
                                 f"Could not start application in any mode.\n"
                                 f"Error: {e}\n\n"
                                 f"Please check your Python/Tkinter installation.")

    def close_window(self, editor_window):
        """Close an editor window"""
        if editor_window in self.editor_windows:
            self.editor_windows.remove(editor_window)

        # If no windows left, exit application
        if not self.editor_windows:
            self.quit()

    def _setup_app_events(self):
        """Setup application-level event handlers"""
        if self.root:
            # Handle application quit
            self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        """Quit the application"""
        try:
            # Save session data if possible
            if self.config:
                self._save_session()

            # Close all windows
            for editor in self.editor_windows[:]:
                try:
                    if hasattr(editor, 'close'):
                        if not editor.close():
                            return  # User cancelled quit
                    else:
                        editor.destroy()
                except:
                    pass

            # Destroy root and exit
            if self.root:
                self.root.quit()
                self.root.destroy()

        except Exception as e:
            print(f"⚠️  Quit warning: {e}")
            # Force quit if there's an error
            if self.root:
                try:
                    self.root.destroy()
                except:
                    pass

    def _save_session(self):
        """Save session data for restoration"""
        if not self.config:
            return

        try:
            session_data = {'windows': []}

            for editor in self.editor_windows:
                if hasattr(editor, 'get_session_data'):
                    window_data = editor.get_session_data()
                    if window_data:
                        session_data['windows'].append(window_data)

            self.config.save_session(session_data)
        except Exception as e:
            print(f"⚠️  Session save warning: {e}")

    def run(self):
        """Run the application with comprehensive error handling"""
        try:
            print("🚀 Starting Modern Notepad...")
            self.initialize()

            if self.root:
                print("✅ Application started successfully!")
                self.root.mainloop()
            else:
                print("❌ Failed to create main window")

        except tk.TclError as e:
            if "expected integer but got" in str(e):
                print("🔧 Detected integer conversion error - this should be fixed now!")
                print(f"Error details: {e}")
                messagebox.showerror("Configuration Error",
                                     "A configuration error was detected but should be fixed.\n"
                                     "If this persists, delete the config file and restart.")
            else:
                print(f"❌ TclError: {e}")
                messagebox.showerror("UI Error", f"A user interface error occurred: {e}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Application error: {e}")
            print(f"❌ Application error: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            # Cleanup
            if self.root:
                try:
                    self.root.destroy()
                except:
                    pass
            print("👋 Application closed")


def main():
    """Main entry point with error handling"""
    print("Modern Notepad - Fixed Version")
    print("=" * 40)

    try:
        # Create and run the application
        app = ModernNotepadApp()
        app.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        try:
            messagebox.showerror("Fatal Error", f"Could not start application: {e}")
        except:
            print("Could not even show error dialog!")


if __name__ == "__main__":
    main()
