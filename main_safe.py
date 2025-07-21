#!/usr/bin/env python3
"""
Safe Startup Version of Modern Notepad
Use this if main.py is giving "expected integer but got ''" errors

Usage: python main_safe.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class SafeNotepad:
    """Safe version of Modern Notepad with minimal features to avoid startup errors"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modern Notepad (Safe Mode)")
        self.root.geometry("800x600")

        # Initialize with safe defaults
        self.current_file = None
        self.is_modified = False

        self._create_ui()
        self._setup_events()

        print("✅ Safe Notepad started successfully!")

    def _create_ui(self):
        """Create basic UI"""
        # Create menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Text widget with scrollbars
        self.text_widget = scrolledtext.ScrolledText(
            self.root,
            undo=True,
            wrap=tk.WORD,
            font=("Consolas", 12)
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_events(self):
        """Setup event bindings"""
        # File operations
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())

        # Edit operations
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())

        # Text change events
        self.text_widget.bind('<<Modified>>', self._on_text_change)

        # Window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def new_file(self):
        """Create new file"""
        if self.is_modified:
            if not self._ask_save_changes():
                return

        self.text_widget.delete('1.0', tk.END)
        self.current_file = None
        self.is_modified = False
        self._update_title()
        self.status_bar.config(text="New file created")

    def open_file(self):
        """Open file"""
        from tkinter import filedialog

        if self.is_modified:
            if not self._ask_save_changes():
                return

        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.text_widget.delete('1.0', tk.END)
                self.text_widget.insert('1.0', content)
                self.current_file = file_path
                self.is_modified = False
                self._update_title()
                self.status_bar.config(text=f"Opened: {file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """Save file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save file as"""
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
            self._update_title()

    def _save_to_file(self, file_path):
        """Save content to file"""
        try:
            content = self.text_widget.get('1.0', 'end-1c')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.is_modified = False
            self._update_title()
            self.status_bar.config(text=f"Saved: {file_path}")
            return True

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return False

    def undo(self):
        """Undo last action"""
        try:
            self.text_widget.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        """Redo last action"""
        try:
            self.text_widget.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        """Cut selected text"""
        self.text_widget.event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text"""
        self.text_widget.event_generate("<<Copy>>")

    def paste(self):
        """Paste from clipboard"""
        self.text_widget.event_generate("<<Paste>>")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About",
            "Modern Notepad (Safe Mode)\n\n"
            "A simplified version for troubleshooting.\n"
            "If this works, the full version should work too!"
        )

    def _on_text_change(self, event=None):
        """Handle text changes"""
        if self.text_widget.edit_modified():
            self.is_modified = True
            self._update_title()
            self.text_widget.edit_modified(False)

    def _update_title(self):
        """Update window title"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
        else:
            filename = "Untitled"

        if self.is_modified:
            filename += " *"

        self.root.title(f"Modern Notepad (Safe Mode) - {filename}")

    def _ask_save_changes(self):
        """Ask user to save changes"""
        if not self.is_modified:
            return True

        result = messagebox.askyesnocancel(
            "Save Changes",
            "Do you want to save changes to the current file?"
        )

        if result is None:  # Cancel
            return False
        elif result:  # Yes
            return self.save_file()
        else:  # No
            return True

    def _on_close(self):
        """Handle window close"""
        if self._ask_save_changes():
            self.root.destroy()

    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")


def main():
    """Main entry point"""
    print("Starting Modern Notepad in Safe Mode...")
    print("This version has minimal features to avoid startup errors.")

    try:
        app = SafeNotepad()
        app.run()
    except Exception as e:
        print(f"Failed to start even safe mode: {e}")
        messagebox.showerror("Fatal Error", f"Could not start application: {e}")


if __name__ == "__main__":
    main()