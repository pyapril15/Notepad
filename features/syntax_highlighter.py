"""
Syntax Highlighter - Provides syntax highlighting for various file types
"""

import os
import re
import threading
import tkinter as tk


class SyntaxHighlighter:
    """Syntax highlighting for text editor"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.file_type = None
        self.is_highlighting = False
        self.highlight_thread = None
        self.stop_highlighting = False

        # Language definitions
        self.languages = {
            'python': {
                'extensions': ['.py', '.pyw', '.pyx'],
                'keywords': [
                    'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
                    'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',
                    'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
                    'not', 'or', 'pass', 'print', 'raise', 'return', 'try',
                    'while', 'with', 'yield', 'True', 'False', 'None', 'self',
                    'async', 'await', 'nonlocal'
                ],
                'builtins': [
                    'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
                    'enumerate', 'eval', 'filter', 'float', 'frozenset', 'getattr',
                    'globals', 'hasattr', 'hash', 'hex', 'id', 'input', 'int',
                    'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals',
                    'map', 'max', 'min', 'next', 'object', 'oct', 'open', 'ord',
                    'pow', 'property', 'range', 'repr', 'reversed', 'round',
                    'set', 'setattr', 'slice', 'sorted', 'str', 'sum', 'super',
                    'tuple', 'type', 'vars', 'zip', '__import__'
                ],
                'patterns': {
                    'comment': r'#.*$',
                    'string': r'(""".*?"""|\'\'\'.*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
                    'number': r'\b\d+\.?\d*\b',
                    'decorator': r'@\w+',
                    'function_def': r'\bdef\s+(\w+)',
                    'class_def': r'\bclass\s+(\w+)'
                }
            },
            'javascript': {
                'extensions': ['.js', '.jsx', '.ts', '.tsx'],
                'keywords': [
                    'break', 'case', 'catch', 'class', 'const', 'continue',
                    'debugger', 'default', 'delete', 'do', 'else', 'export',
                    'extends', 'finally', 'for', 'function', 'if', 'import',
                    'in', 'instanceof', 'let', 'new', 'return', 'super',
                    'switch', 'this', 'throw', 'try', 'typeof', 'var',
                    'void', 'while', 'with', 'yield', 'async', 'await'
                ],
                'builtins': [
                    'Array', 'Boolean', 'Date', 'Error', 'Function', 'JSON',
                    'Math', 'Number', 'Object', 'RegExp', 'String', 'console',
                    'document', 'window', 'setTimeout', 'setInterval'
                ],
                'patterns': {
                    'comment': r'(//.*$|/\*.*?\*/)',
                    'string': r'(`[^`]*`|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
                    'number': r'\b\d+\.?\d*\b',
                    'regex': r'/(?:[^/\\]|\\.)+/[gimuy]*',
                    'function_def': r'\bfunction\s+(\w+)',
                    'arrow_function': r'(\w+)\s*=>\s*'
                }
            },
            'html': {
                'extensions': ['.html', '.htm', '.xhtml'],
                'keywords': [],
                'builtins': [],
                'patterns': {
                    'comment': r'<!--.*?-->',
                    'tag': r'</?[\w:]+(?:\s+[\w:]+(?:=(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?)*\s*/?>',
                    'attribute': r'\b[\w-]+(?==)',
                    'string': r'(="[^"]*"|=\'[^\']*\')',
                    'doctype': r'<!DOCTYPE[^>]*>'
                }
            },
            'css': {
                'extensions': ['.css', '.scss', '.sass', '.less'],
                'keywords': [
                    'important', 'inherit', 'initial', 'unset', 'auto', 'none',
                    'normal', 'bold', 'italic', 'underline', 'left', 'right',
                    'center', 'justify', 'top', 'bottom', 'middle'
                ],
                'builtins': [
                    'color', 'background', 'border', 'margin', 'padding',
                    'width', 'height', 'font', 'text', 'display', 'position',
                    'float', 'clear', 'overflow', 'z-index', 'opacity'
                ],
                'patterns': {
                    'comment': r'/\*.*?\*/',
                    'selector': r'[.#]?[\w-]+(?:\s*[>+~]\s*[\w-]+)*\s*(?=\{)',
                    'property': r'\b[\w-]+(?=\s*:)',
                    'value': r':\s*([^;{}]+)',
                    'string': r'(\"[^\"]*\"|\'[^\']*\')',
                    'color': r'#[0-9a-fA-F]{3,6}\b',
                    'unit': r'\b\d+(?:px|em|rem|%|vh|vw|pt|pc|in|cm|mm)\b'
                }
            },
            'json': {
                'extensions': ['.json', '.jsonl'],
                'keywords': ['true', 'false', 'null'],
                'builtins': [],
                'patterns': {
                    'string': r'"(?:[^"\\]|\\.)*"',
                    'number': r'-?\b\d+\.?\d*(?:[eE][+-]?\d+)?\b',
                    'punctuation': r'[{}\[\]:,]'
                }
            },
            'xml': {
                'extensions': ['.xml', '.xsl', '.xsd'],
                'keywords': [],
                'builtins': [],
                'patterns': {
                    'comment': r'<!--.*?-->',
                    'cdata': r'<!\[CDATA\[.*?\]\]>',
                    'tag': r'</?[\w:]+(?:\s+[\w:]+(?:=(?:"[^"]*"|\'[^\']*\'|[^\s>]+))?)*\s*/?>',
                    'attribute': r'\b[\w:-]+(?==)',
                    'string': r'(="[^"]*"|=\'[^\']*\')',
                    'declaration': r'<\?.*?\?>'
                }
            },
            'markdown': {
                'extensions': ['.md', '.markdown', '.mdown', '.mkd'],
                'keywords': [],
                'builtins': [],
                'patterns': {
                    'header': r'^#{1,6}\s.*$',
                    'bold': r'\*\*[^*]+\*\*',
                    'italic': r'\*[^*]+\*',
                    'code_block': r'```.*?```',
                    'inline_code': r'`[^`]+`',
                    'link': r'\[([^\]]+)\]\(([^)]+)\)',
                    'image': r'!\[([^\]]*)\]\(([^)]+)\)',
                    'list': r'^\s*[-*+]\s',
                    'ordered_list': r'^\s*\d+\.\s',
                    'blockquote': r'^>\s'
                }
            }
        }

        # Initialize highlighting tags
        self._setup_tags()

        # Bind events for real-time highlighting
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<<Modified>>', self._on_modified)

    def _setup_tags(self):
        """Setup text widget tags for syntax highlighting"""
        # Get theme colors (default to light theme if not available)
        try:
            import json
            theme_path = 'themes/light.json'
            if os.path.exists(theme_path):
                with open(theme_path, 'r') as f:
                    theme = json.load(f)
                colors = theme.get('syntax', {})
            else:
                colors = {}
        except:
            colors = {}

        # Default color scheme
        default_colors = {
            'keyword': '#0000ff',
            'builtin': '#800080',
            'string': '#008000',
            'comment': '#808080',
            'number': '#ff0000',
            'function': '#000080',
            'class': '#800000',
            'decorator': '#808000',
            'tag': '#800000',
            'attribute': '#ff0000',
            'property': '#000080',
            'selector': '#800000',
            'header': '#000080',
            'bold': '#000000',
            'italic': '#000000',
            'code': '#008000',
            'link': '#0000ff'
        }

        # Merge with theme colors
        for key, default_color in default_colors.items():
            color = colors.get(key, default_color)
            self.text_widget.tag_configure(f"syntax_{key}", foreground=color)

        # Special formatting
        self.text_widget.tag_configure("syntax_bold", font=("", "", "bold"))
        self.text_widget.tag_configure("syntax_italic", font=("", "", "italic"))
        self.text_widget.tag_configure("syntax_code", font=("Courier", "", ""))

    def set_file_type(self, file_path):
        """Set file type based on file extension"""
        if not file_path:
            self.file_type = None
            return

        ext = os.path.splitext(file_path)[1].lower()

        for lang_name, lang_info in self.languages.items():
            if ext in lang_info['extensions']:
                self.file_type = lang_name
                return

        # Default to text if no match
        self.file_type = 'text'

    def highlight(self, force=False):
        """Highlight the entire document"""
        if not self.file_type or self.file_type == 'text':
            return

        if self.is_highlighting and not force:
            return

        # Stop any existing highlighting thread
        self.stop_highlighting = True
        if self.highlight_thread and self.highlight_thread.is_alive():
            self.highlight_thread.join(timeout=0.1)

        # Start new highlighting thread
        self.stop_highlighting = False
        self.highlight_thread = threading.Thread(target=self._highlight_worker)
        self.highlight_thread.daemon = True
        self.highlight_thread.start()

    def _highlight_worker(self):
        """Worker thread for syntax highlighting"""
        self.is_highlighting = True

        try:
            # Get document content
            content = self.text_widget.get('1.0', 'end-1c')

            if not content.strip():
                return

            # Clear existing tags
            self._clear_syntax_tags()

            # Get language definition
            lang_def = self.languages.get(self.file_type, {})

            # Highlight based on language
            if self.file_type == 'python':
                self._highlight_python(content)
            elif self.file_type == 'javascript':
                self._highlight_javascript(content)
            elif self.file_type == 'html':
                self._highlight_html(content)
            elif self.file_type == 'css':
                self._highlight_css(content)
            elif self.file_type == 'json':
                self._highlight_json(content)
            elif self.file_type == 'xml':
                self._highlight_xml(content)
            elif self.file_type == 'markdown':
                self._highlight_markdown(content)

        except Exception as e:
            print(f"Error in syntax highlighting: {e}")
        finally:
            self.is_highlighting = False

    def _highlight_python(self, content):
        """Highlight Python syntax"""
        lang_def = self.languages['python']

        # Highlight strings first (to avoid highlighting keywords inside strings)
        self._highlight_pattern(content, lang_def['patterns']['string'], 'string')

        # Highlight comments
        self._highlight_pattern(content, lang_def['patterns']['comment'], 'comment')

        # Highlight decorators
        self._highlight_pattern(content, lang_def['patterns']['decorator'], 'decorator')

        # Highlight function definitions
        self._highlight_pattern(content, lang_def['patterns']['function_def'], 'function', group=1)

        # Highlight class definitions
        self._highlight_pattern(content, lang_def['patterns']['class_def'], 'class', group=1)

        # Highlight numbers
        self._highlight_pattern(content, lang_def['patterns']['number'], 'number')

        # Highlight keywords and builtins (avoiding strings and comments)
        self._highlight_keywords(content, lang_def['keywords'], 'keyword')
        self._highlight_keywords(content, lang_def['builtins'], 'builtin')

    def _highlight_javascript(self, content):
        """Highlight JavaScript syntax"""
        lang_def = self.languages['javascript']

        # Highlight strings
        self._highlight_pattern(content, lang_def['patterns']['string'], 'string')

        # Highlight comments
        self._highlight_pattern(content, lang_def['patterns']['comment'], 'comment')

        # Highlight regular expressions
        self._highlight_pattern(content, lang_def['patterns']['regex'], 'string')

        # Highlight function definitions
        self._highlight_pattern(content, lang_def['patterns']['function_def'], 'function', group=1)

        # Highlight numbers
        self._highlight_pattern(content, lang_def['patterns']['number'], 'number')

        # Highlight keywords and builtins
        self._highlight_keywords(content, lang_def['keywords'], 'keyword')
        self._highlight_keywords(content, lang_def['builtins'], 'builtin')

    def _highlight_html(self, content):
        """Highlight HTML syntax"""
        lang_def = self.languages['html']

        # Highlight comments
        self._highlight_pattern(content, lang_def['patterns']['comment'], 'comment')

        # Highlight DOCTYPE
        self._highlight_pattern(content, lang_def['patterns']['doctype'], 'keyword')

        # Highlight tags
        self._highlight_pattern(content, lang_def['patterns']['tag'], 'tag')

        # Highlight attributes
        self._highlight_pattern(content, lang_def['patterns']['attribute'], 'attribute')

        # Highlight string values
        self._highlight_pattern(content, lang_def['patterns']['string'], 'string')

    def _highlight_css(self, content):
        """Highlight CSS syntax"""
        lang_def = self.languages['css']

        # Highlight comments
        self._highlight_pattern(content, lang_def['patterns']['comment'], 'comment')

        # Highlight selectors
        self._highlight_pattern(content, lang_def['patterns']['selector'], 'selector')

        # Highlight properties
        self._highlight_pattern(content, lang_def['patterns']['property'], 'property')

        # Highlight colors
        self._highlight_pattern(content, lang_def['patterns']['color'], 'string')

        # Highlight units
        self._highlight_pattern(content, lang_def['patterns']['unit'], 'number')

        # Highlight string values
        self._highlight_pattern(content, lang_def['patterns']['string'], 'string')

    def _highlight_json(self, content):
        """Highlight JSON syntax"""
        lang_def = self.languages['json']

        # Highlight strings
        self._highlight_pattern(content, lang_def['patterns']['string'], 'string')

        # Highlight numbers
        self._highlight_pattern(content, lang_def['patterns']['number'], 'number')

        # Highlight keywords
        self._highlight_keywords(content, lang_def['keywords'], 'keyword')

    def _highlight_xml(self, content):
        """Highlight XML syntax"""
        lang_def = self.languages['xml']

        # Highlight comments
        self._highlight_pattern(content, lang_def['patterns']['comment'], 'comment')

        # Highlight CDATA
        self._highlight_pattern(content, lang_def['patterns']['cdata'], 'string')

        # Highlight XML declarations
        self._highlight_pattern(content, lang_def['patterns']['declaration'], 'keyword')

        # Highlight tags
        self._highlight_pattern(content, lang_def['patterns']['tag'], 'tag')

        # Highlight attributes
        self._highlight_pattern(content, lang_def['patterns']['attribute'], 'attribute')

        # Highlight string values
        self._highlight_pattern(content, lang_def['patterns']['string'], 'string')

    def _highlight_markdown(self, content):
        """Highlight Markdown syntax"""
        lang_def = self.languages['markdown']

        # Highlight headers
        self._highlight_pattern(content, lang_def['patterns']['header'], 'header')

        # Highlight code blocks
        self._highlight_pattern(content, lang_def['patterns']['code_block'], 'code')

        # Highlight inline code
        self._highlight_pattern(content, lang_def['patterns']['inline_code'], 'code')

        # Highlight bold text
        self._highlight_pattern(content, lang_def['patterns']['bold'], 'bold')

        # Highlight italic text
        self._highlight_pattern(content, lang_def['patterns']['italic'], 'italic')

        # Highlight links
        self._highlight_pattern(content, lang_def['patterns']['link'], 'link')

        # Highlight images
        self._highlight_pattern(content, lang_def['patterns']['image'], 'link')

    def _highlight_pattern(self, content, pattern, tag_name, group=0):
        """Highlight text matching a regex pattern"""
        if self.stop_highlighting:
            return

        try:
            for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                if self.stop_highlighting:
                    break

                start = match.start(group)
                end = match.end(group)

                # Convert to text widget indices
                start_pos = self._get_text_index(content, start)
                end_pos = self._get_text_index(content, end)

                # Schedule tag addition in main thread
                self.text_widget.after_idle(
                    self._add_tag_safe, f"syntax_{tag_name}", start_pos, end_pos
                )
        except re.error:
            pass  # Invalid regex

    def _highlight_keywords(self, content, keywords, tag_name):
        """Highlight keywords"""
        if self.stop_highlighting or not keywords:
            return

        # Create pattern for keywords
        keyword_pattern = r'\b(?:' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'

        self._highlight_pattern(content, keyword_pattern, tag_name)

    def _get_text_index(self, content, char_pos):
        """Convert character position to text widget index"""
        lines_before = content[:char_pos].count('\n')
        line_start = content.rfind('\n', 0, char_pos)
        col = char_pos - line_start - 1 if line_start != -1 else char_pos
        return f"{lines_before + 1}.{col}"

    def _add_tag_safe(self, tag_name, start_pos, end_pos):
        """Safely add tag in main thread"""
        try:
            self.text_widget.tag_add(tag_name, start_pos, end_pos)
        except tk.TclError:
            pass  # Position may be invalid if text was modified

    def _clear_syntax_tags(self):
        """Clear all syntax highlighting tags"""
        tag_names = [
            'syntax_keyword', 'syntax_builtin', 'syntax_string', 'syntax_comment',
            'syntax_number', 'syntax_function', 'syntax_class', 'syntax_decorator',
            'syntax_tag', 'syntax_attribute', 'syntax_property', 'syntax_selector',
            'syntax_header', 'syntax_bold', 'syntax_italic', 'syntax_code',
            'syntax_link'
        ]

        for tag_name in tag_names:
            self.text_widget.tag_remove(tag_name, '1.0', 'end')

    def _on_text_change(self, event=None):
        """Handle text changes for incremental highlighting"""
        if not self.file_type or self.file_type == 'text':
            return

        # Debounce highlighting - only highlight after user stops typing
        if hasattr(self, '_highlight_timer'):
            self.text_widget.after_cancel(self._highlight_timer)

        self._highlight_timer = self.text_widget.after(500, self._delayed_highlight)

    def _on_modified(self, event=None):
        """Handle text modification events"""
        self._on_text_change(event)

    def _delayed_highlight(self):
        """Delayed highlighting after text changes"""
        if not self.is_highlighting:
            self.highlight()

    def toggle_highlighting(self):
        """Toggle syntax highlighting on/off"""
        if self.file_type and self.file_type != 'text':
            if self.is_highlighting:
                self.stop_highlighting = True
                self._clear_syntax_tags()
            else:
                self.highlight()

    def get_supported_languages(self):
        """Get list of supported languages"""
        return list(self.languages.keys())

    def get_language_extensions(self):
        """Get dictionary of language extensions"""
        extensions = {}
        for lang, info in self.languages.items():
            extensions[lang] = info['extensions']
        return extensions

    def force_language(self, language):
        """Force a specific language for highlighting"""
        if language in self.languages:
            self.file_type = language
            self.highlight(force=True)
        else:
            self.file_type = 'text'
            self._clear_syntax_tags()

    def get_current_language(self):
        """Get current highlighting language"""
        return self.file_type
