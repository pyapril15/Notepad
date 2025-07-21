"""
Spell Checker - Provides spell checking functionality
"""

import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Try to import spellchecker, fall back to basic implementation
try:
    from spellchecker import SpellChecker as PySpellChecker

    SPELLCHECKER_AVAILABLE = True
except ImportError:
    SPELLCHECKER_AVAILABLE = False
    PySpellChecker = None


class SpellChecker:
    """Spell checking functionality for the text editor"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.enabled = SPELLCHECKER_AVAILABLE
        self.language = 'en'

        # Initialize spell checker
        if SPELLCHECKER_AVAILABLE:
            self.spell = PySpellChecker(language=self.language)
        else:
            self.spell = None

        # Custom word lists
        self.custom_words = set()
        self.ignored_words = set()

        # Spell check state
        self.is_checking = False
        self.misspelled_words = {}  # position -> word
        self.current_check_position = "1.0"

        # UI elements
        self.check_dialog = None
        self.suggestion_dialog = None

        # Setup highlighting
        self._setup_tags()

        # Load custom dictionary
        self._load_custom_dictionary()

        # Bind events for real-time spell checking
        if self.enabled:
            self.text_widget.bind('<KeyRelease>', self._on_text_change)
            self.text_widget.bind('<Button-3>', self._on_right_click)

    def _setup_tags(self):
        """Setup text widget tags for spell checking"""
        self.text_widget.tag_configure(
            "misspelled",
            underline=True,
            underlinefg="red"
        )

        self.text_widget.tag_configure(
            "spell_current",
            background="#ffcccc"
        )

    def _load_custom_dictionary(self):
        """Load custom words from file"""
        try:
            from pathlib import Path
            dict_file = Path.home() / '.modern_notepad' / 'custom_dict.txt'

            if dict_file.exists():
                with open(dict_file, 'r', encoding='utf-8') as f:
                    self.custom_words = set(word.strip().lower() for word in f.readlines())
        except Exception as e:
            print(f"Error loading custom dictionary: {e}")

    def _save_custom_dictionary(self):
        """Save custom words to file"""
        try:
            from pathlib import Path
            dict_dir = Path.home() / '.modern_notepad'
            dict_dir.mkdir(exist_ok=True)
            dict_file = dict_dir / 'custom_dict.txt'

            with open(dict_file, 'w', encoding='utf-8') as f:
                for word in sorted(self.custom_words):
                    f.write(f"{word}\n")
        except Exception as e:
            print(f"Error saving custom dictionary: {e}")

    def is_word_correct(self, word):
        """Check if a word is spelled correctly"""
        if not self.enabled or not self.spell:
            return True

        word_lower = word.lower()

        # Check if word is in ignored list
        if word_lower in self.ignored_words:
            return True

        # Check if word is in custom dictionary
        if word_lower in self.custom_words:
            return True

        # Check with spell checker
        return word_lower in self.spell

    def get_suggestions(self, word):
        """Get spelling suggestions for a word"""
        if not self.enabled or not self.spell:
            return []

        suggestions = list(self.spell.candidates(word.lower()))
        return suggestions[:10]  # Return top 10 suggestions

    def add_to_dictionary(self, word):
        """Add word to custom dictionary"""
        self.custom_words.add(word.lower())
        self._save_custom_dictionary()

        # Remove misspelling highlight
        self._remove_misspelling_highlight(word)

    def ignore_word(self, word):
        """Ignore word for this session"""
        self.ignored_words.add(word.lower())

        # Remove misspelling highlight
        self._remove_misspelling_highlight(word)

    def check_spelling(self):
        """Run interactive spell check"""
        if not self.enabled:
            messagebox.showinfo(
                "Spell Check",
                "Spell checking is not available. Please install the 'pyspellchecker' package."
            )
            return

        if self.is_checking:
            return

        # Start spell check from beginning
        self.current_check_position = "1.0"
        self._find_next_misspelled_word()

    def check_spelling_background(self):
        """Run background spell check (non-interactive)"""
        if not self.enabled or self.is_checking:
            return

        # Run in background thread
        thread = threading.Thread(target=self._background_spell_check)
        thread.daemon = True
        thread.start()

    def _background_spell_check(self):
        """Background spell checking worker"""
        self.is_checking = True

        try:
            # Clear previous highlights
            self.text_widget.after_idle(self._clear_misspelling_highlights)

            # Get all text
            content = self.text_widget.get('1.0', 'end-1c')

            # Find all words
            words = self._extract_words(content)

            # Check each word
            for word_info in words:
                word, start_pos, end_pos = word_info

                if not self.is_word_correct(word):
                    # Schedule highlighting in main thread
                    self.text_widget.after_idle(
                        self._highlight_misspelled_word, start_pos, end_pos, word
                    )

        except Exception as e:
            print(f"Error in background spell check: {e}")
        finally:
            self.is_checking = False

    def _extract_words(self, content):
        """Extract words and their positions from content"""
        words = []

        # Pattern to match words (letters, numbers, apostrophes)
        word_pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b"

        for match in re.finditer(word_pattern, content):
            word = match.group()
            start = match.start()
            end = match.end()

            # Convert to text widget indices
            start_pos = self._char_to_text_index(content, start)
            end_pos = self._char_to_text_index(content, end)

            words.append((word, start_pos, end_pos))

        return words

    def _char_to_text_index(self, content, char_pos):
        """Convert character position to text widget index"""
        lines_before = content[:char_pos].count('\n')
        line_start = content.rfind('\n', 0, char_pos)
        col = char_pos - line_start - 1 if line_start != -1 else char_pos
        return f"{lines_before + 1}.{col}"

    def _highlight_misspelled_word(self, start_pos, end_pos, word):
        """Highlight a misspelled word"""
        try:
            self.text_widget.tag_add("misspelled", start_pos, end_pos)
            self.misspelled_words[start_pos] = word
        except tk.TclError:
            pass  # Position may be invalid

    def _clear_misspelling_highlights(self):
        """Clear all misspelling highlights"""
        self.text_widget.tag_remove("misspelled", "1.0", "end")
        self.text_widget.tag_remove("spell_current", "1.0", "end")
        self.misspelled_words.clear()

    def _remove_misspelling_highlight(self, word):
        """Remove highlighting for a specific word"""
        positions_to_remove = []

        for pos, highlighted_word in self.misspelled_words.items():
            if highlighted_word.lower() == word.lower():
                try:
                    # Find the end position
                    end_pos = f"{pos}+{len(highlighted_word)}c"
                    self.text_widget.tag_remove("misspelled", pos, end_pos)
                    positions_to_remove.append(pos)
                except tk.TclError:
                    positions_to_remove.append(pos)

        # Remove from tracking
        for pos in positions_to_remove:
            del self.misspelled_words[pos]

    def _find_next_misspelled_word(self):
        """Find next misspelled word for interactive checking"""
        if not self.enabled:
            return

        # Get text from current position to end
        try:
            remaining_text = self.text_widget.get(self.current_check_position, 'end-1c')
        except tk.TclError:
            self._spell_check_complete()
            return

        if not remaining_text.strip():
            self._spell_check_complete()
            return

        # Find next word
        word_pattern = r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b"
        match = re.search(word_pattern, remaining_text)

        if not match:
            self._spell_check_complete()
            return

        word = match.group()
        start_offset = match.start()
        end_offset = match.end()

        # Calculate absolute positions
        start_pos = f"{self.current_check_position}+{start_offset}c"
        end_pos = f"{self.current_check_position}+{end_offset}c"

        # Check if word is misspelled
        if not self.is_word_correct(word):
            self._show_spell_check_dialog(word, start_pos, end_pos)
        else:
            # Move to next word
            self.current_check_position = f"{end_pos}+1c"
            self._find_next_misspelled_word()

    def _show_spell_check_dialog(self, word, start_pos, end_pos):
        """Show spell check dialog for a misspelled word"""
        if self.check_dialog and self.check_dialog.winfo_exists():
            self.check_dialog.destroy()

        # Highlight current word
        self.text_widget.tag_remove("spell_current", "1.0", "end")
        self.text_widget.tag_add("spell_current", start_pos, end_pos)
        self.text_widget.see(start_pos)

        # Create dialog
        self.check_dialog = tk.Toplevel(self.text_widget.master)
        self.check_dialog.title("Spell Check")
        self.check_dialog.geometry("400x300")
        self.check_dialog.resizable(False, False)
        self.check_dialog.transient(self.text_widget.master)

        # Main frame
        main_frame = ttk.Frame(self.check_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Misspelled word info
        ttk.Label(main_frame, text=f"Not in dictionary:").pack(anchor=tk.W)
        word_label = ttk.Label(main_frame, text=word, font=("", 12, "bold"))
        word_label.pack(anchor=tk.W, pady=(0, 10))

        # Suggestions
        ttk.Label(main_frame, text="Suggestions:").pack(anchor=tk.W)

        suggestions_frame = ttk.Frame(main_frame)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Suggestions listbox
        self.suggestions_var = tk.StringVar()
        suggestions_listbox = tk.Listbox(
            suggestions_frame,
            listvariable=self.suggestions_var,
            height=8
        )
        suggestions_listbox.pack(fill=tk.BOTH, expand=True)

        # Get and display suggestions
        suggestions = self.get_suggestions(word)
        if suggestions:
            suggestions_listbox.delete(0, tk.END)
            for suggestion in suggestions:
                suggestions_listbox.insert(tk.END, suggestion)
            suggestions_listbox.selection_set(0)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # Action buttons
        ttk.Button(
            buttons_frame,
            text="Replace",
            command=lambda: self._replace_word(word, start_pos, end_pos, suggestions_listbox)
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="Ignore",
            command=lambda: self._ignore_word_dialog(word)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Add to Dictionary",
            command=lambda: self._add_word_dialog(word)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._cancel_spell_check
        ).pack(side=tk.RIGHT)

        # Bind events
        suggestions_listbox.bind('<Double-Button-1>',
                                 lambda e: self._replace_word(word, start_pos, end_pos, suggestions_listbox))

        self.check_dialog.bind('<Escape>', lambda e: self._cancel_spell_check())

        # Focus on dialog
        self.check_dialog.focus_set()

    def _replace_word(self, original_word, start_pos, end_pos, suggestions_listbox):
        """Replace misspelled word with selected suggestion"""
        try:
            selection = suggestions_listbox.curselection()
            if selection:
                replacement = suggestions_listbox.get(selection[0])

                # Replace the word
                self.text_widget.delete(start_pos, end_pos)
                self.text_widget.insert(start_pos, replacement)

                # Update check position
                new_end_pos = f"{start_pos}+{len(replacement)}c"
                self.current_check_position = f"{new_end_pos}+1c"
        except (tk.TclError, IndexError):
            pass

        # Close dialog and continue
        self._close_spell_check_dialog()
        self._find_next_misspelled_word()

    def _ignore_word_dialog(self, word):
        """Ignore word and continue spell check"""
        self.ignore_word(word)

        # Move past this word
        try:
            end_pos = f"{self.current_check_position}+{len(word)}c"
            self.current_check_position = f"{end_pos}+1c"
        except tk.TclError:
            pass

        # Close dialog and continue
        self._close_spell_check_dialog()
        self._find_next_misspelled_word()

    def _add_word_dialog(self, word):
        """Add word to dictionary and continue spell check"""
        self.add_to_dictionary(word)

        # Move past this word
        try:
            end_pos = f"{self.current_check_position}+{len(word)}c"
            self.current_check_position = f"{end_pos}+1c"
        except tk.TclError:
            pass

        # Close dialog and continue
        self._close_spell_check_dialog()
        self._find_next_misspelled_word()

    def _cancel_spell_check(self):
        """Cancel spell check"""
        self._close_spell_check_dialog()
        self.text_widget.tag_remove("spell_current", "1.0", "end")

    def _close_spell_check_dialog(self):
        """Close spell check dialog"""
        if self.check_dialog:
            self.check_dialog.destroy()
            self.check_dialog = None

    def _spell_check_complete(self):
        """Spell check completed"""
        self.text_widget.tag_remove("spell_current", "1.0", "end")
        messagebox.showinfo("Spell Check", "Spell check complete!")

    def _on_text_change(self, event=None):
        """Handle text changes for real-time spell checking"""
        if not self.enabled:
            return

        # Debounce spell checking
        if hasattr(self, '_spell_check_timer'):
            self.text_widget.after_cancel(self._spell_check_timer)

        self._spell_check_timer = self.text_widget.after(1000, self.check_spelling_background)

    def _on_right_click(self, event):
        """Handle right-click for spell check context menu"""
        if not self.enabled:
            return

        # Get clicked position
        click_pos = self.text_widget.index(f"@{event.x},{event.y}")

        # Check if click is on a misspelled word
        tags = self.text_widget.tag_names(click_pos)
        if "misspelled" in tags:
            self._show_context_menu(event, click_pos)

    def _show_context_menu(self, event, position):
        """Show context menu for misspelled word"""
        # Find the misspelled word at this position
        word = None
        start_pos = None
        end_pos = None

        for pos, misspelled_word in self.misspelled_words.items():
            word_end = f"{pos}+{len(misspelled_word)}c"
            if (self.text_widget.compare(pos, "<=", position) and
                    self.text_widget.compare(position, "<", word_end)):
                word = misspelled_word
                start_pos = pos
                end_pos = word_end
                break

        if not word:
            return

        # Create context menu
        context_menu = tk.Menu(self.text_widget, tearoff=0)

        # Add suggestions
        suggestions = self.get_suggestions(word)
        if suggestions:
            for suggestion in suggestions[:5]:  # Show top 5
                context_menu.add_command(
                    label=suggestion,
                    command=lambda s=suggestion: self._replace_word_context(
                        word, start_pos, end_pos, s
                    )
                )
            context_menu.add_separator()

        # Add other options
        context_menu.add_command(
            label="Ignore",
            command=lambda: self.ignore_word(word)
        )
        context_menu.add_command(
            label="Add to Dictionary",
            command=lambda: self.add_to_dictionary(word)
        )

        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _replace_word_context(self, original_word, start_pos, end_pos, replacement):
        """Replace word from context menu"""
        try:
            self.text_widget.delete(start_pos, end_pos)
            self.text_widget.insert(start_pos, replacement)

            # Remove from misspelled words
            if start_pos in self.misspelled_words:
                del self.misspelled_words[start_pos]
        except tk.TclError:
            pass

    def set_language(self, language_code):
        """Set spell check language"""
        if not SPELLCHECKER_AVAILABLE:
            return False

        try:
            self.spell = PySpellChecker(language=language_code)
            self.language = language_code

            # Re-run spell check with new language
            if self.enabled:
                self.check_spelling_background()

            return True
        except Exception as e:
            print(f"Error setting language {language_code}: {e}")
            return False

    def get_available_languages(self):
        """Get list of available spell check languages"""
        if not SPELLCHECKER_AVAILABLE:
            return []

        # This would need to be implemented based on the spell checker library
        return ['en', 'es', 'fr', 'de', 'it', 'pt']

    def toggle_spell_check(self):
        """Toggle spell checking on/off"""
        if not SPELLCHECKER_AVAILABLE:
            return False

        self.enabled = not self.enabled

        if self.enabled:
            self.check_spelling_background()
        else:
            self._clear_misspelling_highlights()

        return self.enabled

    def get_statistics(self):
        """Get spell check statistics"""
        if not self.enabled:
            return None

        # Get document text
        content = self.text_widget.get('1.0', 'end-1c')
        words = self._extract_words(content)

        total_words = len(words)
        misspelled_count = len(self.misspelled_words)

        return {
            'total_words': total_words,
            'misspelled_words': misspelled_count,
            'accuracy': ((total_words - misspelled_count) / total_words * 100) if total_words > 0 else 100
        }
