"""
Auto-save - Automatic file saving functionality
"""

import os
import shutil
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path


class AutoSave:
    """Auto-save functionality for the editor"""

    def __init__(self, editor):
        self.editor = editor
        self.text_widget = editor.text_widget

        # Auto-save settings
        self.enabled = editor.config.get('autosave_enabled', True)
        self.interval = editor.config.get('autosave_interval', 300)  # 5 minutes default
        self.save_on_focus_lost = editor.config.get('autosave_on_focus_lost', True)
        self.create_backups = editor.config.get('autosave_create_backups', True)

        # Auto-save state
        self.is_running = False
        self.last_save_time = time.time()
        self.last_content_hash = None
        self.auto_save_thread = None
        self.stop_thread = False

        # Backup directory
        self.backup_dir = Path.home() / '.modern_notepad' / 'autosave'
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Recovery files
        self.recovery_file = None
        self.recovery_enabled = True

        # Bind events
        self._setup_events()

        # Start auto-save if enabled
        if self.enabled:
            self.start()

    def _setup_events(self):
        """Setup event bindings"""
        # Text change events
        self.text_widget.bind('<<Modified>>', self._on_text_modified)

        # Focus events
        self.editor.window.bind('<FocusOut>', self._on_focus_lost)
        self.editor.window.bind('<FocusIn>', self._on_focus_gained)

        # Window close event
        self.editor.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def start(self):
        """Start auto-save functionality"""
        if self.is_running:
            return

        self.is_running = True
        self.stop_thread = False

        # Create recovery file
        if self.recovery_enabled:
            self._create_recovery_file()

        # Start auto-save thread
        self.auto_save_thread = threading.Thread(target=self._auto_save_worker, daemon=True)
        self.auto_save_thread.start()

        self.editor.app.logger.log_user_action("Auto-save started")

    def stop(self):
        """Stop auto-save functionality"""
        if not self.is_running:
            return

        self.is_running = False
        self.stop_thread = True

        # Wait for thread to finish
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            self.auto_save_thread.join(timeout=1.0)

        # Clean up recovery file
        self._cleanup_recovery_file()

        self.editor.app.logger.log_user_action("Auto-save stopped")

    def _auto_save_worker(self):
        """Auto-save worker thread"""
        while not self.stop_thread and self.is_running:
            try:
                # Check if enough time has passed
                current_time = time.time()
                if current_time - self.last_save_time >= self.interval:
                    self._perform_auto_save()

                # Update recovery file more frequently
                if self.recovery_enabled:
                    self._update_recovery_file()

                # Sleep for a short time to avoid busy waiting
                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.editor.app.logger.log_error_with_context(
                    f"Auto-save error: {e}", "Auto-save worker thread"
                )
                time.sleep(10)  # Continue after error

    def _perform_auto_save(self):
        """Perform auto-save if needed"""
        try:
            # Check if file is modified
            if not self.editor.is_modified:
                self.last_save_time = time.time()
                return

            # Check if content has actually changed
            current_content = self.text_widget.get('1.0', 'end-1c')
            content_hash = hash(current_content)

            if content_hash == self.last_content_hash:
                self.last_save_time = time.time()
                return

            # Perform save
            if self.editor.current_file:
                # Save existing file
                success = self._save_file_safely(self.editor.current_file, current_content)
                if success:
                    self.last_content_hash = content_hash
                    self.last_save_time = time.time()

                    # Update UI in main thread
                    self.editor.window.after_idle(self._update_ui_after_save)

                    self.editor.app.logger.log_file_operation(
                        "Auto-save", self.editor.current_file, True
                    )
            else:
                # Create auto-save file for untitled document
                auto_save_file = self._create_auto_save_file(current_content)
                if auto_save_file:
                    self.last_content_hash = content_hash
                    self.last_save_time = time.time()

                    self.editor.app.logger.log_file_operation(
                        "Auto-save (untitled)", auto_save_file, True
                    )

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Auto-save failed: {e}",
                f"File: {self.editor.current_file or 'untitled'}"
            )

    def _save_file_safely(self, file_path, content):
        """Save file with atomic operation"""
        try:
            # Create backup if enabled
            if self.create_backups and os.path.exists(file_path):
                self._create_backup(file_path)

            # Use temporary file for atomic save
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(
                        mode='w',
                        encoding='utf-8',
                        delete=False,
                        dir=os.path.dirname(file_path),
                        prefix=f".{os.path.basename(file_path)}.autosave."
                ) as f:
                    f.write(content)
                    temp_file = f.name

                # Atomic move
                shutil.move(temp_file, file_path)
                return True

            except Exception as e:
                # Clean up temp file if something went wrong
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                raise e

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Safe save failed: {e}", f"File: {file_path}"
            )
            return False

    def _create_auto_save_file(self, content):
        """Create auto-save file for untitled document"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"untitled_{timestamp}.txt"
            file_path = self.backup_dir / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return str(file_path)

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Create auto-save file failed: {e}", "Untitled document"
            )
            return None

    def _create_backup(self, file_path):
        """Create backup of existing file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_name = f"{filename}.{timestamp}.autosave"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(file_path, backup_path)

            # Clean up old backups (keep last 10 for each file)
            self._cleanup_old_backups(filename)

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Create backup failed: {e}", f"File: {file_path}"
            )

    def _cleanup_old_backups(self, filename):
        """Clean up old backup files"""
        try:
            # Find all backups for this file
            backup_pattern = f"{filename}.*.autosave"
            backups = list(self.backup_dir.glob(backup_pattern))

            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove old backups (keep only 10 most recent)
            for backup in backups[10:]:
                backup.unlink()

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Cleanup backups failed: {e}", f"Pattern: {filename}.*.autosave"
            )

    def _create_recovery_file(self):
        """Create recovery file for crash recovery"""
        try:
            if self.editor.current_file:
                recovery_name = f"recovery_{os.path.basename(self.editor.current_file)}"
            else:
                recovery_name = f"recovery_untitled_{int(time.time())}.txt"

            self.recovery_file = self.backup_dir / recovery_name

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Create recovery file failed: {e}", "Recovery setup"
            )

    def _update_recovery_file(self):
        """Update recovery file with current content"""
        if not self.recovery_file:
            return

        try:
            content = self.text_widget.get('1.0', 'end-1c')

            # Only update if content has changed
            if hasattr(self, '_last_recovery_content'):
                if content == self._last_recovery_content:
                    return

            with open(self.recovery_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self._last_recovery_content = content

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Update recovery file failed: {e}",
                f"Recovery file: {self.recovery_file}"
            )

    def _cleanup_recovery_file(self):
        """Clean up recovery file"""
        if self.recovery_file and self.recovery_file.exists():
            try:
                self.recovery_file.unlink()
                self.recovery_file = None
            except Exception as e:
                self.editor.app.logger.log_error_with_context(
                    f"Cleanup recovery file failed: {e}",
                    f"Recovery file: {self.recovery_file}"
                )

    def _update_ui_after_save(self):
        """Update UI after auto-save (called in main thread)"""
        # Reset modified flag
        self.editor.set_modified(False)

        # Update status bar or show notification
        if hasattr(self.editor, 'status_bar'):
            # Could show "Auto-saved" message briefly
            pass

    def _on_text_modified(self, event=None):
        """Handle text modification"""
        # Update last modification time for auto-save timing
        self.last_save_time = time.time()

    def _on_focus_lost(self, event=None):
        """Handle focus lost event"""
        if self.save_on_focus_lost and self.enabled and self.editor.is_modified:
            # Trigger immediate save
            threading.Thread(target=self._perform_auto_save, daemon=True).start()

    def _on_focus_gained(self, event=None):
        """Handle focus gained event"""
        # Check if file was modified externally
        if self.editor.current_file and os.path.exists(self.editor.current_file):
            self._check_external_modification()

    def _check_external_modification(self):
        """Check if file was modified externally"""
        if not self.editor.current_file:
            return

        try:
            file_stat = os.stat(self.editor.current_file)
            current_mtime = file_stat.st_mtime

            if hasattr(self, '_last_file_mtime'):
                if current_mtime > self._last_file_mtime:
                    # File was modified externally
                    self._handle_external_modification()

            self._last_file_mtime = current_mtime

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Check external modification failed: {e}",
                f"File: {self.editor.current_file}"
            )

    def _handle_external_modification(self):
        """Handle external file modification"""
        if self.editor.is_modified:
            # Show dialog asking user what to do
            result = tk.messagebox.askyesnocancel(
                "File Modified",
                "The file has been modified by another program.\n"
                "Do you want to reload it? (Your changes will be lost)"
            )

            if result:  # Yes, reload
                self.editor.file_ops.reload_file()
        else:
            # No local changes, just reload
            self.editor.file_ops.reload_file()

    def _on_window_close(self):
        """Handle window close event"""
        # Perform final save if needed
        if self.enabled and self.editor.is_modified:
            self._perform_auto_save()

        # Clean up
        self.stop()

    def force_save(self):
        """Force immediate auto-save"""
        if self.enabled:
            threading.Thread(target=self._perform_auto_save, daemon=True).start()

    def set_interval(self, seconds):
        """Set auto-save interval"""
        self.interval = max(30, seconds)  # Minimum 30 seconds
        self.editor.config.set('autosave_interval', self.interval)

    def get_interval(self):
        """Get current auto-save interval"""
        return self.interval

    def set_enabled(self, enabled):
        """Enable or disable auto-save"""
        if enabled and not self.is_running:
            self.enabled = True
            self.start()
        elif not enabled and self.is_running:
            self.enabled = False
            self.stop()

        self.editor.config.set('autosave_enabled', self.enabled)

    def is_enabled(self):
        """Check if auto-save is enabled"""
        return self.enabled and self.is_running

    def get_backup_files(self):
        """Get list of backup files"""
        try:
            backup_files = []

            # Auto-save backups
            for backup_file in self.backup_dir.glob("*.autosave"):
                backup_files.append({
                    'path': str(backup_file),
                    'name': backup_file.name,
                    'modified': datetime.fromtimestamp(backup_file.stat().st_mtime),
                    'size': backup_file.stat().st_size,
                    'type': 'autosave'
                })

            # Recovery files
            for recovery_file in self.backup_dir.glob("recovery_*"):
                backup_files.append({
                    'path': str(recovery_file),
                    'name': recovery_file.name,
                    'modified': datetime.fromtimestamp(recovery_file.stat().st_mtime),
                    'size': recovery_file.stat().st_size,
                    'type': 'recovery'
                })

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x['modified'], reverse=True)

            return backup_files

        except Exception as e:
            self.editor.app.logger.log_error_with_context(
                f"Get backup files failed: {e}", "Backup directory"
            )
            return []

    def restore_from_backup(self, backup_path):
        """Restore content from backup file"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Set content in editor
            self.text_widget.delete('1.0', 'end')
            self.text_widget.insert('1.0', content)

            # Mark as modified
            self.editor.set_modified(True)

            self.editor.app.logger.log_file_operation(
                "Restore from backup", backup_path, True
            )

            return True

        except Exception as e:
            self.editor.app.logger.log_file_operation(
                "Restore from backup", backup_path, False
            )
            tk.messagebox.showerror(
                "Error",
                f"Failed to restore from backup: {e}"
            )
            return False

    def show_backup_manager(self):
        """Show backup manager window"""
        backup_window = tk.Toplevel(self.editor.window)
        backup_window.title("Backup Manager")
        backup_window.geometry("600x400")
        backup_window.transient(self.editor.window)

        # Main frame
        main_frame = tk.Frame(backup_window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Backup files list
        tk.Label(main_frame, text="Backup Files:", font=("", 12, "bold")).pack(anchor=tk.W)

        # Listbox with scrollbar
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        backup_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        backup_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=backup_listbox.yview)

        # Populate list
        backup_files = self.get_backup_files()
        for backup in backup_files:
            display_text = f"{backup['name']} - {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')} ({backup['type']})"
            backup_listbox.insert(tk.END, display_text)

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def restore_selected():
            selection = backup_listbox.curselection()
            if selection:
                backup_file = backup_files[selection[0]]
                if self.restore_from_backup(backup_file['path']):
                    backup_window.destroy()

        def delete_selected():
            selection = backup_listbox.curselection()
            if selection:
                backup_file = backup_files[selection[0]]
                if tk.messagebox.askyesno("Confirm", f"Delete backup '{backup_file['name']}'?"):
                    try:
                        os.unlink(backup_file['path'])
                        backup_listbox.delete(selection[0])
                        backup_files.pop(selection[0])
                    except Exception as e:
                        tk.messagebox.showerror("Error", f"Failed to delete backup: {e}")

        tk.Button(button_frame, text="Restore", command=restore_selected).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="Delete", command=delete_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=backup_window.destroy).pack(side=tk.RIGHT)

        # Bind double-click to restore
        backup_listbox.bind('<Double-Button-1>', lambda e: restore_selected())
