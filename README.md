# Modern Notepad - Advanced Text Editor

A full-featured, modern text editor built with Python and Tkinter, designed for productivity and extensibility.

![Modern Notepad](assets/screenshot.png)

## 🚀 Features

### 📝 Core Text Editing
- **New File, Open, Save, Save As** - Complete file management
- **Undo/Redo** - Multi-level undo/redo support
- **Cut, Copy, Paste, Delete** - Standard editing operations
- **Select All** - Quick text selection
- **Find & Replace** - Advanced search with regex support
- **Go to Line** - Quick navigation to specific lines
- **Word Wrap** - Toggle word wrapping

### 🎨 Text Formatting & Appearance
- **Font Selection** - Choose from any system font
- **Text Styling** - Bold, italic, underline support
- **Color Customization** - Text and background colors
- **Zoom In/Out/Reset** - Flexible text sizing
- **Multiple Themes** - Light, Dark, and custom themes
- **Line Numbers** - Optional line number display
- **Syntax Highlighting** - Support for Python, JavaScript, HTML, CSS, JSON, XML, Markdown

### 🧠 Smart Features
- **Auto-save** - Configurable automatic saving
- **Session Restore** - Restore open files on startup
- **Spell Checking** - Real-time spell checking with suggestions
- **Code Folding** - Collapse code sections (for supported languages)
- **Smart Indentation** - Automatic indentation based on context
- **Current Line Highlighting** - Highlight the active line

### 📁 File Management
- **Multiple Tabs** - Work with multiple files simultaneously
- **Recent Files** - Quick access to recently opened files
- **Drag & Drop** - Open files by dragging them into the editor
- **File Explorer** - Built-in file browser (optional sidebar)
- **Backup Creation** - Automatic backup file generation
- **Recovery Mode** - Recover unsaved work after crashes

### 🔍 Search & Navigation
- **Incremental Search** - Search as you type
- **Find All** - Highlight all occurrences
- **Replace All** - Bulk text replacement
- **Case Sensitive Search** - Toggle case sensitivity
- **Whole Word Matching** - Match complete words only
- **Regular Expressions** - Advanced pattern matching
- **Bookmarks** - Mark important lines

### ⌨️ Accessibility & Usability
- **Keyboard Shortcuts** - Comprehensive shortcut support
- **Context Menus** - Right-click for quick actions
- **High Contrast Mode** - Accessibility-friendly display
- **Font Zoom** - Ctrl+Scroll wheel zooming
- **Full Screen Mode** - Distraction-free editing
- **Status Bar** - Real-time document statistics

### 📊 Advanced Features
- **Word Count** - Live word, character, and line counts
- **Export Options** - Export to PDF, HTML
- **Import Support** - Import from Word documents, RTF
- **Encoding Support** - Multiple text encodings (UTF-8, UTF-16, ASCII)
- **Plugin Architecture** - Extensible with custom plugins
- **Customizable Interface** - Personalize toolbars and menus

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)

### Required Dependencies

```bash
pip install -r requirements.txt
```

### Optional Dependencies

For enhanced functionality, install these optional packages:

```bash
# For spell checking
pip install pyspellchecker

# For advanced syntax highlighting
pip install pygments

# For drag-and-drop support
pip install tkinterdnd2

# For PDF export
pip install reportlab

# For Markdown preview
pip install markdown2

# For Word document import
pip install python-docx
```

### Quick Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/modern-notepad.git
   cd modern-notepad
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Creating a Standalone Executable

To create a standalone executable using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --icon=assets/icons/notepad.ico main.py

# The executable will be in the dist/ folder
```

## 📖 Usage Guide

### Getting Started

1. **Launch the Application**
   - Run `python main.py` or double-click the executable
   - The editor opens with a new untitled document

2. **Basic Operations**
   - **New File**: Ctrl+N or File → New
   - **Open File**: Ctrl+O or File → Open
   - **Save File**: Ctrl+S or File → Save
   - **Save As**: Ctrl+Shift+S or File → Save As

3. **Text Editing**
   - **Undo**: Ctrl+Z
   - **Redo**: Ctrl+Y
   - **Cut**: Ctrl+X
   - **Copy**: Ctrl+C
   - **Paste**: Ctrl+V
   - **Select All**: Ctrl+A

### Advanced Features

#### Search and Replace
- **Find**: Ctrl+F - Opens find dialog
- **Replace**: Ctrl+H - Opens replace dialog
- **Find Next**: F3
- **Find Previous**: Shift+F3
- **Go to Line**: Ctrl+G

#### View Options
- **Zoom In**: Ctrl+Plus
- **Zoom Out**: Ctrl+Minus
- **Reset Zoom**: Ctrl+0
- **Full Screen**: F11
- **Toggle Word Wrap**: View → Word Wrap

#### Themes and Appearance
- Access themes via View → Themes
- Customize fonts via Format → Font
- Adjust colors via Format → Text Color/Background Color

#### Settings and Preferences
- Open settings: Tools → Options
- Configure auto-save, themes, fonts, and more
- Export/import settings for backup

### File Formats and Syntax Highlighting

Supported file types with syntax highlighting:
- **Python**: .py, .pyw, .pyx
- **JavaScript**: .js, .jsx, .ts, .tsx
- **HTML**: .html, .htm, .xhtml
- **CSS**: .css, .scss, .sass, .less
- **JSON**: .json, .jsonl
- **XML**: .xml, .xsl, .xsd
- **Markdown**: .md, .markdown, .mdown, .mkd

### Keyboard Shortcuts

#### File Operations
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save file
- `Ctrl+Shift+S` - Save as
- `Ctrl+W` - Close file
- `Alt+F4` - Exit application

#### Edit Operations
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Del` - Delete
- `Ctrl+A` - Select all

#### Search Operations
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+G` - Go to line
- `F3` - Find next
- `Shift+F3` - Find previous

#### View Operations
- `Ctrl++` - Zoom in
- `Ctrl+-` - Zoom out
- `Ctrl+0` - Reset zoom
- `F11` - Toggle full screen

#### Other
- `F5` - Insert date/time
- `F7` - Spell check
- `F1` - Show help

## ⚙️ Configuration

### Settings File

The application stores settings in:
- **Windows**: `%USERPROFILE%\.modern_notepad\config.json`
- **macOS/Linux**: `~/.modern_notepad/config.json`

### Customization Options

#### Themes
Create custom themes by adding JSON files to the `themes/` directory:

```json
{
  "name": "Custom Theme",
  "text_widget": {
    "background": "#ffffff",
    "foreground": "#000000",
    "cursor": "#000000",
    "selection": "#0078d4"
  },
  "syntax": {
    "keyword": "#0000ff",
    "string": "#008000",
    "comment": "#808080"
  }
}
```

#### Custom Shortcuts
Modify keyboard shortcuts in the settings file under the `shortcuts` section.

#### Plugin Development
Create plugins by adding Python files to the `plugins/` directory. Plugins should implement the standard plugin interface.

## 🐛 Troubleshooting

### Common Issues

1. **Application won't start**
   - Ensure Python 3.7+ is installed
   - Check that tkinter is available: `python -c "import tkinter"`
   - Verify all dependencies are installed

2. **Spell checking not working**
   - Install pyspellchecker: `pip install pyspellchecker`
   - Enable spell checking in Tools → Options → Editor

3. **Syntax highlighting not working**
   - Ensure the file extension is supported
   - Check that syntax highlighting is enabled in settings
   - Try forcing the language via Format → Force Language

4. **Auto-save not working**
   - Enable auto-save in Tools → Options → General
   - Check auto-save interval settings
   - Verify write permissions in the document folder

### Log Files

Application logs are stored in:
- **Windows**: `%USERPROFILE%\.modern_notepad\logs\`
- **macOS/Linux**: `~/.modern_notepad/logs/`

Check log files for detailed error information.

### Recovery Mode

If the application crashes, recovery files are automatically created:
- Recovery files: `~/.modern_notepad/autosave/recovery_*`
- Auto-save backups: `~/.modern_notepad/autosave/*.autosave`

Access recovery files via Tools → Auto-save → Backup Manager

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/modern-notepad.git
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where applicable
- Add docstrings to all functions and classes
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Inspired by modern code editors like VS Code and Sublime Text
- Icons from [Feather Icons](https://feathericons.com/)
- Syntax highlighting patterns adapted from various open-source editors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/modern-notepad/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/modern-notepad/discussions)
- **Email**: support@modern-notepad.com

## 🗺️ Roadmap

### Upcoming Features
- [ ] Plugin marketplace
- [ ] Multi-cursor editing
- [ ] Code completion
- [ ] Git integration
- [ ] Terminal integration
- [ ] Database viewer
- [ ] FTP/SFTP support
- [ ] Collaborative editing
- [ ] Mobile companion app

### Version History

#### v1.0.0 (Current)
- Initial release
- Core text editing features
- Syntax highlighting
- Themes and customization
- Auto-save and recovery
- Search and replace
- Settings management

---

**Made with ❤️ by the Modern Notepad Team**