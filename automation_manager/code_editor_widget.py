"""
IntelliSense-enabled Code Editor for NodeBox
Uses QScintilla for advanced code editing features including:
- Syntax highlighting for Python
- Autocomplete for Python keywords and standard library
- Context-aware suggestions for node inputs/outputs
- Function signatures and docstrings
- Line numbers and code folding
- Brace matching
"""

import keyword
import builtins

try:
    from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
    from PyQt6.QtGui import QFont, QColor
    from PyQt6.QtCore import Qt
    QSCINTILLA_AVAILABLE = True
except ImportError:
    QSCINTILLA_AVAILABLE = False
    # Fallback to QTextEdit if QScintilla is not available
    from PyQt6.QtWidgets import QTextEdit
    from PyQt6.QtGui import QFont, QColor
    from PyQt6.QtCore import Qt

try:
    import jedi
    JEDI_AVAILABLE = True
except ImportError:
    JEDI_AVAILABLE = False


class EditorConfig:
    """Configuration class for IntelliSense editor settings."""
    def __init__(self):
        # Autocomplete settings
        self.autocomplete_threshold = 1  # Characters before showing autocomplete
        self.autocomplete_case_sensitive = False
        self.autocomplete_enabled = True
        self.show_line_numbers = True
        self.show_fold_margin = True
        self.tab_width = 4
        self.use_tabs = False
        self.edge_column = 88  # PEP 8 line length
        self.enable_brace_matching = True
        self.highlight_current_line = True
        self.enable_code_folding = True


# Base class selection based on availability
if QSCINTILLA_AVAILABLE:
    BaseEditorClass = QsciScintilla
else:
    from PyQt6.QtWidgets import QTextEdit
    BaseEditorClass = QTextEdit
    print("Warning: QScintilla not available. Using basic QTextEdit. Install PyQt6-QScintilla for IntelliSense features.")


class IntelliSenseCodeEditor(BaseEditorClass):
    """
    Advanced Python code editor with IntelliSense features.
    Falls back to basic QTextEdit if QScintilla is not available.
    """
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        
        # Configuration
        self.config = config if config else EditorConfig()
        
        # Node context for autocomplete
        self.node_inputs = {}
        self.node_outputs = {}
        
        # Initialize editor only if QScintilla is available
        if QSCINTILLA_AVAILABLE:
            self._setup_editor()
            self._setup_lexer()
            self._setup_autocomplete()
            self._setup_styles()
        else:
            # Basic setup for QTextEdit fallback
            self._setup_basic_editor()
    
    def _setup_basic_editor(self):
        """Setup basic editor when QScintilla is not available."""
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11pt;
                border: 1px solid #444444;
            }
        """)
        
    def _setup_editor(self):
        """Configure basic editor settings."""
        # Font
        font = QFont("Consolas", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setMarginsFont(font)
        
        # Line numbers
        if self.config.show_line_numbers:
            self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
            self.setMarginWidth(0, "00000")
            self.setMarginsForegroundColor(QColor("#888888"))
            self.setMarginsBackgroundColor(QColor("#2a2a2a"))
        
        # Folding
        if self.config.enable_code_folding:
            self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
            self.setFoldMarginColors(QColor("#2a2a2a"), QColor("#2a2a2a"))
        
        # Indentation
        self.setIndentationsUseTabs(self.config.use_tabs)
        self.setTabWidth(self.config.tab_width)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)
        self.setTabIndents(True)
        
        # Brace matching
        if self.config.enable_brace_matching:
            self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
            self.setMatchedBraceBackgroundColor(QColor("#3a3a3a"))
            self.setMatchedBraceForegroundColor(QColor("#00ff00"))
        
        # Current line highlighting
        if self.config.highlight_current_line:
            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QColor("#2d2d2d"))
            self.setCaretForegroundColor(QColor("#ffffff"))
        
        # Edge mode (line length indicator)
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(self.config.edge_column)
        self.setEdgeColor(QColor("#3a3a3a"))
        
        # Whitespace visibility
        self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsInvisible)
        
        # Scroll width
        self.setScrollWidth(1)
        self.setScrollWidthTracking(True)
        
        # Wrap mode
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        
    def _setup_lexer(self):
        """Setup Python syntax highlighting."""
        lexer = QsciLexerPython(self)
        lexer.setDefaultFont(self.font())
        
        # Color scheme (VS Code Dark+ inspired)
        lexer.setColor(QColor("#d4d4d4"), QsciLexerPython.Default)  # Default
        lexer.setColor(QColor("#6a9955"), QsciLexerPython.Comment)  # Comments
        lexer.setColor(QColor("#6a9955"), QsciLexerPython.CommentBlock)  # Block comments
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.Number)  # Numbers
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.DoubleQuotedString)  # Strings
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.SingleQuotedString)  # Strings
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.TripleSingleQuotedString)  # Docstrings
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.TripleDoubleQuotedString)  # Docstrings
        lexer.setColor(QColor("#c586c0"), QsciLexerPython.Keyword)  # Keywords
        lexer.setColor(QColor("#4ec9b0"), QsciLexerPython.ClassName)  # Class names
        lexer.setColor(QColor("#dcdcaa"), QsciLexerPython.FunctionMethodName)  # Functions
        lexer.setColor(QColor("#569cd6"), QsciLexerPython.Operator)  # Operators
        lexer.setColor(QColor("#9cdcfe"), QsciLexerPython.Identifier)  # Identifiers
        lexer.setColor(QColor("#d4d4d4"), QsciLexerPython.Decorator)  # Decorators
        
        # Set paper (background) colors
        lexer.setPaper(QColor("#1e1e1e"))
        for style in range(16):
            lexer.setPaper(QColor("#1e1e1e"), style)
        
        self.setLexer(lexer)
        
    def _setup_autocomplete(self):
        """Setup autocomplete features."""
        if not self.config.autocomplete_enabled:
            return
            
        # Autocomplete settings
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(self.config.autocomplete_threshold)
        self.setAutoCompletionCaseSensitivity(self.config.autocomplete_case_sensitive)
        self.setAutoCompletionReplaceWord(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)
        
        # Create API for autocomplete
        self.api = QsciAPIs(self.lexer())
        
        # Add Python keywords
        for kw in keyword.kwlist:
            self.api.add(kw)
        
        # Add Python builtins
        for name in dir(builtins):
            if not name.startswith('_'):
                try:
                    obj = getattr(builtins, name)
                    if callable(obj):
                        # Try to get signature
                        try:
                            import inspect
                            sig = inspect.signature(obj)
                            self.api.add(f"{name}{sig}")
                        except Exception:
                            self.api.add(f"{name}()")
                    else:
                        self.api.add(name)
                except Exception:
                    self.api.add(name)
        
        # Add common standard library modules and their functions
        self._add_stdlib_completions()
        
        # Add Python code snippets
        self._add_code_snippets()
        
        # Prepare the API
        self.api.prepare()
        
        # Call tips
        self.setCallTipsStyle(QsciScintilla.CallTipsStyle.CallTipsContext)
        self.setCallTipsVisible(0)
        self.setCallTipsBackgroundColor(QColor("#2a2a2a"))
        self.setCallTipsForegroundColor(QColor("#d4d4d4"))
        self.setCallTipsHighlightColor(QColor("#007acc"))
        
    def _add_stdlib_completions(self):
        """Add common standard library completions."""
        # Common imports and their main functions/classes
        stdlib_items = {
            'os': ['path', 'getcwd', 'chdir', 'listdir', 'mkdir', 'remove', 'rename', 'environ'],
            'sys': ['argv', 'exit', 'path', 'stdin', 'stdout', 'stderr', 'platform'],
            'json': ['loads', 'dumps', 'load', 'dump'],
            'math': ['sqrt', 'sin', 'cos', 'tan', 'pi', 'e', 'floor', 'ceil'],
            'datetime': ['datetime', 'date', 'time', 'timedelta'],
            'random': ['random', 'randint', 'choice', 'shuffle', 'sample'],
            're': ['match', 'search', 'findall', 'sub', 'compile'],
            'pathlib': ['Path'],
            'collections': ['defaultdict', 'Counter', 'OrderedDict', 'deque'],
            'itertools': ['chain', 'combinations', 'permutations', 'product'],
            'functools': ['reduce', 'partial', 'wraps', 'lru_cache'],
            'typing': ['List', 'Dict', 'Tuple', 'Set', 'Optional', 'Union', 'Any'],
        }
        
        for module, items in stdlib_items.items():
            for item in items:
                self.api.add(f"{module}.{item}")
                self.api.add(item)
    
    def _add_code_snippets(self):
        """Add common Python code snippets for faster coding."""
        snippets = {
            # Control flow
            'for_loop': 'for item in items:\n    pass',
            'while_loop': 'while condition:\n    pass',
            'if_else': 'if condition:\n    pass\nelse:\n    pass',
            'try_except': 'try:\n    pass\nexcept Exception as e:\n    pass',
            'with_open': 'with open(filename, "r") as f:\n    content = f.read()',
            
            # Functions
            'def_function': 'def function_name(args):\n    """Docstring"""\n    pass',
            'lambda_func': 'lambda x: x',
            
            # Classes
            'class_def': 'class ClassName:\n    def __init__(self):\n        pass',
            
            # Common patterns
            'list_comp': '[x for x in items if condition]',
            'dict_comp': '{k: v for k, v in items.items()}',
            'enumerate_loop': 'for i, item in enumerate(items):\n    pass',
            'zip_loop': 'for a, b in zip(list1, list2):\n    pass',
            
            # Node-specific patterns
            'node_template': '# Access inputs\nvalue = inputs.get("key", default)\n\n# Process data\nresult = value\n\n# Set outputs\noutputs = {\n    "result": result\n}',
        }
        
        for name, snippet in snippets.items():
            # Add snippet name with a comment indicator
            self.api.add(f"{name}  # snippet")
        
    def _setup_styles(self):
        """Apply custom styling."""
        # Selection colors
        self.setSelectionBackgroundColor(QColor("#264f78"))
        self.setSelectionForegroundColor(QColor("#ffffff"))
        
        # Autocomplete list styling
        self.SendScintilla(QsciScintilla.SCI_AUTOCSETMAXHEIGHT, 10)
        
    def set_node_context(self, inputs=None, outputs=None):
        """
        Set the node context for context-aware autocomplete.
        
        Args:
            inputs: Dictionary of input variable names and their values/types
            outputs: Dictionary of output variable names and their values/types
        """
        self.node_inputs = inputs or {}
        self.node_outputs = outputs or {}
        
        # Add node-specific variables to autocomplete (only if QScintilla available)
        if QSCINTILLA_AVAILABLE:
            self._update_node_completions()
        
    def _update_node_completions(self):
        """Update autocomplete with node-specific variables."""
        # Clear and recreate API to include node variables
        self.api.clear()
        
        # Re-add Python keywords
        for kw in keyword.kwlist:
            self.api.add(kw)
        
        # Re-add builtins (simplified)
        for name in dir(builtins):
            if not name.startswith('_'):
                self.api.add(name)
        
        # Add standard library
        self._add_stdlib_completions()
        
        # Add node-specific inputs with descriptions
        self.api.add("inputs")  # The inputs dict itself
        for var_name, var_value in self.node_inputs.items():
            var_type = type(var_value).__name__ if var_value is not None else "Any"
            self.api.add(f"{var_name}")  # Just the variable name
            self.api.add(f"inputs['{var_name}']")  # Dict access
            # Add with type hint as tooltip
            self.api.add(f"{var_name}  # type: {var_type}")
        
        # Add node-specific outputs
        self.api.add("outputs")  # The outputs dict
        for var_name in self.node_outputs:
            self.api.add(f"outputs['{var_name}']")
        
        # Prepare the updated API
        self.api.prepare()
    
    def keyPressEvent(self, event):
        """
        Handle key press events for enhanced autocomplete behavior.
        """
        if not QSCINTILLA_AVAILABLE:
            # Fallback to default behavior
            super().keyPressEvent(event)
            return
            
        # Trigger autocomplete on dot (for attribute/method access)
        if event.text() == '.':
            super().keyPressEvent(event)
            self.autoCompleteFromAll()
            return
        
        # Trigger autocomplete on Ctrl+Space
        if event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.autoCompleteFromAll()
            return
        
        # Handle tab for indentation
        if event.key() == Qt.Key.Key_Tab:
            if self.isListActive():
                # If autocomplete is active, tab selects the item
                super().keyPressEvent(event)
            else:
                # Otherwise, insert indentation
                self.indent()
            return
        
        super().keyPressEvent(event)
        
        # Auto-trigger autocomplete after typing
        if event.text().isalnum() or event.text() in ['_', '.']:
            if len(self.text()) > 0:
                self.autoCompleteFromAll()
    
    def get_jedi_completions(self, source, line, column):
        """
        Get completions from Jedi for advanced IntelliSense.
        
        Args:
            source: Full source code text
            line: Current line number (1-indexed)
            column: Current column number (0-indexed)
            
        Returns:
            List of completion strings
        """
        if not JEDI_AVAILABLE:
            return []
        
        try:
            script = jedi.Script(source, path='<input>')
            completions = script.complete(line, column)
            
            results = []
            for completion in completions:
                name = completion.name
                # Add type information if available
                if completion.type:
                    name += f"  # {completion.type}"
                results.append(name)
            
            return results
        except Exception as e:
            print(f"Jedi completion error: {e}")
            return []
    
    def setText(self, text):
        """Override setText to maintain compatibility with QTextEdit API."""
        super().setText(text)
        
    def toPlainText(self):
        """Override toPlainText to maintain compatibility with QTextEdit API."""
        return self.text()
    
    def setPlainText(self, text):
        """Override setPlainText to maintain compatibility with QTextEdit API."""
        self.setText(text)
