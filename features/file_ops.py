"""
File Operations - Handles all file-related operations
"""

import os
import shutil
import tempfile
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import chardet


class FileOperations:
    """Handles file operations for the editor"""

    def __init__(self, editor):
        self.editor = editor
        self.backup_dir = Path.home() / '.modern_notepad' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Supported file types
        self.file_types = [
            ("Text files", "*.txt"),
            ("Python files", "*.py"),
            ("JavaScript files", "*.js"),
            ("HTML files", "*.html *.htm"),
            ("CSS files", "*.css"),
            ("JSON files", "*.json"),
            ("XML files", "*.xml"),
            ("Markdown files", "*.md *.markdown"),
            ("Config files", "*.ini *.cfg *.conf"),
            ("Log files", "*.log"),
            ("All files", "*.*")
        ]

        # Default encoding
        self.default_encoding = 'utf-8'

        # File watchers (for detecting external changes)
        self.file_watchers = {}

    def new_file(self):
        """Create a new file"""
        if self.editor.is_modified:
            result = messagebox.askyesnocancel(
                "New File",
                "Do you want to save changes to the current file?"
            )
            if result is None:  # Cancel
                return False
            elif result:  # Yes, save
                if not self.save_file():
                    return False

        # Clear the text widget
        self.editor.text_widget.delete('1.0', 'end')

        # Reset file state
        self.editor.current_file = None
        self.editor.set_modified(False)
        self.editor.window.title("Modern Notepad - Untitled")

        # Clear undo history
        self.editor.text_widget.edit_reset()

        # Log action
        self.editor.app.logger.log_user_action("New file created")
        return True

    def open_file(self, file_path=None):
        """Open a file"""
        if file_path is None:
            file_path = filedialog.askopenfilename(
                title="Open File",
                filetypes=self.file_types,
                defaultextension=".txt"
            )

        if not file_path:
            return False

        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            # Remove from recent files if it was there
            self.editor.config.remove_recent_file(file_path)
            return False

        # Check if file is already open in another window
        for editor_window in self.editor.app.editor_windows:
            if editor_window.current_file == file_path:
                editor_window.window.lift()
                editor_window.window.focus_set()
                return True

        # Check for unsaved changes
        if self.editor.is_modified:
            result = messagebox.askyesnocancel(
                "Open File",
                "Do you want to save changes to the current file?"
            )
            if result is None:  # Cancel
                return False
            elif result:  # Yes, save
                if not self.save_file():
                    return False

        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)

            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            # Set content in text widget
            self.editor.text_widget.delete('1.0', 'end')
            self.editor.text_widget.insert('1.0', content)

            # Update editor state
            self.editor.current_file = file_path
            self.editor.set_modified(False)
            self.editor.window.title(f"Modern Notepad - {os.path.basename(file_path)}")

            # Clear undo history
            self.editor.text_widget.edit_reset()

            # Add to recent files
            self.editor.config.add_recent_file(file_path)

            # Update syntax highlighting
            if self.editor.syntax_highlighter:
                self.editor.syntax_highlighter.set_file_type(file_path)
                self.editor.syntax_highlighter.highlight()

            # Start file watcher
            self._start_file_watcher(file_path)

            # Log success
            self.editor.app.logger.log_file_operation("Open file", file_path, True)
            return True

        except Exception as e:
            error_msg = f"Error opening file: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.editor.app.logger.log_file_operation("Open file", file_path, False)
            self.editor.app.logger.log_error_with_context(str(e), f"Opening file: {file_path}")
            return False

    def save_file(self):
        """Save the current file"""
        if self.editor.current_file is None:
            return self.save_as_file()

        return self._save_to_file(self.editor.current_file)

    def save_as_file(self):
        """Save file with a new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            filetypes=self.file_types,
            defaultextension=".txt"
        )

        if not file_path:
            return False

        if self._save_to_file(file_path):
            self.editor.current_file = file_path
            self.editor.window.title(f"Modern Notepad - {os.path.basename(file_path)}")

            # Add to recent files
            self.editor.config.add_recent_file(file_path)

            # Update syntax highlighting
            if self.editor.syntax_highlighter:
                self.editor.syntax_highlighter.set_file_type(file_path)
                self.editor.syntax_highlighter.highlight()

            # Start file watcher
            self._start_file_watcher(file_path)

            return True

        return False

    def _save_to_file(self, file_path):
        """Save content to specified file"""
        try:
            # Create backup if enabled
            if self.editor.config.get('backup_files', True) and os.path.exists(file_path):
                self._create_backup(file_path)

            # Get content from text widget
            content = self.editor.text_widget.get('1.0', 'end-1c')

            # Determine encoding
            encoding = self.editor.config.get('encoding', 'utf-8')

            # Write to temporary file first, then move (atomic save)
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                        mode='w',
                        encoding=encoding,
                        delete=False,
                        dir=os.path.dirname(file_path),
                        prefix=f".{os.path.basename(file_path)}.tmp"
                ) as f:
                    f.write(content)
                    temp_file = f.name

                # Move temporary file to target
                shutil.move(temp_file, file_path)

            except Exception as e:
                # Clean up temporary file if something went wrong
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                raise e

            # Update editor state
            self.editor.set_modified(False)

            # Log success
            self.editor.app.logger.log_file_operation("Save file", file_path, True)
            return True

        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.editor.app.logger.log_file_operation("Save file", file_path, False)
            self.editor.app.logger.log_error_with_context(str(e), f"Saving file: {file_path}")
            return False

    def _detect_encoding(self, file_path):
        """Detect file encoding"""
        try:
            # Read a sample of the file
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB

            # Detect encoding
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', self.default_encoding)

            # Fallback to common encodings if detection fails
            if not encoding or result.get('confidence', 0) < 0.7:
                for test_encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                    try:
                        with open(file_path, 'r', encoding=test_encoding) as f:
                            f.read(1000)  # Try to read first 1KB
                        encoding = test_encoding
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    encoding = self.default_encoding

            return encoding

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Error detecting encoding: {e}",
                f"File: {file_path}"
            )
            return self.default_encoding

    def _create_backup(self, file_path):
        """Create a backup of the file"""
        try:
            if not os.path.exists(file_path):
                return

            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_name = f"{filename}.{timestamp}.bak"
            backup_path = self.backup_dir / backup_name

            # Copy file to backup location
            shutil.copy2(file_path, backup_path)

            # Clean up old backups (keep last 10 for each file)
            self._cleanup_backups(filename)

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Error creating backup: {e}",
                f"File: {file_path}"
            )

    def _cleanup_backups(self, filename):
        """Clean up old backup files"""
        try:
            # Find all backups for this file
            backup_pattern = f"{filename}.*.bak"
            backups = list(self.backup_dir.glob(backup_pattern))

            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove old backups (keep only the 10 most recent)
            for backup in backups[10:]:
                backup.unlink()

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Error cleaning up backups: {e}",
                f"Pattern: {filename}.*.bak"
            )

    def _start_file_watcher(self, file_path):
        """Start watching file for external changes"""
        # This is a placeholder for file watching functionality
        # In a full implementation, you would use a library like watchdog
        pass

    def get_file_stats(self, file_path=None):
        """Get file statistics"""
        if file_path is None:
            file_path = self.editor.current_file

        if not file_path or not os.path.exists(file_path):
            return None

        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK)
            }
        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Error getting file stats: {e}",
                f"File: {file_path}"
            )
            return None

    def reload_file(self):
        """Reload the current file from disk"""
        if not self.editor.current_file:
            messagebox.showwarning("Warning", "No file is currently open")
            return False

        if self.editor.is_modified:
            result = messagebox.askyesnocancel(
                "Reload File",
                "File has been modified. Reload will lose your changes. Continue?"
            )
            if not result:
                return False

        # Save cursor position
        cursor_pos = self.editor.text_widget.index(tk.INSERT)

        # Reload file
        success = self.open_file(self.editor.current_file)

        if success:
            # Restore cursor position
            try:
                self.editor.text_widget.mark_set(tk.INSERT, cursor_pos)
                self.editor.text_widget.see(tk.INSERT)
            except tk.TclError:
                pass  # Invalid position, ignore

        return success

    def export_to_html(self, file_path=None):
        """Export content as HTML"""
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                title="Export to HTML",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                defaultextension=".html"
            )

        if not file_path:
            return False

        try:
            content = self.editor.text_widget.get('1.0', 'end-1c')

            # Simple HTML template
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(self.editor.current_file or 'Untitled')}</title>
    <style>
        body {{
            font-family: monospace;
            white-space: pre-wrap;
            margin: 20px;
            background-color: #ffffff;
            color: #000000;
        }}
    </style>
</head>
<body>
{self._escape_html(content)}
</body>
</html>"""

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.editor.app.logger.log_file_operation("Export to HTML", file_path, True)
            messagebox.showinfo("Success", f"File exported to: {file_path}")
            return True

        except Exception as e:
            error_msg = f"Error exporting to HTML: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.editor.app.logger.log_file_operation("Export to HTML", file_path, False)
            return False

    def _escape_html(self, text):
        """Escape HTML special characters"""
        import html
        return html.escape(text)

    def get_recent_files(self):
        """Get list of recent files"""
        recent_files = self.editor.config.get('recent_files', [])
        # Filter out non-existent files
        valid_files = [f for f in recent_files if os.path.exists(f)]

        # Update config if we filtered any files
        if len(valid_files) != len(recent_files):
            self.editor.config.set('recent_files', valid_files)

        return valid_files

    def clear_recent_files(self):
        """Clear recent files list"""
        self.editor.config.clear_recent_files()

    def show_file_properties(self):
        """Show file properties dialog"""
        if not self.editor.current_file:
            messagebox.showwarning("Warning", "No file is currently open")
            return

        stats = self.get_file_stats()
        if not stats:
            messagebox.showerror("Error", "Could not retrieve file properties")
            return

        # Get text statistics
        content = self.editor.text_widget.get('1.0', 'end-1c')
        lines = int(self.editor.text_widget.index('end-1c').split('.')[0])
        words = len(content.split()) if content.strip() else 0
        chars = len(content)

        properties_text = f"""File Properties:

Path: {self.editor.current_file}
Size: {stats['size']:,} bytes
Lines: {lines:,}
Words: {words:,}
Characters: {chars:,}

Created: {stats['created'].strftime('%Y-%m-%d %H:%M:%S')}
Modified: {stats['modified'].strftime('%Y-%m-%d %H:%M:%S')}

Permissions:
  Readable: {'Yes' if stats['readable'] else 'No'}
  Writable: {'Yes' if stats['writable'] else 'No'}
  Executable: {'Yes' if stats['executable'] else 'No'}
"""

        # Create properties window
        props_window = tk.Toplevel(self.editor.window)
        props_window.title("File Properties")
        props_window.geometry("400x300")
        props_window.resizable(False, False)

        text_widget = tk.Text(props_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', properties_text)
        text_widget.config(state='disabled')

        # Add close button
        close_button = tk.Button(
            props_window,
            text="Close",
            command=props_window.destroy
        )
        close_button.pack(pady=10)
