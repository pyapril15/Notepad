"""
Settings Window - Application settings and preferences
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog, font


class SettingsWindow:
    """Settings and preferences window"""

    def __init__(self, editor):
        self.editor = editor
        self.config = editor.config

        # Validate config before proceeding
        self._validate_config()

        # Store original settings for cancel functionality
        self.original_settings = self.config.get_all().copy()

        # Create settings window
        self.window = tk.Toplevel(editor.window)
        self.window.title("Settings")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        self.window.transient(editor.window)
        self.window.grab_set()

        # Center the window
        self._center_window()

        # Create UI
        self._create_ui()

        # Load current settings
        self._load_settings()

        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _validate_config(self):
        """Validate configuration has proper types"""
        # Ensure all integer settings have integer values
        int_keys = ['font_size', 'autosave_interval', 'max_recent_files', 'tab_size', 'large_file_threshold']
        for key in int_keys:
            value = self.config.get(key)
            if not isinstance(value, int) or value == "":
                default_value = self.config.default_config.get(key, 12)
                self.config.set(key, default_value)
                print(f"Fixed config {key}: set to {default_value}")

        # Ensure all boolean settings have boolean values
        bool_keys = ['autosave_enabled', 'backup_files', 'restore_session', 'confirm_exit',
                     'word_wrap', 'line_numbers', 'highlight_current_line', 'show_whitespace',
                     'auto_indent', 'smart_indent', 'syntax_highlighting', 'spell_check_enabled',
                     'status_bar', 'show_line_endings', 'enable_logging']
        for key in bool_keys:
            value = self.config.get(key)
            if not isinstance(value, bool) or value == "":
                default_value = self.config.default_config.get(key, True)
                self.config.set(key, default_value)
                print(f"Fixed config {key}: set to {default_value}")

    def _center_window(self):
        """Center the settings window on the parent window"""
        self.window.update_idletasks()

        # Get parent window position and size
        parent_x = self.editor.window.winfo_x()
        parent_y = self.editor.window.winfo_y()
        parent_width = self.editor.window.winfo_width()
        parent_height = self.editor.window.winfo_height()

        # Calculate center position
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()

        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _create_ui(self):
        """Create the settings user interface"""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create tabs
        self._create_general_tab()
        self._create_editor_tab()
        self._create_appearance_tab()
        self._create_advanced_tab()

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)

        # Buttons
        ttk.Button(buttons_frame, text="OK", command=self._apply_and_close).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Apply", command=self._apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT)

    def _create_general_tab(self):
        """Create general settings tab"""
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="General")

        # File handling
        file_group = ttk.LabelFrame(general_frame, text="File Handling", padding="10")
        file_group.pack(fill=tk.X, pady=(0, 10))

        self.auto_save_var = tk.BooleanVar()
        ttk.Checkbutton(
            file_group,
            text="Enable auto-save",
            variable=self.auto_save_var
        ).pack(anchor=tk.W)

        # Auto-save interval
        interval_frame = ttk.Frame(file_group)
        interval_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(interval_frame, text="Auto-save interval (seconds):").pack(side=tk.LEFT)
        self.auto_save_interval_var = tk.IntVar()
        interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=30,
            to=3600,
            textvariable=self.auto_save_interval_var,
            width=10
        )
        interval_spinbox.pack(side=tk.RIGHT)

        self.backup_files_var = tk.BooleanVar()
        ttk.Checkbutton(
            file_group,
            text="Create backup files",
            variable=self.backup_files_var
        ).pack(anchor=tk.W, pady=(5, 0))

        self.restore_session_var = tk.BooleanVar()
        ttk.Checkbutton(
            file_group,
            text="Restore session on startup",
            variable=self.restore_session_var
        ).pack(anchor=tk.W, pady=(5, 0))

        # Recent files
        recent_frame = ttk.Frame(file_group)
        recent_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(recent_frame, text="Max recent files:").pack(side=tk.LEFT)
        self.max_recent_var = tk.IntVar()
        recent_spinbox = ttk.Spinbox(
            recent_frame,
            from_=5,
            to=50,
            textvariable=self.max_recent_var,
            width=10
        )
        recent_spinbox.pack(side=tk.RIGHT)

        # Application behavior
        behavior_group = ttk.LabelFrame(general_frame, text="Application Behavior", padding="10")
        behavior_group.pack(fill=tk.X, pady=(0, 10))

        self.confirm_exit_var = tk.BooleanVar()
        ttk.Checkbutton(
            behavior_group,
            text="Confirm before exit",
            variable=self.confirm_exit_var
        ).pack(anchor=tk.W)

        # Default encoding
        encoding_frame = ttk.Frame(behavior_group)
        encoding_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(encoding_frame, text="Default encoding:").pack(side=tk.LEFT)
        self.encoding_var = tk.StringVar()
        encoding_combo = ttk.Combobox(
            encoding_frame,
            textvariable=self.encoding_var,
            values=['utf-8', 'utf-16', 'ascii', 'latin-1', 'cp1252'],
            state='readonly',
            width=15
        )
        encoding_combo.pack(side=tk.RIGHT)

    def _create_editor_tab(self):
        """Create editor settings tab"""
        editor_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(editor_frame, text="Editor")

        # Text editing
        text_group = ttk.LabelFrame(editor_frame, text="Text Editing", padding="10")
        text_group.pack(fill=tk.X, pady=(0, 10))

        self.word_wrap_var = tk.BooleanVar()
        ttk.Checkbutton(
            text_group,
            text="Word wrap",
            variable=self.word_wrap_var
        ).pack(anchor=tk.W)

        self.line_numbers_var = tk.BooleanVar()
        ttk.Checkbutton(
            text_group,
            text="Show line numbers",
            variable=self.line_numbers_var
        ).pack(anchor=tk.W)

        self.highlight_current_line_var = tk.BooleanVar()
        ttk.Checkbutton(
            text_group,
            text="Highlight current line",
            variable=self.highlight_current_line_var
        ).pack(anchor=tk.W)

        self.show_whitespace_var = tk.BooleanVar()
        ttk.Checkbutton(
            text_group,
            text="Show whitespace characters",
            variable=self.show_whitespace_var
        ).pack(anchor=tk.W)

        # Tab settings
        tab_frame = ttk.Frame(text_group)
        tab_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(tab_frame, text="Tab size:").pack(side=tk.LEFT)
        self.tab_size_var = tk.IntVar()
        tab_spinbox = ttk.Spinbox(
            tab_frame,
            from_=2,
            to=8,
            textvariable=self.tab_size_var,
            width=5
        )
        tab_spinbox.pack(side=tk.RIGHT)

        # Auto-indent
        self.auto_indent_var = tk.BooleanVar()
        ttk.Checkbutton(
            text_group,
            text="Auto-indent",
            variable=self.auto_indent_var
        ).pack(anchor=tk.W, pady=(5, 0))

        self.smart_indent_var = tk.BooleanVar()
        ttk.Checkbutton(
            text_group,
            text="Smart indent",
            variable=self.smart_indent_var
        ).pack(anchor=tk.W)

        # Syntax highlighting
        syntax_group = ttk.LabelFrame(editor_frame, text="Syntax Highlighting", padding="10")
        syntax_group.pack(fill=tk.X, pady=(0, 10))

        self.syntax_highlighting_var = tk.BooleanVar()
        ttk.Checkbutton(
            syntax_group,
            text="Enable syntax highlighting",
            variable=self.syntax_highlighting_var
        ).pack(anchor=tk.W)

        # Spell checking
        spell_group = ttk.LabelFrame(editor_frame, text="Spell Checking", padding="10")
        spell_group.pack(fill=tk.X)

        self.spell_check_var = tk.BooleanVar()
        ttk.Checkbutton(
            spell_group,
            text="Enable spell checking",
            variable=self.spell_check_var
        ).pack(anchor=tk.W)

        # Spell check language
        lang_frame = ttk.Frame(spell_group)
        lang_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        self.spell_language_var = tk.StringVar()
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.spell_language_var,
            values=['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese'],
            state='readonly',
            width=15
        )
        lang_combo.pack(side=tk.RIGHT)

    def _create_appearance_tab(self):
        """Create appearance settings tab"""
        appearance_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(appearance_frame, text="Appearance")

        # Theme selection
        theme_group = ttk.LabelFrame(appearance_frame, text="Theme", padding="10")
        theme_group.pack(fill=tk.X, pady=(0, 10))

        self.theme_var = tk.StringVar()

        # Get available themes
        available_themes = self._get_available_themes()

        for theme in available_themes:
            ttk.Radiobutton(
                theme_group,
                text=theme.title(),
                variable=self.theme_var,
                value=theme
            ).pack(anchor=tk.W)

        # Custom theme
        custom_theme_frame = ttk.Frame(theme_group)
        custom_theme_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            custom_theme_frame,
            text="Load Custom Theme...",
            command=self._load_custom_theme
        ).pack(side=tk.LEFT)

        ttk.Button(
            custom_theme_frame,
            text="Export Current Theme...",
            command=self._export_theme
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Font settings
        font_group = ttk.LabelFrame(appearance_frame, text="Font", padding="10")
        font_group.pack(fill=tk.X, pady=(0, 10))

        # Font family
        family_frame = ttk.Frame(font_group)
        family_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(family_frame, text="Font family:").pack(side=tk.LEFT)
        self.font_family_var = tk.StringVar()

        # Get available fonts
        available_fonts = sorted(font.families())
        font_combo = ttk.Combobox(
            family_frame,
            textvariable=self.font_family_var,
            values=available_fonts,
            width=20
        )
        font_combo.pack(side=tk.RIGHT)

        # Font size
        size_frame = ttk.Frame(font_group)
        size_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(size_frame, text="Font size:").pack(side=tk.LEFT)
        self.font_size_var = tk.IntVar()
        size_spinbox = ttk.Spinbox(
            size_frame,
            from_=8,
            to=72,
            textvariable=self.font_size_var,
            width=5
        )
        size_spinbox.pack(side=tk.RIGHT)

        # Font preview
        preview_frame = ttk.LabelFrame(font_group, text="Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(5, 0))

        self.font_preview = tk.Text(
            preview_frame,
            height=3,
            wrap=tk.WORD,
            state='disabled'
        )
        self.font_preview.pack(fill=tk.X)

        # Update preview when font changes
        font_combo.bind('<<ComboboxSelected>>', self._update_font_preview)
        size_spinbox.bind('<KeyRelease>', self._update_font_preview)

        # UI settings
        ui_group = ttk.LabelFrame(appearance_frame, text="User Interface", padding="10")
        ui_group.pack(fill=tk.X)

        self.status_bar_var = tk.BooleanVar()
        ttk.Checkbutton(
            ui_group,
            text="Show status bar",
            variable=self.status_bar_var
        ).pack(anchor=tk.W)

        self.show_line_endings_var = tk.BooleanVar()
        ttk.Checkbutton(
            ui_group,
            text="Show line endings",
            variable=self.show_line_endings_var
        ).pack(anchor=tk.W)

    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="Advanced")

        # Performance
        perf_group = ttk.LabelFrame(advanced_frame, text="Performance", padding="10")
        perf_group.pack(fill=tk.X, pady=(0, 10))

        # Large file threshold
        threshold_frame = ttk.Frame(perf_group)
        threshold_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(threshold_frame, text="Large file threshold (MB):").pack(side=tk.LEFT)
        self.large_file_threshold_var = tk.IntVar()
        threshold_spinbox = ttk.Spinbox(
            threshold_frame,
            from_=1,
            to=100,
            textvariable=self.large_file_threshold_var,
            width=5
        )
        threshold_spinbox.pack(side=tk.RIGHT)

        # Logging
        log_group = ttk.LabelFrame(advanced_frame, text="Logging", padding="10")
        log_group.pack(fill=tk.X, pady=(0, 10))

        self.enable_logging_var = tk.BooleanVar()
        ttk.Checkbutton(
            log_group,
            text="Enable logging",
            variable=self.enable_logging_var
        ).pack(anchor=tk.W)

        # Log level
        level_frame = ttk.Frame(log_group)
        level_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(level_frame, text="Log level:").pack(side=tk.LEFT)
        self.log_level_var = tk.StringVar()
        level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.log_level_var,
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            state='readonly',
            width=10
        )
        level_combo.pack(side=tk.RIGHT)

        # Plugin settings
        plugin_group = ttk.LabelFrame(advanced_frame, text="Plugins", padding="10")
        plugin_group.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(plugin_group, text="Plugin support coming soon...").pack(anchor=tk.W)

        # Export/Import settings
        export_group = ttk.LabelFrame(advanced_frame, text="Settings Management", padding="10")
        export_group.pack(fill=tk.X)

        export_frame = ttk.Frame(export_group)
        export_frame.pack(fill=tk.X)

        ttk.Button(
            export_frame,
            text="Export Settings...",
            command=self._export_settings
        ).pack(side=tk.LEFT)

        ttk.Button(
            export_frame,
            text="Import Settings...",
            command=self._import_settings
        ).pack(side=tk.LEFT, padx=(5, 0))

    def _get_available_themes(self):
        """Get list of available themes"""
        themes = ['light', 'dark']

        # Check for additional theme files
        themes_dir = Path('themes')
        if themes_dir.exists():
            for theme_file in themes_dir.glob('*.json'):
                theme_name = theme_file.stem
                if theme_name not in themes:
                    themes.append(theme_name)

        return themes

    def _load_settings(self):
        """Load current settings into the UI"""
        # General settings
        self.auto_save_var.set(self.config.get('autosave_enabled', True))
        self.auto_save_interval_var.set(self.config.get('autosave_interval', 300))
        self.backup_files_var.set(self.config.get('backup_files', True))
        self.restore_session_var.set(self.config.get('restore_session', True))
        self.max_recent_var.set(self.config.get('max_recent_files', 10))
        self.confirm_exit_var.set(self.config.get('confirm_exit', True))
        self.encoding_var.set(self.config.get('encoding', 'utf-8'))

        # Editor settings
        self.word_wrap_var.set(self.config.get('word_wrap', True))
        self.line_numbers_var.set(self.config.get('line_numbers', True))
        self.highlight_current_line_var.set(self.config.get('highlight_current_line', True))
        self.show_whitespace_var.set(self.config.get('show_whitespace', False))
        self.tab_size_var.set(self.config.get('tab_size', 4))
        self.auto_indent_var.set(self.config.get('auto_indent', True))
        self.smart_indent_var.set(self.config.get('smart_indent', True))
        self.syntax_highlighting_var.set(self.config.get('syntax_highlighting', True))
        self.spell_check_var.set(self.config.get('spell_check_enabled', True))
        self.spell_language_var.set(self.config.get('spell_language', 'English'))

        # Appearance settings
        self.theme_var.set(self.config.get('theme', 'light'))
        self.font_family_var.set(self.config.get('font_family', 'Consolas'))
        self.font_size_var.set(self.config.get('font_size', 12))
        self.status_bar_var.set(self.config.get('status_bar', True))
        self.show_line_endings_var.set(self.config.get('show_line_endings', False))

        # Advanced settings
        self.large_file_threshold_var.set(self.config.get('large_file_threshold', 10))
        self.enable_logging_var.set(self.config.get('enable_logging', True))
        self.log_level_var.set(self.config.get('log_level', 'INFO'))

        # Update font preview
        self._update_font_preview()

    def _update_font_preview(self, event=None):
        """Update font preview"""
        try:
            family = self.font_family_var.get()
            size = self.font_size_var.get()

            if family and size:
                font_tuple = (family, size)
                self.font_preview.config(state='normal', font=font_tuple)
                self.font_preview.delete('1.0', 'end')
                self.font_preview.insert('1.0',
                                         f"The quick brown fox jumps over the lazy dog.\n123456789\n{family} {size}pt")
                self.font_preview.config(state='disabled')
        except:
            pass

    def _apply_settings(self):
        """Apply settings without closing window"""
        # General settings
        self.config.set('autosave_enabled', self.auto_save_var.get())
        self.config.set('autosave_interval', self.auto_save_interval_var.get())
        self.config.set('backup_files', self.backup_files_var.get())
        self.config.set('restore_session', self.restore_session_var.get())
        self.config.set('max_recent_files', self.max_recent_var.get())
        self.config.set('confirm_exit', self.confirm_exit_var.get())
        self.config.set('encoding', self.encoding_var.get())

        # Editor settings
        self.config.set('word_wrap', self.word_wrap_var.get())
        self.config.set('line_numbers', self.line_numbers_var.get())
        self.config.set('highlight_current_line', self.highlight_current_line_var.get())
        self.config.set('show_whitespace', self.show_whitespace_var.get())
        self.config.set('tab_size', self.tab_size_var.get())
        self.config.set('auto_indent', self.auto_indent_var.get())
        self.config.set('smart_indent', self.smart_indent_var.get())
        self.config.set('syntax_highlighting', self.syntax_highlighting_var.get())
        self.config.set('spell_check_enabled', self.spell_check_var.get())
        self.config.set('spell_language', self.spell_language_var.get())

        # Appearance settings
        self.config.set('theme', self.theme_var.get())
        self.config.set('font_family', self.font_family_var.get())
        self.config.set('font_size', self.font_size_var.get())
        self.config.set('status_bar', self.status_bar_var.get())
        self.config.set('show_line_endings', self.show_line_endings_var.get())

        # Advanced settings
        self.config.set('large_file_threshold', self.large_file_threshold_var.get())
        self.config.set('enable_logging', self.enable_logging_var.get())
        self.config.set('log_level', self.log_level_var.get())

        # Apply changes to editor
        self._apply_to_editor()

        messagebox.showinfo("Settings", "Settings applied successfully!")

    def _apply_to_editor(self):
        """Apply settings to the current editor"""
        # Font changes
        font_family = self.font_family_var.get()
        font_size = self.font_size_var.get()

        if font_family and font_size:
            self.editor.font_family = font_family
            self.editor.font_size = font_size
            current_size = font_size + self.editor.zoom_level
            self.editor.text_widget.config(font=(font_family, current_size))

        # Theme changes
        if self.theme_var.get() != self.editor.current_theme:
            self.editor.current_theme = self.theme_var.get()
            self.editor._apply_theme()

        # Word wrap
        wrap_mode = tk.WORD if self.word_wrap_var.get() else tk.NONE
        self.editor.text_widget.config(wrap=wrap_mode)

        # Line numbers
        if self.line_numbers_var.get():
            if not self.editor.line_numbers.winfo_viewable():
                self.editor.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        else:
            if self.editor.line_numbers.winfo_viewable():
                self.editor.line_numbers.pack_forget()

        # Status bar
        if self.status_bar_var.get():
            if not self.editor.status_bar.winfo_viewable():
                self.editor.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            if self.editor.status_bar.winfo_viewable():
                self.editor.status_bar.pack_forget()

        # Auto-save settings
        if hasattr(self.editor, 'autosave'):
            self.editor.autosave.set_enabled(self.auto_save_var.get())
            self.editor.autosave.set_interval(self.auto_save_interval_var.get())

        # Spell check settings
        if hasattr(self.editor, 'spell_checker'):
            if not self.spell_check_var.get():
                self.editor.spell_checker.toggle_spell_check()

    def _apply_and_close(self):
        """Apply settings and close window"""
        self._apply_settings()
        self.window.destroy()

    def _cancel(self):
        """Cancel changes and close window"""
        self.window.destroy()

    def _reset_defaults(self):
        """Reset all settings to defaults"""
        result = messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?"
        )

        if result:
            self.config.reset_to_defaults()
            self._load_settings()
            messagebox.showinfo("Settings", "Settings reset to defaults!")

    def _on_close(self):
        """Handle window close event"""
        self._cancel()

    def _load_custom_theme(self):
        """Load custom theme file"""
        file_path = filedialog.askopenfilename(
            title="Load Custom Theme",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    theme_data = json.load(f)

                # Validate theme structure
                required_keys = ['name', 'text_widget', 'line_numbers', 'syntax']
                if all(key in theme_data for key in required_keys):
                    # Copy theme to themes directory
                    theme_name = theme_data.get('name', 'custom').lower().replace(' ', '_')
                    themes_dir = Path('themes')
                    themes_dir.mkdir(exist_ok=True)

                    new_theme_path = themes_dir / f"{theme_name}.json"
                    with open(new_theme_path, 'w') as f:
                        json.dump(theme_data, f, indent=2)

                    # Update theme selection
                    self.theme_var.set(theme_name)

                    messagebox.showinfo("Theme Loaded", f"Theme '{theme_name}' loaded successfully!")
                else:
                    messagebox.showerror("Invalid Theme", "The selected file is not a valid theme file.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load theme: {e}")

    def _export_theme(self):
        """Export current theme"""
        file_path = filedialog.asksaveasfilename(
            title="Export Theme",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )

        if file_path:
            try:
                current_theme = self.theme_var.get()
                theme_path = Path('themes') / f"{current_theme}.json"

                if theme_path.exists():
                    # Copy existing theme file
                    with open(theme_path, 'r') as f:
                        theme_data = json.load(f)

                    with open(file_path, 'w') as f:
                        json.dump(theme_data, f, indent=2)

                    messagebox.showinfo("Theme Exported", f"Theme exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Current theme file not found.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export theme: {e}")

    def _export_settings(self):
        """Export all settings"""
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )

        if file_path:
            if self.config.export_config(file_path):
                messagebox.showinfo("Settings Exported", f"Settings exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export settings.")

    def _import_settings(self):
        """Import settings from file"""
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            result = messagebox.askyesno(
                "Import Settings",
                "Importing settings will overwrite your current configuration. Continue?"
            )

            if result:
                if self.config.import_config(file_path):
                    self._load_settings()
                    messagebox.showinfo("Settings Imported", "Settings imported successfully!")
                else:
                    messagebox.showerror("Error", "Failed to import settings.")
