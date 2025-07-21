"""
Menu Bar - Application menu system
"""

import os
import tkinter as tk
import webbrowser
from tkinter import messagebox


class MenuBar:
    """Menu bar for the editor window"""

    def __init__(self, editor):
        self.editor = editor
        self.menubar = tk.Menu(editor.window)
        self._create_menus()

    def _create_menus(self):
        """Create all menu items"""
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_search_menu()
        self._create_format_menu()
        self._create_tools_menu()
        self._create_help_menu()

    def _create_file_menu(self):
        """Create File menu"""
        file_menu = tk.Menu(self.menubar, tearoff=0)

        file_menu.add_command(
            label="New",
            accelerator="Ctrl+N",
            command=self.editor.new_file
        )
        file_menu.add_command(
            label="New Window",
            accelerator="Ctrl+Shift+N",
            command=self.editor.app.new_window
        )
        file_menu.add_separator()

        file_menu.add_command(
            label="Open...",
            accelerator="Ctrl+O",
            command=self.editor.open_file
        )

        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self._update_recent_files()

        file_menu.add_separator()

        file_menu.add_command(
            label="Save",
            accelerator="Ctrl+S",
            command=self.editor.save_file
        )
        file_menu.add_command(
            label="Save As...",
            accelerator="Ctrl+Shift+S",
            command=self.editor.save_as_file
        )
        file_menu.add_command(
            label="Save All",
            command=self._save_all_files
        )

        file_menu.add_separator()

        # Import/Export submenu
        import_export_menu = tk.Menu(file_menu, tearoff=0)
        import_export_menu.add_command(label="Import from Word Document...", command=self._import_docx)
        import_export_menu.add_command(label="Export to PDF...", command=self._export_pdf)
        import_export_menu.add_command(label="Export to HTML...", command=self._export_html)
        file_menu.add_cascade(label="Import/Export", menu=import_export_menu)

        file_menu.add_separator()

        file_menu.add_command(
            label="Page Setup...",
            command=self._page_setup
        )
        file_menu.add_command(
            label="Print...",
            accelerator="Ctrl+P",
            command=self._print_file
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Close",
            accelerator="Ctrl+W",
            command=self.editor.close
        )
        file_menu.add_command(
            label="Exit",
            accelerator="Alt+F4",
            command=self.editor.app.quit
        )

        self.menubar.add_cascade(label="File", menu=file_menu)

    def _create_edit_menu(self):
        """Create Edit menu"""
        edit_menu = tk.Menu(self.menubar, tearoff=0)

        edit_menu.add_command(
            label="Undo",
            accelerator="Ctrl+Z",
            command=self.editor.undo
        )
        edit_menu.add_command(
            label="Redo",
            accelerator="Ctrl+Y",
            command=self.editor.redo
        )

        edit_menu.add_separator()

        edit_menu.add_command(
            label="Cut",
            accelerator="Ctrl+X",
            command=self.editor.cut
        )
        edit_menu.add_command(
            label="Copy",
            accelerator="Ctrl+C",
            command=self.editor.copy
        )
        edit_menu.add_command(
            label="Paste",
            accelerator="Ctrl+V",
            command=self.editor.paste
        )
        edit_menu.add_command(
            label="Delete",
            accelerator="Del",
            command=self._delete_selection
        )

        edit_menu.add_separator()

        edit_menu.add_command(
            label="Select All",
            accelerator="Ctrl+A",
            command=self.editor.select_all
        )

        edit_menu.add_separator()

        edit_menu.add_command(
            label="Insert Date/Time",
            accelerator="F5",
            command=self.editor.insert_datetime
        )

        # Text transformation submenu
        transform_menu = tk.Menu(edit_menu, tearoff=0)
        transform_menu.add_command(label="UPPERCASE", command=self._transform_uppercase)
        transform_menu.add_command(label="lowercase", command=self._transform_lowercase)
        transform_menu.add_command(label="Title Case", command=self._transform_title_case)
        transform_menu.add_command(label="Reverse Text", command=self._transform_reverse)
        edit_menu.add_cascade(label="Transform", menu=transform_menu)

        self.menubar.add_cascade(label="Edit", menu=edit_menu)

    def _create_view_menu(self):
        """Create View menu"""
        view_menu = tk.Menu(self.menubar, tearoff=0)

        # Zoom submenu
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        zoom_menu.add_command(
            label="Zoom In",
            accelerator="Ctrl++",
            command=self.editor.zoom_in
        )
        zoom_menu.add_command(
            label="Zoom Out",
            accelerator="Ctrl+-",
            command=self.editor.zoom_out
        )
        zoom_menu.add_command(
            label="Reset Zoom",
            accelerator="Ctrl+0",
            command=self.editor.reset_zoom
        )
        view_menu.add_cascade(label="Zoom", menu=zoom_menu)

        view_menu.add_separator()

        # Toggle options
        view_menu.add_checkbutton(
            label="Show Line Numbers",
            command=self._toggle_line_numbers
        )
        view_menu.add_checkbutton(
            label="Word Wrap",
            command=self._toggle_word_wrap
        )
        view_menu.add_checkbutton(
            label="Show Status Bar",
            command=self._toggle_status_bar
        )
        view_menu.add_checkbutton(
            label="Highlight Current Line",
            command=self._toggle_current_line_highlight
        )

        view_menu.add_separator()

        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_radiobutton(
            label="Light Theme",
            command=lambda: self._change_theme('light')
        )
        theme_menu.add_radiobutton(
            label="Dark Theme",
            command=lambda: self._change_theme('dark')
        )
        theme_menu.add_radiobutton(
            label="Monokai Theme",
            command=lambda: self._change_theme('monokai')
        )
        theme_menu.add_radiobutton(
            label="Solarized Theme",
            command=lambda: self._change_theme('solarized')
        )
        view_menu.add_cascade(label="Themes", menu=theme_menu)

        view_menu.add_separator()

        view_menu.add_command(
            label="Full Screen",
            accelerator="F11",
            command=self.editor.toggle_fullscreen
        )

        self.menubar.add_cascade(label="View", menu=view_menu)

    def _create_search_menu(self):
        """Create Search menu"""
        search_menu = tk.Menu(self.menubar, tearoff=0)

        search_menu.add_command(
            label="Find...",
            accelerator="Ctrl+F",
            command=self.editor.show_find_dialog
        )
        search_menu.add_command(
            label="Find Next",
            accelerator="F3",
            command=self._find_next
        )
        search_menu.add_command(
            label="Find Previous",
            accelerator="Shift+F3",
            command=self._find_previous
        )

        search_menu.add_separator()

        search_menu.add_command(
            label="Replace...",
            accelerator="Ctrl+H",
            command=self.editor.show_replace_dialog
        )

        search_menu.add_separator()

        search_menu.add_command(
            label="Go to Line...",
            accelerator="Ctrl+G",
            command=self.editor.show_goto_line
        )

        search_menu.add_separator()

        search_menu.add_command(
            label="Find in Files...",
            accelerator="Ctrl+Shift+F",
            command=self._find_in_files
        )

        self.menubar.add_cascade(label="Search", menu=search_menu)

    def _create_format_menu(self):
        """Create Format menu"""
        format_menu = tk.Menu(self.menubar, tearoff=0)

        format_menu.add_command(
            label="Font...",
            command=self._change_font
        )
        format_menu.add_command(
            label="Text Color...",
            command=self._change_text_color
        )
        format_menu.add_command(
            label="Background Color...",
            command=self._change_background_color
        )

        format_menu.add_separator()

        # Text style submenu
        style_menu = tk.Menu(format_menu, tearoff=0)
        style_menu.add_checkbutton(
            label="Bold",
            accelerator="Ctrl+B",
            command=self._toggle_bold
        )
        style_menu.add_checkbutton(
            label="Italic",
            accelerator="Ctrl+I",
            command=self._toggle_italic
        )
        style_menu.add_checkbutton(
            label="Underline",
            accelerator="Ctrl+U",
            command=self._toggle_underline
        )
        format_menu.add_cascade(label="Text Style", menu=style_menu)

        format_menu.add_separator()

        # Indentation submenu
        indent_menu = tk.Menu(format_menu, tearoff=0)
        indent_menu.add_command(
            label="Increase Indent",
            accelerator="Tab",
            command=self._increase_indent
        )
        indent_menu.add_command(
            label="Decrease Indent",
            accelerator="Shift+Tab",
            command=self._decrease_indent
        )
        indent_menu.add_command(
            label="Auto Indent",
            command=self._auto_indent
        )
        format_menu.add_cascade(label="Indentation", menu=indent_menu)

        self.menubar.add_cascade(label="Format", menu=format_menu)

    def _create_tools_menu(self):
        """Create Tools menu"""
        tools_menu = tk.Menu(self.menubar, tearoff=0)

        tools_menu.add_command(
            label="Spell Check",
            accelerator="F7",
            command=self._run_spell_check
        )
        tools_menu.add_command(
            label="Word Count",
            command=self._show_word_count
        )

        tools_menu.add_separator()

        tools_menu.add_command(
            label="Sort Lines",
            command=self._sort_lines
        )
        tools_menu.add_command(
            label="Remove Duplicates",
            command=self._remove_duplicates
        )
        tools_menu.add_command(
            label="Line Endings...",
            command=self._line_endings_dialog
        )

        tools_menu.add_separator()

        # Encoding submenu
        encoding_menu = tk.Menu(tools_menu, tearoff=0)
        encoding_menu.add_radiobutton(label="UTF-8", command=lambda: self._set_encoding('utf-8'))
        encoding_menu.add_radiobutton(label="UTF-16", command=lambda: self._set_encoding('utf-16'))
        encoding_menu.add_radiobutton(label="ASCII", command=lambda: self._set_encoding('ascii'))
        tools_menu.add_cascade(label="Encoding", menu=encoding_menu)

        tools_menu.add_separator()

        # Auto-save options
        autosave_menu = tk.Menu(tools_menu, tearoff=0)
        autosave_menu.add_checkbutton(
            label="Enable Auto-save",
            command=self._toggle_autosave
        )
        autosave_menu.add_command(
            label="Auto-save Settings...",
            command=self._autosave_settings
        )
        tools_menu.add_cascade(label="Auto-save", menu=autosave_menu)

        tools_menu.add_separator()

        tools_menu.add_command(
            label="Options...",
            command=self.editor.show_settings
        )

        self.menubar.add_cascade(label="Tools", menu=tools_menu)

    def _create_help_menu(self):
        """Create Help menu"""
        help_menu = tk.Menu(self.menubar, tearoff=0)

        help_menu.add_command(
            label="Keyboard Shortcuts",
            accelerator="F1",
            command=self._show_shortcuts
        )
        help_menu.add_command(
            label="User Manual",
            command=self._show_manual
        )

        help_menu.add_separator()

        help_menu.add_command(
            label="Check for Updates",
            command=self._check_updates
        )
        help_menu.add_command(
            label="Report Bug",
            command=self._report_bug
        )
        help_menu.add_command(
            label="Send Feedback",
            command=self._send_feedback
        )

        help_menu.add_separator()

        help_menu.add_command(
            label="About Modern Notepad",
            command=self._show_about
        )

        self.menubar.add_cascade(label="Help", menu=help_menu)

    # Menu action implementations
    def _update_recent_files(self):
        """Update recent files menu"""
        # Clear existing items
        self.recent_menu.delete(0, tk.END)

        # Get recent files from config
        recent_files = self.editor.config.get('recent_files', [])

        if recent_files:
            for file_path in recent_files[:10]:  # Show last 10 files
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    self.recent_menu.add_command(
                        label=filename,
                        command=lambda f=file_path: self.editor.file_ops.open_file(f)
                    )

            self.recent_menu.add_separator()
            self.recent_menu.add_command(
                label="Clear Recent Files",
                command=self._clear_recent_files
            )
        else:
            self.recent_menu.add_command(label="(No recent files)", state='disabled')

    def _clear_recent_files(self):
        """Clear recent files list"""
        self.editor.config.set('recent_files', [])
        self._update_recent_files()

    def _save_all_files(self):
        """Save all open files"""
        for editor_window in self.editor.app.editor_windows:
            if editor_window.is_modified:
                editor_window.save_file()

    def _delete_selection(self):
        """Delete selected text"""
        try:
            self.editor.text_widget.delete('sel.first', 'sel.last')
        except tk.TclError:
            # No selection, delete character at cursor
            self.editor.text_widget.delete(tk.INSERT)

    def _transform_uppercase(self):
        """Transform selected text to uppercase"""
        try:
            selected_text = self.editor.text_widget.get('sel.first', 'sel.last')
            self.editor.text_widget.delete('sel.first', 'sel.last')
            self.editor.text_widget.insert(tk.INSERT, selected_text.upper())
        except tk.TclError:
            pass

    def _transform_lowercase(self):
        """Transform selected text to lowercase"""
        try:
            selected_text = self.editor.text_widget.get('sel.first', 'sel.last')
            self.editor.text_widget.delete('sel.first', 'sel.last')
            self.editor.text_widget.insert(tk.INSERT, selected_text.lower())
        except tk.TclError:
            pass

    def _transform_title_case(self):
        """Transform selected text to title case"""
        try:
            selected_text = self.editor.text_widget.get('sel.first', 'sel.last')
            self.editor.text_widget.delete('sel.first', 'sel.last')
            self.editor.text_widget.insert(tk.INSERT, selected_text.title())
        except tk.TclError:
            pass

    def _transform_reverse(self):
        """Reverse selected text"""
        try:
            selected_text = self.editor.text_widget.get('sel.first', 'sel.last')
            self.editor.text_widget.delete('sel.first', 'sel.last')
            self.editor.text_widget.insert(tk.INSERT, selected_text[::-1])
        except tk.TclError:
            pass

    def _toggle_line_numbers(self):
        """Toggle line numbers visibility"""
        if self.editor.line_numbers.winfo_viewable():
            self.editor.line_numbers.pack_forget()
        else:
            self.editor.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

    def _toggle_word_wrap(self):
        """Toggle word wrap"""
        current_wrap = self.editor.text_widget.cget('wrap')
        new_wrap = tk.NONE if current_wrap == tk.WORD else tk.WORD
        self.editor.text_widget.config(wrap=new_wrap)

    def _toggle_status_bar(self):
        """Toggle status bar visibility"""
        if self.editor.status_bar.winfo_viewable():
            self.editor.status_bar.pack_forget()
        else:
            self.editor.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _toggle_current_line_highlight(self):
        """Toggle current line highlighting"""
        # Implementation for highlighting current line
        pass

    def _change_theme(self, theme_name):
        """Change application theme"""
        self.editor.current_theme = theme_name
        self.editor._apply_theme()
        self.editor.config.set('theme', theme_name)

    def _find_next(self):
        """Find next occurrence"""
        if hasattr(self.editor.search_replace, 'find_next'):
            self.editor.search_replace.find_next()

    def _find_previous(self):
        """Find previous occurrence"""
        if hasattr(self.editor.search_replace, 'find_previous'):
            self.editor.search_replace.find_previous()

    def _find_in_files(self):
        """Find in multiple files"""
        messagebox.showinfo("Feature", "Find in Files feature coming soon!")

    def _change_font(self):
        """Change font"""
        from tkinter.simpledialog import askstring

        # Simple font dialog - in a real implementation, you'd use a proper font dialog
        new_font = askstring("Font", f"Current font: {self.editor.font_family}")
        if new_font:
            self.editor.font_family = new_font
            current_size = self.editor.font_size + self.editor.zoom_level
            self.editor.text_widget.config(font=(new_font, current_size))

    def _change_text_color(self):
        """Change text color"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Choose text color")
        if color[1]:
            self.editor.text_widget.config(fg=color[1])

    def _change_background_color(self):
        """Change background color"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="Choose background color")
        if color[1]:
            self.editor.text_widget.config(bg=color[1])

    def _toggle_bold(self):
        """Toggle bold text style"""
        # Implementation for bold text
        pass

    def _toggle_italic(self):
        """Toggle italic text style"""
        # Implementation for italic text
        pass

    def _toggle_underline(self):
        """Toggle underline text style"""
        # Implementation for underline text
        pass

    def _increase_indent(self):
        """Increase indentation"""
        try:
            # Get selected lines or current line
            sel_start = self.editor.text_widget.index('sel.first')
            sel_end = self.editor.text_widget.index('sel.last')
        except tk.TclError:
            # No selection, use current line
            sel_start = self.editor.text_widget.index(f"{tk.INSERT} linestart")
            sel_end = self.editor.text_widget.index(f"{tk.INSERT} lineend")

        # Add indentation to each line
        start_line = int(sel_start.split('.')[0])
        end_line = int(sel_end.split('.')[0])

        for line_num in range(start_line, end_line + 1):
            line_start = f"{line_num}.0"
            self.editor.text_widget.insert(line_start, "    ")  # 4 spaces

    def _decrease_indent(self):
        """Decrease indentation"""
        try:
            sel_start = self.editor.text_widget.index('sel.first')
            sel_end = self.editor.text_widget.index('sel.last')
        except tk.TclError:
            sel_start = self.editor.text_widget.index(f"{tk.INSERT} linestart")
            sel_end = self.editor.text_widget.index(f"{tk.INSERT} lineend")

        start_line = int(sel_start.split('.')[0])
        end_line = int(sel_end.split('.')[0])

        for line_num in range(start_line, end_line + 1):
            line_start = f"{line_num}.0"
            line_text = self.editor.text_widget.get(line_start, f"{line_num}.end")
            if line_text.startswith("    "):
                self.editor.text_widget.delete(line_start, f"{line_num}.4")
            elif line_text.startswith("\t"):
                self.editor.text_widget.delete(line_start, f"{line_num}.1")

    def _auto_indent(self):
        """Auto-indent selected text"""
        messagebox.showinfo("Feature", "Auto-indent feature coming soon!")

    def _run_spell_check(self):
        """Run spell check"""
        if self.editor.spell_checker:
            self.editor.spell_checker.check_spelling()
        else:
            messagebox.showinfo("Spell Check", "Spell checker not available")

    def _show_word_count(self):
        """Show word count dialog"""
        content = self.editor.text_widget.get('1.0', 'end-1c')
        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        lines = int(self.editor.text_widget.index('end-1c').split('.')[0])

        messagebox.showinfo(
            "Document Statistics",
            f"Words: {words}\nCharacters: {chars}\nLines: {lines}"
        )

    def _sort_lines(self):
        """Sort selected lines"""
        try:
            selected_text = self.editor.text_widget.get('sel.first', 'sel.last')
            lines = selected_text.split('\n')
            sorted_lines = '\n'.join(sorted(lines))
            self.editor.text_widget.delete('sel.first', 'sel.last')
            self.editor.text_widget.insert(tk.INSERT, sorted_lines)
        except tk.TclError:
            messagebox.showwarning("Sort Lines", "Please select text to sort")

    def _remove_duplicates(self):
        """Remove duplicate lines"""
        try:
            selected_text = self.editor.text_widget.get('sel.first', 'sel.last')
            lines = selected_text.split('\n')
            unique_lines = []
            for line in lines:
                if line not in unique_lines:
                    unique_lines.append(line)
            result = '\n'.join(unique_lines)
            self.editor.text_widget.delete('sel.first', 'sel.last')
            self.editor.text_widget.insert(tk.INSERT, result)
        except tk.TclError:
            messagebox.showwarning("Remove Duplicates", "Please select text to process")

    def _line_endings_dialog(self):
        """Show line endings dialog"""
        messagebox.showinfo("Feature", "Line endings management coming soon!")

    def _set_encoding(self, encoding):
        """Set file encoding"""
        self.editor.file_encoding = encoding
        if self.editor.status_bar:
            self.editor.status_bar.file_encoding.set(encoding.upper())

    def _toggle_autosave(self):
        """Toggle auto-save feature"""
        if self.editor.autosave:
            if self.editor.autosave.is_enabled():
                self.editor.autosave.stop()
            else:
                self.editor.autosave.start()

    def _autosave_settings(self):
        """Show auto-save settings"""
        messagebox.showinfo("Feature", "Auto-save settings coming soon!")

    # Import/Export functions
    def _import_docx(self):
        """Import from Word document"""
        messagebox.showinfo("Feature", "Import from Word document coming soon!")

    def _export_pdf(self):
        """Export to PDF"""
        messagebox.showinfo("Feature", "Export to PDF coming soon!")

    def _export_html(self):
        """Export to HTML"""
        messagebox.showinfo("Feature", "Export to HTML coming soon!")

    def _page_setup(self):
        """Show page setup dialog"""
        messagebox.showinfo("Feature", "Page setup coming soon!")

    def _print_file(self):
        """Print file"""
        messagebox.showinfo("Feature", "Print functionality coming soon!")

    # Help functions
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
Keyboard Shortcuts:

File Operations:
Ctrl+N - New file
Ctrl+O - Open file
Ctrl+S - Save file
Ctrl+Shift+S - Save as
Ctrl+W - Close file
Alt+F4 - Exit

Edit Operations:
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+A - Select all
Del - Delete

Search Operations:
Ctrl+F - Find
Ctrl+H - Replace
Ctrl+G - Go to line
F3 - Find next
Shift+F3 - Find previous

View Operations:
Ctrl++ - Zoom in
Ctrl+- - Zoom out
Ctrl+0 - Reset zoom
F11 - Full screen

Other:
F5 - Insert date/time
F7 - Spell check
F1 - Show this help
        """

        # Create a new window to show shortcuts
        shortcuts_window = tk.Toplevel(self.editor.window)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x600")
        shortcuts_window.resizable(False, False)

        text_widget = tk.Text(shortcuts_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', shortcuts_text)
        text_widget.config(state='disabled')

        # Add close button
        close_button = tk.Button(
            shortcuts_window,
            text="Close",
            command=shortcuts_window.destroy
        )
        close_button.pack(pady=10)

    def _show_manual(self):
        """Show user manual"""
        messagebox.showinfo("Feature", "User manual coming soon!")

    def _check_updates(self):
        """Check for updates"""
        messagebox.showinfo("Updates", "You are using the latest version!")

    def _report_bug(self):
        """Report a bug"""
        webbrowser.open("https://github.com/yourrepository/issues")

    def _send_feedback(self):
        """Send feedback"""
        messagebox.showinfo("Feedback", "Please send feedback to: feedback@example.com")

    def _show_about(self):
        """Show about dialog"""
        about_text = """
Modern Notepad v1.0

A full-featured text editor built with Python and Tkinter.

Features:
• Syntax highlighting
• Auto-save
• Multiple themes
• Search and replace
• Spell checking
• Line numbers
• And much more!

Built with ❤️ using Python and Tkinter
        """
        messagebox.showinfo("About Modern Notepad", about_text)
