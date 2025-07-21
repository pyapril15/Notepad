"""
Search and Replace - Advanced search and replace functionality
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class SearchReplace:
    """Advanced search and replace functionality"""

    def __init__(self, editor):
        self.editor = editor
        self.text_widget = editor.text_widget

        # Search state
        self.last_search = ""
        self.last_replace = ""
        self.current_matches = []
        self.current_match_index = -1
        self.search_start_pos = "1.0"

        # Search options
        self.case_sensitive = tk.BooleanVar(value=False)
        self.whole_words = tk.BooleanVar(value=False)
        self.use_regex = tk.BooleanVar(value=False)
        self.wrap_around = tk.BooleanVar(value=True)

        # Dialog windows
        self.find_dialog = None
        self.replace_dialog = None
        self.goto_dialog = None

        # Highlight tags
        self._setup_highlight_tags()

    def _setup_highlight_tags(self):
        """Setup text widget tags for highlighting search results"""
        self.text_widget.tag_configure(
            "search_highlight",
            background="#ffff00",
            foreground="#000000"
        )
        self.text_widget.tag_configure(
            "current_match",
            background="#ff6600",
            foreground="#ffffff"
        )

    def show_find_dialog(self):
        """Show find dialog"""
        if self.find_dialog and self.find_dialog.winfo_exists():
            self.find_dialog.lift()
            self.find_dialog.focus_set()
            return

        self.find_dialog = tk.Toplevel(self.editor.window)
        self.find_dialog.title("Find")
        self.find_dialog.geometry("400x200")
        self.find_dialog.resizable(False, False)
        self.find_dialog.transient(self.editor.window)

        # Main frame
        main_frame = ttk.Frame(self.find_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search term
        ttk.Label(main_frame, text="Find what:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.find_var = tk.StringVar(value=self.last_search)
        find_entry = ttk.Entry(main_frame, textvariable=self.find_var, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        find_entry.focus_set()

        # Get selected text if any
        try:
            selected_text = self.text_widget.get('sel.first', 'sel.last')
            if selected_text and '\n' not in selected_text:
                self.find_var.set(selected_text)
        except tk.TclError:
            pass

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Whole words only", variable=self.whole_words).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Regular expressions", variable=self.use_regex).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Wrap around", variable=self.wrap_around).pack(anchor=tk.W)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(buttons_frame, text="Find Next", command=self._find_next_from_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Find Previous", command=self._find_previous_from_dialog).pack(side=tk.LEFT,
                                                                                                      padx=2)
        ttk.Button(buttons_frame, text="Find All", command=self._find_all_from_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Close", command=self._close_find_dialog).pack(side=tk.LEFT, padx=2)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Bind events
        find_entry.bind('<Return>', lambda e: self._find_next_from_dialog())
        find_entry.bind('<Escape>', lambda e: self._close_find_dialog())
        self.find_dialog.bind('<Escape>', lambda e: self._close_find_dialog())

        # Select all text in entry
        find_entry.select_range(0, tk.END)

    def show_replace_dialog(self):
        """Show replace dialog"""
        if self.replace_dialog and self.replace_dialog.winfo_exists():
            self.replace_dialog.lift()
            self.replace_dialog.focus_set()
            return

        self.replace_dialog = tk.Toplevel(self.editor.window)
        self.replace_dialog.title("Replace")
        self.replace_dialog.geometry("450x250")
        self.replace_dialog.resizable(False, False)
        self.replace_dialog.transient(self.editor.window)

        # Main frame
        main_frame = ttk.Frame(self.replace_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Find term
        ttk.Label(main_frame, text="Find what:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.replace_find_var = tk.StringVar(value=self.last_search)
        find_entry = ttk.Entry(main_frame, textvariable=self.replace_find_var, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        find_entry.focus_set()

        # Replace term
        ttk.Label(main_frame, text="Replace with:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.replace_with_var = tk.StringVar(value=self.last_replace)
        replace_entry = ttk.Entry(main_frame, textvariable=self.replace_with_var, width=30)
        replace_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=2)

        # Get selected text if any
        try:
            selected_text = self.text_widget.get('sel.first', 'sel.last')
            if selected_text and '\n' not in selected_text:
                self.replace_find_var.set(selected_text)
        except tk.TclError:
            pass

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Checkbutton(options_frame, text="Case sensitive", variable=self.case_sensitive).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Whole words only", variable=self.whole_words).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Regular expressions", variable=self.use_regex).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Wrap around", variable=self.wrap_around).pack(anchor=tk.W)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)

        ttk.Button(buttons_frame, text="Find Next", command=self._find_next_from_replace_dialog).pack(side=tk.LEFT,
                                                                                                      padx=2)
        ttk.Button(buttons_frame, text="Replace", command=self._replace_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Replace All", command=self._replace_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Close", command=self._close_replace_dialog).pack(side=tk.LEFT, padx=2)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Bind events
        find_entry.bind('<Return>', lambda e: self._find_next_from_replace_dialog())
        replace_entry.bind('<Return>', lambda e: self._replace_current())
        self.replace_dialog.bind('<Escape>', lambda e: self._close_replace_dialog())

        # Select all text in entry
        find_entry.select_range(0, tk.END)

    def show_goto_line_dialog(self):
        """Show go to line dialog"""
        total_lines = int(self.text_widget.index('end-1c').split('.')[0])
        current_line = int(self.text_widget.index(tk.INSERT).split('.')[0])

        line_number = simpledialog.askinteger(
            "Go to Line",
            f"Line number (1-{total_lines}):",
            initialvalue=current_line,
            minvalue=1,
            maxvalue=total_lines
        )

        if line_number:
            self.goto_line(line_number)

    def goto_line(self, line_number):
        """Go to specific line number"""
        try:
            # Move cursor to the beginning of the line
            pos = f"{line_number}.0"
            self.text_widget.mark_set(tk.INSERT, pos)
            self.text_widget.see(pos)

            # Select the entire line
            line_start = f"{line_number}.0"
            line_end = f"{line_number}.end"
            self.text_widget.tag_remove('sel', '1.0', 'end')
            self.text_widget.tag_add('sel', line_start, line_end)

            self.editor.app.logger.log_user_action(f"Go to line {line_number}")

        except tk.TclError as e:
            messagebox.showerror("Error", f"Invalid line number: {line_number}")

    def find_next(self, search_term=None):
        """Find next occurrence"""
        if search_term is None:
            search_term = self.last_search

        if not search_term:
            self.show_find_dialog()
            return False

        return self._search_forward(search_term)

    def find_previous(self, search_term=None):
        """Find previous occurrence"""
        if search_term is None:
            search_term = self.last_search

        if not search_term:
            self.show_find_dialog()
            return False

        return self._search_backward(search_term)

    def find_all(self, search_term=None):
        """Find all occurrences and highlight them"""
        if search_term is None:
            search_term = self.last_search

        if not search_term:
            return []

        # Clear previous highlights
        self._clear_highlights()

        # Find all matches
        matches = self._find_all_matches(search_term)

        # Highlight all matches
        for start, end in matches:
            self.text_widget.tag_add("search_highlight", start, end)

        if matches:
            # Show first match
            self.text_widget.see(matches[0][0])
            self.text_widget.mark_set(tk.INSERT, matches[0][0])

            # Show status
            messagebox.showinfo("Find All", f"Found {len(matches)} occurrences")
        else:
            messagebox.showinfo("Find All", "No matches found")

        return matches

    def _search_forward(self, search_term):
        """Search forward from current position"""
        self.last_search = search_term

        # Get current cursor position
        start_pos = self.text_widget.index(tk.INSERT)

        # If there's a selection, start after it
        try:
            sel_end = self.text_widget.index('sel.last')
            if sel_end:
                start_pos = sel_end
        except tk.TclError:
            pass

        # Find next match
        match_pos = self._find_next_match(search_term, start_pos)

        if match_pos:
            self._select_match(match_pos)
            return True
        elif self.wrap_around.get():
            # Try from beginning
            match_pos = self._find_next_match(search_term, "1.0")
            if match_pos and self.text_widget.compare(match_pos[0], "<", start_pos):
                self._select_match(match_pos)
                return True

        messagebox.showinfo("Find", f"'{search_term}' not found")
        return False

    def _search_backward(self, search_term):
        """Search backward from current position"""
        self.last_search = search_term

        # Get current cursor position
        start_pos = self.text_widget.index(tk.INSERT)

        # If there's a selection, start before it
        try:
            sel_start = self.text_widget.index('sel.first')
            if sel_start:
                start_pos = sel_start
        except tk.TclError:
            pass

        # Find all matches up to current position
        all_matches = self._find_all_matches(search_term)

        # Filter matches before current position
        previous_matches = [
            match for match in all_matches
            if self.text_widget.compare(match[0], "<", start_pos)
        ]

        if previous_matches:
            # Select the last match before current position
            match_pos = previous_matches[-1]
            self._select_match(match_pos)
            return True
        elif self.wrap_around.get() and all_matches:
            # Wrap to last match in document
            match_pos = all_matches[-1]
            if self.text_widget.compare(match_pos[0], ">", start_pos):
                self._select_match(match_pos)
                return True

        messagebox.showinfo("Find", f"'{search_term}' not found")
        return False

    def _find_next_match(self, search_term, start_pos):
        """Find next match from given position"""
        try:
            if self.use_regex.get():
                return self._regex_search(search_term, start_pos)
            else:
                return self._text_search(search_term, start_pos)
        except re.error as e:
            messagebox.showerror("Regular Expression Error", f"Invalid regex: {e}")
            return None

    def _text_search(self, search_term, start_pos):
        """Perform text search"""
        flags = []
        if not self.case_sensitive.get():
            flags.append('nocase')

        # Use tkinter's built-in search
        pos = self.text_widget.search(
            search_term,
            start_pos,
            stopindex='end',
            *flags
        )

        if pos:
            end_pos = f"{pos}+{len(search_term)}c"

            # Check for whole words if needed
            if self.whole_words.get():
                if not self._is_whole_word(pos, end_pos):
                    # Continue searching from after this match
                    next_pos = f"{pos}+1c"
                    return self._find_next_match(search_term, next_pos)

            return (pos, end_pos)

        return None

    def _regex_search(self, pattern, start_pos):
        """Perform regex search"""
        try:
            flags = 0
            if not self.case_sensitive.get():
                flags |= re.IGNORECASE

            compiled_pattern = re.compile(pattern, flags)

            # Get text from start position to end
            text = self.text_widget.get(start_pos, 'end')

            match = compiled_pattern.search(text)
            if match:
                # Calculate absolute positions
                start_line, start_col = map(int, start_pos.split('.'))
                match_start = match.start()
                match_end = match.end()

                # Convert to text widget indices
                lines_before = text[:match_start].count('\n')
                if lines_before == 0:
                    abs_start = f"{start_line}.{start_col + match_start}"
                    abs_end = f"{start_line}.{start_col + match_end}"
                else:
                    last_newline = text.rfind('\n', 0, match_start)
                    col_start = match_start - last_newline - 1
                    abs_start = f"{start_line + lines_before}.{col_start}"

                    lines_in_match = text[match_start:match_end].count('\n')
                    if lines_in_match == 0:
                        abs_end = f"{start_line + lines_before}.{col_start + match_end - match_start}"
                    else:
                        last_newline_in_match = text.rfind('\n', match_start, match_end)
                        col_end = match_end - last_newline_in_match - 1
                        abs_end = f"{start_line + lines_before + lines_in_match}.{col_end}"

                return (abs_start, abs_end)

        except re.error:
            raise

        return None

    def _find_all_matches(self, search_term):
        """Find all matches in the document"""
        matches = []
        start_pos = "1.0"

        while True:
            match_pos = self._find_next_match(search_term, start_pos)
            if not match_pos:
                break

            matches.append(match_pos)
            start_pos = f"{match_pos[1]}"

            # Prevent infinite loop
            if self.text_widget.compare(start_pos, ">=", "end"):
                break

        return matches

    def _is_whole_word(self, start_pos, end_pos):
        """Check if match is a whole word"""
        # Check character before start
        try:
            before_pos = f"{start_pos}-1c"
            char_before = self.text_widget.get(before_pos, start_pos)
            if char_before.isalnum() or char_before == '_':
                return False
        except tk.TclError:
            pass  # Beginning of text

        # Check character after end
        try:
            char_after = self.text_widget.get(end_pos, f"{end_pos}+1c")
            if char_after.isalnum() or char_after == '_':
                return False
        except tk.TclError:
            pass  # End of text

        return True

    def _select_match(self, match_pos):
        """Select and show a match"""
        start, end = match_pos

        # Clear previous selection and highlights
        self.text_widget.tag_remove('sel', '1.0', 'end')
        self._clear_highlights()

        # Select the match
        self.text_widget.tag_add('sel', start, end)
        self.text_widget.tag_add('current_match', start, end)

        # Move cursor and ensure visibility
        self.text_widget.mark_set(tk.INSERT, start)
        self.text_widget.see(start)

    def _clear_highlights(self):
        """Clear all search highlights"""
        self.text_widget.tag_remove('search_highlight', '1.0', 'end')
        self.text_widget.tag_remove('current_match', '1.0', 'end')

    def _replace_current(self):
        """Replace current selection"""
        try:
            # Check if there's a selection
            sel_start = self.text_widget.index('sel.first')
            sel_end = self.text_widget.index('sel.last')

            # Get the replacement text
            replace_text = self.replace_with_var.get()

            # Replace the selection
            self.text_widget.delete(sel_start, sel_end)
            self.text_widget.insert(sel_start, replace_text)

            # Mark as modified
            self.editor.set_modified(True)

            # Find next occurrence
            self._find_next_from_replace_dialog()

        except tk.TclError:
            messagebox.showwarning("Replace", "No text selected for replacement")

    def _replace_all(self):
        """Replace all occurrences"""
        find_text = self.replace_find_var.get()
        replace_text = self.replace_with_var.get()

        if not find_text:
            messagebox.showwarning("Replace All", "No search term specified")
            return

        # Find all matches
        matches = self._find_all_matches(find_text)

        if not matches:
            messagebox.showinfo("Replace All", "No matches found")
            return

        # Confirm replacement
        result = messagebox.askyesno(
            "Replace All",
            f"Replace {len(matches)} occurrences of '{find_text}' with '{replace_text}'?"
        )

        if not result:
            return

        # Replace all matches (in reverse order to maintain positions)
        self.text_widget.mark_set(tk.INSERT, "1.0")

        for start, end in reversed(matches):
            self.text_widget.delete(start, end)
            self.text_widget.insert(start, replace_text)

        # Mark as modified
        self.editor.set_modified(True)

        # Clear highlights
        self._clear_highlights()

        messagebox.showinfo("Replace All", f"Replaced {len(matches)} occurrences")

    # Dialog event handlers
    def _find_next_from_dialog(self):
        """Find next from find dialog"""
        search_term = self.find_var.get()
        if search_term:
            self.find_next(search_term)

    def _find_previous_from_dialog(self):
        """Find previous from find dialog"""
        search_term = self.find_var.get()
        if search_term:
            self.find_previous(search_term)

    def _find_all_from_dialog(self):
        """Find all from find dialog"""
        search_term = self.find_var.get()
        if search_term:
            self.find_all(search_term)

    def _find_next_from_replace_dialog(self):
        """Find next from replace dialog"""
        search_term = self.replace_find_var.get()
        if search_term:
            self.find_next(search_term)

    def _close_find_dialog(self):
        """Close find dialog"""
        if self.find_dialog:
            self._clear_highlights()
            self.find_dialog.destroy()
            self.find_dialog = None

    def _close_replace_dialog(self):
        """Close replace dialog"""
        if self.replace_dialog:
            self.last_replace = self.replace_with_var.get()
            self._clear_highlights()
            self.replace_dialog.destroy()
            self.replace_dialog = None

    def incremental_search(self, search_term):
        """Incremental search as user types"""
        if not search_term:
            self._clear_highlights()
            return

        # Find and highlight all matches
        matches = self._find_all_matches(search_term)

        # Clear previous highlights
        self._clear_highlights()

        # Highlight all matches
        for start, end in matches:
            self.text_widget.tag_add("search_highlight", start, end)

        # Show first match
        if matches:
            self.text_widget.see(matches[0][0])

    def quick_find(self):
        """Quick find using selected text or word under cursor"""
        try:
            # Try to get selected text
            search_term = self.text_widget.get('sel.first', 'sel.last')
        except tk.TclError:
            # No selection, get word under cursor
            cursor_pos = self.text_widget.index(tk.INSERT)

            # Find word boundaries
            word_start = cursor_pos
            word_end = cursor_pos

            # Find start of word
            while True:
                char_pos = f"{word_start}-1c"
                if self.text_widget.compare(char_pos, "<", "1.0"):
                    break
                char = self.text_widget.get(char_pos, word_start)
                if not (char.isalnum() or char == '_'):
                    break
                word_start = char_pos

            # Find end of word
            while True:
                char_pos = f"{word_end}+1c"
                if self.text_widget.compare(char_pos, ">", "end"):
                    break
                char = self.text_widget.get(word_end, char_pos)
                if not (char.isalnum() or char == '_'):
                    break
                word_end = char_pos

            search_term = self.text_widget.get(word_start, word_end)

        if search_term:
            self.find_next(search_term)
