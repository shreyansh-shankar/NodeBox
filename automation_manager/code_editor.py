from __future__ import annotations

import re

from PyQt6.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QKeyEvent,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PyQt6.QtWidgets import QPlainTextEdit, QWidget


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return self._editor._line_number_area_size_hint()

    def paintEvent(self, event):
        self._editor._paint_line_numbers(event)


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._setup_rules()

    def _setup_rules(self):
        def format_color(color: str, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            if italic:
                fmt.setFontItalic(True)
            return fmt

        keyword_format = format_color("#C586C0", bold=True)
        builtin_format = format_color("#4FC1FF")
        string_format = format_color("#CE9178")
        comment_format = format_color("#6A9955", italic=True)
        number_format = format_color("#B5CEA8")
        function_format = format_color("#DCDCAA")

        keywords = [
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "False",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "None",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "True",
            "try",
            "while",
            "with",
            "yield",
        ]
        builtins = [
            "print",
            "len",
            "range",
            "enumerate",
            "list",
            "dict",
            "set",
            "int",
            "float",
            "str",
            "bool",
            "sum",
            "min",
            "max",
            "any",
            "all",
            "zip",
            "map",
            "filter",
        ]

        self._rules = []
        word_boundary = r"\b"
        for kw in keywords:
            pattern = re.compile(fr"{word_boundary}{kw}{word_boundary}")
            self._rules.append((pattern, keyword_format))
        for bi in builtins:
            pattern = re.compile(fr"{word_boundary}{bi}{word_boundary}")
            self._rules.append((pattern, builtin_format))

        self._rules.extend(
            [
                (re.compile(r"\b[0-9]+(\.[0-9]+)?\b"), number_format),
                (re.compile(r"'[^'\\\\]*(?:\\\\.[^'\\\\]*)*'"), string_format),
                (re.compile(r'\\"[^"\\\\]*(?:\\\\.[^"\\\\]*)*\\"'), string_format),
                (re.compile(r"#.*"), comment_format),
            ]
        )
        self._function_decl = re.compile(r"\bdef\s+(\w+)")
        self._function_format = function_format

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

        for match in self._function_decl.finditer(text):
            start, end = match.span(1)
            self.setFormat(start, end - start, self._function_format)

        self.setCurrentBlockState(0)

        # Multi-line triple quoted strings
        self._apply_multiline_string(text, "'''", QColor("#CE9178"))
        self._apply_multiline_string(text, '\"\"\"', QColor("#CE9178"))

    def _apply_multiline_string(self, text: str, delimiter: str, color: QColor):
        start_expr = delimiter
        end_expr = delimiter
        start_idx = 0
        fmt = QTextCharFormat()
        fmt.setForeground(color)

        if self.previousBlockState() == 1:
            end_idx = text.find(end_expr, start_idx)
            if end_idx == -1:
                self.setFormat(start_idx, len(text) - start_idx, fmt)
                self.setCurrentBlockState(1)
                return
            self.setFormat(start_idx, end_idx - start_idx + len(end_expr), fmt)
            start_idx = end_idx + len(end_expr)

        while True:
            start_idx = text.find(start_expr, start_idx)
            if start_idx == -1:
                break
            end_idx = text.find(end_expr, start_idx + len(start_expr))
            if end_idx == -1:
                self.setFormat(start_idx, len(text) - start_idx, fmt)
                self.setCurrentBlockState(1)
                break
            self.setFormat(start_idx, end_idx - start_idx + len(end_expr), fmt)
            start_idx = end_idx + len(end_expr)


class CodeEditor(QPlainTextEdit):
    request_run = pyqtSignal()
    request_save = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("JetBrains Mono", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self._tab_stop())
        self.setViewportMargins(48, 0, 0, 0)
        self._line_number_area = LineNumberArea(self)
        self._error_line = None
        self._error_selection = None

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlighter = PythonHighlighter(self.document())
        self.highlightCurrentLine()

    def _tab_stop(self):
        metrics: QFontMetrics = self.fontMetrics()
        return metrics.horizontalAdvance(" ") * 4

    # --- Line number area helpers ---
    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def _line_number_area_size_hint(self):
        return QSize(self.lineNumberAreaWidth(), 0)

    def _paint_line_numbers(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#1c1c1c"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#6A6A6A"))
                fm = self.fontMetrics()
                painter.drawText(
                    0,
                    top,
                    self.lineNumberAreaWidth() - 6,
                    fm.height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # --- Highlighting helpers ---
    def highlightCurrentLine(self):
        if self.isReadOnly():
            self.setExtraSelections([])
            return

        selections = []

        selection = QPlainTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#2d2d2d"))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        selections.append(selection)

        if self._error_selection:
            selections.append(self._error_selection)

        self.setExtraSelections(selections)

    def show_error_marker(self, line_number: int, message: str | None = None):
        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(
            QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, max(line_number - 1, 0)
        )
        self._error_selection = QPlainTextEdit.ExtraSelection()
        self._error_selection.format.setBackground(QColor("#4d1f1f"))
        self._error_selection.format.setProperty(
            QTextFormat.Property.FullWidthSelection, True
        )
        self._error_selection.cursor = cursor
        self.setToolTip(message or "")
        self.highlightCurrentLine()

    def clear_error_marker(self):
        self._error_selection = None
        self.setToolTip("")
        self.highlightCurrentLine()

    # --- Key handling ---
    def keyPressEvent(self, event: QKeyEvent):
        modifiers = event.modifiers()
        if event.key() == Qt.Key.Key_S and modifiers & Qt.KeyboardModifier.ControlModifier:
            event.accept()
            self.request_save.emit()
            return
        if (
            event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            event.accept()
            self.request_run.emit()
            return
        if event.key() == Qt.Key.Key_Tab and not modifiers:
            self.insertPlainText(" " * 4)
            return
        if event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 4
            )
            if cursor.selectedText().startswith(" "):
                cursor.removeSelectedText()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            indent = re.match(r"\s*", cursor.selectedText()).group(0)
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        super().keyPressEvent(event)

