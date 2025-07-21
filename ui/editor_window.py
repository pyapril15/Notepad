"""
Editor Window - Main text editor interface
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from features.autosave import AutoSave
from features.file_ops import FileOperations
from features.search_replace import SearchReplace
from features.spell_checker import SpellChecker
from features.syntax_highlighter import SyntaxHighlighter
from ui.menu_bar import MenuBar
from ui.settings_window import SettingsWindow


class LineNumberWidget(tk.Text):
    """Widget to display line numbers"""

    def __init__(self, parent, text_widget, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.config(
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            state='disabled',
            wrap='none',
            background='#f0f0f0',
            foreground='#666666'
        )

        # Bind text widget events
        self.text_widget.bind('<KeyPress>', self.on_key_press)
        self.text_widget.bind('<Button-1>', self.on_click)
        self.text_widget.bind('<MouseWheel>', self.on_mousewheel)

        self.update_line_numbers()

    def on_key_press(self, event=None):
        self.after_idle(self.update_line_numbers)

    def on_click(self, event=None):
        self.after_idle(self.update_line_numbers)

    def on_mousewheel(self, event=None):
        self.after_idle(self.update_line_numbers)

    def update_line_numbers(self):
        """Update line numbers display"""
        self.config(state='normal')
        self.delete('1.0', 'end')

        line_count = int(self.text_widget.index('end-1c').split('.')[0])
        line_numbers = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.insert('1.0', line_numbers)

        self.config(state='disabled')

        # Sync scrolling
        self.yview_moveto(self.text_widget.yview()[0])


class StatusBar(ttk.Frame):
    """Status bar widget"""

    def __init__(self, parent):
        super().__init__(parent)

        # Status variables
        self.cursor_pos = tk.StringVar(value="Line 1, Col 1")
        self.word_count = tk.StringVar(value="Words: 0")
        self.char_count = tk.StringVar(value="Chars: 0")
        self.file_encoding = tk.StringVar(value="UTF-8")
        self.modified_status = tk.StringVar(value="")

        # Create status widgets
        ttk.Label(self, textvariable=self.cursor_pos).pack(side=tk.LEFT, padx=5)
        ttk.Separator(self, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)
        ttk.Label(self, textvariable=self.word_count).pack(side=tk.LEFT, padx=5)
        ttk.Separator(self, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)
        ttk.Label(self, textvariable=self.char_count).pack(side=tk.LEFT, padx=5)
        ttk.Separator(self, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=2)
        ttk.Label(self, textvariable=self.file_encoding).pack(side=tk.RIGHT, padx=5)
        ttk.Label(self, textvariable=self.modified_status).pack(side=tk.RIGHT, padx=5)

    def update_cursor_position(self, line, col):
        self.cursor_pos.set(f"Line {line}, Col {col}")

    def update_counts(self, words, chars):
        self.word_count.set(f"Words: {words}")
        self.char_count.set(f"Chars: {chars}")

    def update_modified_status(self, modified):
        self.modified_status.set("•" if modified else "")


class EditorWindow:
    """Main editor window class"""

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.window = None
        self.current_file = None
        self.is_modified = False
        self.zoom_level = 0

        # UI Components
        self.text_widget = None
        self.line_numbers = None
        self.status_bar = None
        self.menu_bar = None

        # Feature modules
        self.file_ops = None
        self.search_replace = None
        self.syntax_highlighter = None
        self.spell_checker = None
        self.autosave = None

        # Theme and settings
        self.current_theme = self.config.get('theme', 'light')
        self.font_family = self.config.get('font_family', 'Consolas')
        self.font_size = self.config.get('font_size', 12)

        self._create_window()
        self._setup_ui()
        self._setup_features()
        self._setup_bindings()
        self._apply_theme()

    def _create_window(self):
        """Create the main window"""
        self.window = tk.Toplevel()
        self.window.title("Modern Notepad - Untitled")
        self.window.geometry("1000x700")
        self.window.minsize(400, 300)

        # Set window icon if available
        try:
            icon_path = os.path.join('assets', 'icons', 'notepad.ico')
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except:
            pass

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def _setup_ui(self):
        """Setup the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create menu bar
        self.menu_bar = MenuBar(self)
        self.window.config(menu=self.menu_bar.menubar)

        # Create toolbar (optional)
        self._create_toolbar(main_frame)

        # Create text editing area
        self._create_text_area(main_frame)

        # Create status bar
        self.status_bar = StatusBar(main_frame)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_toolbar(self, parent):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        # Common buttons
        ttk.Button(toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=1)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="Cut", command=self.cut).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Copy", command=self.copy).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Paste", command=self.paste).pack(side=tk.LEFT, padx=1)

        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="Find", command=self.show_find_dialog).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Replace", command=self.show_replace_dialog).pack(side=tk.LEFT, padx=1)

    def _create_text_area(self, parent):
        """Create the main text editing area"""
        # Create frame for text area
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create line number frame
        line_frame = ttk.Frame(text_frame)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create text widget with scrollbars
        text_container = ttk.Frame(text_frame)
        text_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(
            text_container,
            undo=True,
            maxundo=50,
            wrap=tk.WORD,
            font=(self.font_family, self.font_size),
            insertbackground='black',
            selectbackground='#316AC5'
        )

        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.text_widget.yview)
        h_scrollbar = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL, command=self.text_widget.xview)

        self.text_widget.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack scrollbars and text widget
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Create line numbers
        self.line_numbers = LineNumberWidget(line_frame, self.text_widget)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Setup text widget events
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<Button-1>', self._on_cursor_move)
        self.text_widget.bind('<KeyPress>', self._on_cursor_move)
        self.text_widget.bind('<<Modified>>', self._on_modified)

    def _setup_features(self):
        """Initialize feature modules"""
        self.file_ops = FileOperations(self)
        self.search_replace = SearchReplace(self)
        self.syntax_highlighter = SyntaxHighlighter(self.text_widget)
        self.spell_checker = SpellChecker(self.text_widget)
        self.autosave = AutoSave(self)

    def _setup_bindings(self):
        """Setup keyboard bindings"""
        # File operations
        self.window.bind('<Control-n>', lambda e: self.new_file())
        self.window.bind('<Control-o>', lambda e: self.open_file())
        self.window.bind('<Control-s>', lambda e: self.save_file())
        self.window.bind('<Control-Shift-S>', lambda e: self.save_as_file())

        # Edit operations
        self.window.bind('<Control-z>', lambda e: self.undo())
        self.window.bind('<Control-y>', lambda e: self.redo())
        self.window.bind('<Control-x>', lambda e: self.cut())
        self.window.bind('<Control-c>', lambda e: self.copy())
        self.window.bind('<Control-v>', lambda e: self.paste())
        self.window.bind('<Control-a>', lambda e: self.select_all())

        # Search operations
        self.window.bind('<Control-f>', lambda e: self.show_find_dialog())
        self.window.bind('<Control-h>', lambda e: self.show_replace_dialog())
        self.window.bind('<Control-g>', lambda e: self.show_goto_line())

        # Zoom operations
        self.window.bind('<Control-plus>', lambda e: self.zoom_in())
        self.window.bind('<Control-equal>', lambda e: self.zoom_in())  # For keyboards without numpad
        self.window.bind('<Control-minus>', lambda e: self.zoom_out())
        self.window.bind('<Control-0>', lambda e: self.reset_zoom())

        # Other
        self.window.bind('<F5>', lambda e: self.insert_datetime())
        self.window.bind('<F11>', lambda e: self.toggle_fullscreen())

    def _apply_theme(self):
        """Apply current theme to the editor"""
        theme_path = os.path.join('themes', f'{self.current_theme}.json')
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    theme_data = json.load(f)

                # Apply theme to text widget
                text_colors = theme_data.get('text_widget', {})
                self.text_widget.config(
                    bg=text_colors.get('background', '#ffffff'),
                    fg=text_colors.get('foreground', '#000000'),
                    insertbackground=text_colors.get('cursor', '#000000'),
                    selectbackground=text_colors.get('selection', '#316AC5')
                )

                # Update line numbers colors
                line_colors = theme_data.get('line_numbers', {})
                self.line_numbers.config(
                    bg=line_colors.get('background', '#f0f0f0'),
                    fg=line_colors.get('foreground', '#666666')
                )

            except Exception as e:
                print(f"Error loading theme: {e}")

    def _on_text_change(self, event=None):
        """Handle text changes"""
        self._update_status_bar()

        # Trigger syntax highlighting
        if self.syntax_highlighter and self.current_file:
            self.syntax_highlighter.highlight()

    def _on_cursor_move(self, event=None):
        """Handle cursor movement"""
        self.window.after_idle(self._update_status_bar)

    def _on_modified(self, event=None):
        """Handle text modification"""
        if self.text_widget.edit_modified():
            self.set_modified(True)
            self.text_widget.edit_modified(False)

    def _update_status_bar(self):
        """Update status bar information"""
        # Get cursor position
        cursor_pos = self.text_widget.index(tk.INSERT)
        line, col = cursor_pos.split('.')
        self.status_bar.update_cursor_position(int(line), int(col) + 1)

        # Get text statistics
        content = self.text_widget.get('1.0', 'end-1c')
        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        self.status_bar.update_counts(words, chars)

        # Update modified status
        self.status_bar.update_modified_status(self.is_modified)

    def set_modified(self, modified=True):
        """Set the modified state"""
        self.is_modified = modified
        title = self.window.title()

        if modified and not title.endswith(' *'):
            self.window.title(title + ' *')
        elif not modified and title.endswith(' *'):
            self.window.title(title[:-2])

    def show(self):
        """Show the editor window"""
        self.window.deiconify()
        self.window.lift()
        self.text_widget.focus_set()

    def close(self):
        """Close the editor window"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Save Changes",
                f"Do you want to save changes to {self.get_display_name()}?"
            )
            if result is None:  # Cancel
                return False
            elif result:  # Yes, save
                if not self.save_file():
                    return False

        # Stop autosave
        if self.autosave:
            self.autosave.stop()

        # Close window
        self.window.destroy()
        self.app.close_window(self)
        return True

    def get_display_name(self):
        """Get display name for the file"""
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Untitled"

    def get_session_data(self):
        """Get session data for saving"""
        if self.current_file:
            return {
                'file_path': self.current_file,
                'cursor_position': self.text_widget.index(tk.INSERT)
            }
        return None

    def restore_session(self):
        """Restore session data"""
        session_data = self.config.get_session()
        if session_data and 'windows' in session_data:
            windows = session_data['windows']
            if windows:
                # Restore first window in this instance
                window_data = windows[0]
                if 'file_path' in window_data and os.path.exists(window_data['file_path']):
                    self.file_ops.open_file(window_data['file_path'])
                    if 'cursor_position' in window_data:
                        self.text_widget.mark_set(tk.INSERT, window_data['cursor_position'])
                        self.text_widget.see(tk.INSERT)

                # Create additional windows for remaining files
                for window_data in windows[1:]:
                    if 'file_path' in window_data and os.path.exists(window_data['file_path']):
                        self.app.new_window()
                        # The new window will handle its own restoration

    # File operations
    def new_file(self):
        self.file_ops.new_file()

    def open_file(self):
        self.file_ops.open_file()

    def save_file(self):
        return self.file_ops.save_file()

    def save_as_file(self):
        return self.file_ops.save_as_file()

    # Edit operations
    def undo(self):
        try:
            self.text_widget.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text_widget.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        self.text_widget.event_generate("<<Cut>>")

    def copy(self):
        self.text_widget.event_generate("<<Copy>>")

    def paste(self):
        self.text_widget.event_generate("<<Paste>>")

    def select_all(self):
        self.text_widget.tag_add('sel', '1.0', 'end-1c')
        self.text_widget.mark_set(tk.INSERT, '1.0')
        self.text_widget.see(tk.INSERT)
        return 'break'

    # Search operations
    def show_find_dialog(self):
        self.search_replace.show_find_dialog()

    def show_replace_dialog(self):
        self.search_replace.show_replace_dialog()

    def show_goto_line(self):
        self.search_replace.show_goto_line_dialog()

    # View operations
    def zoom_in(self):
        self.zoom_level += 1
        new_size = self.font_size + self.zoom_level
        self.text_widget.config(font=(self.font_family, new_size))

    def zoom_out(self):
        self.zoom_level -= 1
        new_size = max(8, self.font_size + self.zoom_level)
        self.text_widget.config(font=(self.font_family, new_size))

    def reset_zoom(self):
        self.zoom_level = 0
        self.text_widget.config(font=(self.font_family, self.font_size))

    def toggle_fullscreen(self):
        is_fullscreen = self.window.attributes('-fullscreen')
        self.window.attributes('-fullscreen', not is_fullscreen)

    # Utility functions
    def insert_datetime(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_widget.insert(tk.INSERT, current_time)

    def show_settings(self):
        """Show settings window"""
        SettingsWindow(self)
