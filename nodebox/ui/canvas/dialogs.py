import ast
import json
import os

from PyQt6.QtCore import QRect, QRegularExpression, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nodebox.core.engine import run_node_code
from nodebox.core.paths import resource_path
from nodebox.core.screen import ScreenManager
from nodebox.nodes.registry import PredefinedNodeRegistry
from nodebox.ui.canvas.palette import NodePaletteItem

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
_BG_DEEP   = "#0A0C10"
_BG_BASE   = "#0F1117"
_BG_RAISED = "#161922"
_BG_HOVER  = "#1C2235"
_BORDER    = "#1E2538"
_ACCENT    = "#6366F1"
_SUCCESS   = "#10B981"
_WARNING   = "#F59E0B"
_DANGER    = "#EF4444"
_TEXT      = "#F0F2F8"
_TEXT_SEC  = "#8892B0"
_TEXT_DIM  = "#4A5578"

TEMPLATE_CODE = """# Node code script
# ------------------
# - Access incoming variables using `inputs`:
#       text = inputs.get('text', '')
# - Return variables to downstream nodes in `outputs`:
#       outputs = {
#           'result': text.upper()
#       }

text = inputs.get("text", "Default text")

outputs = {
    "result": text.upper()
}
"""


def parse_code_outputs(code_str: str) -> list:
    """Extract output keys assigned in code via AST parsing."""
    output_keys = []
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "outputs":
                        if isinstance(node.value, ast.Dict):
                            for key in node.value.keys:
                                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                                    output_keys.append(key.value)
            elif isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id == "outputs":
                    if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                        output_keys.append(node.slice.value)
    except Exception:
        pass
    return list(dict.fromkeys(output_keys))


# ---------------------------------------------------------------------------
# Syntax Highlighter
# ---------------------------------------------------------------------------
class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python node scripts."""

    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Keywords — indigo
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#818CF8"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class",
            "continue", "def", "del", "elif", "else", "except", "finally",
            "for", "from", "global", "if", "import", "in", "is", "lambda",
            "nonlocal", "not", "or", "pass", "raise", "return", "try",
            "while", "with", "yield", "None", "True", "False",
        ]
        for kw in keywords:
            self.rules.append((QRegularExpression(rf"\b{kw}\b"), keyword_fmt))

        # NodeBox builtins — amber
        nodebox_fmt = QTextCharFormat()
        nodebox_fmt.setForeground(QColor("#F59E0B"))
        nodebox_fmt.setFontWeight(QFont.Weight.Bold)
        for nb in ["inputs", "outputs"]:
            self.rules.append((QRegularExpression(rf"\b{nb}\b"), nodebox_fmt))

        # Strings — emerald
        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#34D399"))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_fmt))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_fmt))

        # Numbers — amber light
        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#FBB040"))
        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), number_fmt))

        # Comments — dim gray italic
        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#4A5578"))
        comment_fmt.setFontItalic(True)
        self.rules.append((QRegularExpression(r"#.*"), comment_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


# ---------------------------------------------------------------------------
# Line Number Area
# ---------------------------------------------------------------------------
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #080A10;
                color: #E2E8F8;
                border: 1px solid {_BORDER};
                border-radius: 10px;
                padding: 4px;
                selection-background-color: rgba(99,102,241,0.35);
            }}
        """)
        self.highlighter = PythonSyntaxHighlighter(self.document())

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def line_number_area_width(self):
        digits = 1
        max_b = max(1, self.blockCount())
        while max_b >= 10:
            max_b //= 10
            digits += 1
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#0D0F18"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        painter.setFont(self.font())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                is_current = (block_number == self.textCursor().blockNumber())
                painter.setPen(QColor("#6366F1") if is_current else QColor("#2C3352"))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1


# ---------------------------------------------------------------------------
# Node Editor Dialog (Script Configuration Modal)
# ---------------------------------------------------------------------------
class NodeEditorDialog(QDialog):
    def __init__(self, node, inputs=None, initial_code="", parent=None):
        super().__init__(parent)
        self.node = node
        self.raw_inputs = inputs or {}
        self.result_data = None

        self.setWindowTitle(f"Configure Node — {node.title}")
        self.setModal(True)

        width, height = ScreenManager.get_dialog_window_size(
            width_percentage=0.78,
            height_percentage=0.82,
            min_width=1180,
            min_height=780,
        )
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        self.setGeometry(x, y, width, height)
        self.setStyleSheet(f"QDialog {{ background-color: {_BG_DEEP}; color: {_TEXT}; }}")

        self._init_ui()
        self._populate_data(initial_code)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Gradient header ──────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0E1028, stop:0.5 #111530, stop:1 #0C0E22);
                border-bottom: 1px solid {_BORDER};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        node_title = QLabel(f"Node Script Configuration — {self.node.title}")
        node_title.setFont(QFont("Poppins", 15, QFont.Weight.Bold))
        node_title.setStyleSheet("color: #F0F2F8; background: transparent; border: none;")
        subtitle = QLabel("Configure input bindings, script logic, and output parameters")
        subtitle.setFont(QFont("Poppins", 10))
        subtitle.setStyleSheet("color: #8892B0; background: transparent; border: none;")
        title_col.addWidget(node_title)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch()

        badge = QLabel("Python Node")
        badge.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        badge.setStyleSheet(f"""
            background-color: rgba(99,102,241,0.2);
            color: #818CF8;
            border: 1px solid rgba(99,102,241,0.35);
            font-size: 11px;
            font-weight: 600;
            padding: 4px 14px;
            border-radius: 8px;
        """)
        header_layout.addWidget(badge)
        main_layout.addWidget(header)

        # ── Body ────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet(f"background-color: {_BG_DEEP};")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 16)
        body_layout.setSpacing(14)

        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(1)
        main_splitter.setStyleSheet(f"""
            QSplitter::handle {{ background-color: {_BORDER}; }}
        """)

        # ── Left Panel (I/O Inspector) ──────────────────────────────
        left_panel = QWidget()
        left_panel.setStyleSheet(f"background-color: {_BG_BASE}; border-radius: 12px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        inputs_group = self._make_panel_section("Incoming Inputs", "#4A5578")
        inputs_inner = QVBoxLayout()
        inputs_inner.setContentsMargins(12, 8, 12, 12)
        self.inputs_list = self._make_inspector_list()
        inputs_inner.addWidget(self.inputs_list)
        inputs_group.layout().addLayout(inputs_inner)
        left_layout.addWidget(inputs_group, stretch=1)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {_BORDER}; max-height: 1px; border: none;")
        left_layout.addWidget(sep)

        outputs_group = self._make_panel_section("Detected Outputs", "#10B981")
        outputs_inner = QVBoxLayout()
        outputs_inner.setContentsMargins(12, 8, 12, 12)
        self.outputs_list = self._make_inspector_list()
        outputs_inner.addWidget(self.outputs_list)
        outputs_group.layout().addLayout(outputs_inner)
        left_layout.addWidget(outputs_group, stretch=1)

        main_splitter.addWidget(left_panel)

        # ── Right Panel (Code + Terminal) ───────────────────────────
        right_panel = QWidget()
        right_panel.setStyleSheet(f"background-color: {_BG_DEEP};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Editor header row
        editor_header = QHBoxLayout()
        lang_label = QLabel("PYTHON 3  -  Node Script")
        lang_label.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        lang_label.setStyleSheet("color: #4A5578; letter-spacing: 1px;")
        editor_header.addWidget(lang_label)
        editor_header.addStretch()

        btn_add_out = QPushButton("+ Insert Output Key")
        btn_add_out.setFont(QFont("Poppins", 9, QFont.Weight.DemiBold))
        btn_add_out.setFixedHeight(30)
        btn_add_out.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_out.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: #818CF8;
                border: 1px solid rgba(99,102,241,0.3);
                border-radius: 6px;
                padding: 2px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: rgba(99,102,241,0.15);
                border-color: {_ACCENT};
                color: #A5B4FC;
            }}
        """)
        btn_add_out.clicked.connect(self._insert_output_template)
        editor_header.addWidget(btn_add_out)

        right_layout.addLayout(editor_header)

        self.code_edit = CodeEditor()
        self.code_edit.textChanged.connect(self._on_code_changed)
        right_layout.addWidget(self.code_edit, stretch=3)

        # Terminal section
        terminal_header = QHBoxLayout()
        terminal_label = QLabel("TEST EXECUTION CONSOLE")
        terminal_label.setFont(QFont("Poppins", 9, QFont.Weight.DemiBold))
        terminal_label.setStyleSheet("color: #4A5578; letter-spacing: 1px;")
        terminal_header.addWidget(terminal_label)
        terminal_header.addStretch()

        self.terminal_status = QLabel("Ready")
        self.terminal_status.setFont(QFont("Poppins", 9, QFont.Weight.Medium))
        self.terminal_status.setStyleSheet(f"""
            background-color: rgba(74,85,120,0.15);
            color: {_TEXT_SEC};
            border: 1px solid rgba(74,85,120,0.3);
            border-radius: 5px;
            padding: 2px 10px;
        """)
        terminal_header.addWidget(self.terminal_status)
        right_layout.addLayout(terminal_header)

        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setFont(QFont("Consolas", 11))
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #06080E;
                color: #A8B4C8;
                border: 1px solid {_BORDER};
                border-radius: 10px;
                padding: 10px;
                selection-background-color: rgba(99,102,241,0.35);
            }}
        """)
        right_layout.addWidget(self.terminal_output, stretch=1)

        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)

        body_layout.addWidget(main_splitter)

        # ── Bottom Actions ───────────────────────────────────────────
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        btn_run = QPushButton("Run Test Script")
        btn_run.setFont(QFont("Poppins", 11, QFont.Weight.DemiBold))
        btn_run.setFixedHeight(42)
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: #A5B4FC;
                border: 1px solid rgba(99,102,241,0.35);
                border-radius: 9px;
                padding: 8px 22px;
            }}
            QPushButton:hover {{
                background-color: rgba(99,102,241,0.15);
                border-color: {_ACCENT};
                color: #C7D2FE;
            }}
        """)
        btn_run.clicked.connect(self._on_run_code)
        bottom_layout.addWidget(btn_run)

        bottom_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: {_TEXT_SEC};
                border: 1px solid {_BORDER};
                border-radius: 9px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {_BG_HOVER};
                color: {_TEXT};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Save & Apply Changes")
        btn_save.setFont(QFont("Poppins", 11, QFont.Weight.DemiBold))
        btn_save.setFixedHeight(42)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {_SUCCESS};
                color: #FFFFFF;
                border: none;
                border-radius: 9px;
                padding: 8px 26px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)
        btn_save.clicked.connect(self._on_accept)
        bottom_layout.addWidget(btn_save)

        body_layout.addLayout(bottom_layout)
        main_layout.addWidget(body)

    def _make_panel_section(self, title: str, accent_color: str) -> QFrame:
        """Create a labeled inspector panel section."""
        frame = QFrame()
        frame.setStyleSheet(f"background: transparent;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(36)
        header.setStyleSheet(f"""
            background-color: rgba(255,255,255,0.02);
            border-bottom: 1px solid {_BORDER};
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(14, 0, 14, 0)

        accent_dot = QLabel()
        accent_dot.setFixedSize(8, 8)
        accent_dot.setStyleSheet(f"""
            background-color: {accent_color};
            border-radius: 4px;
        """)
        h_layout.addWidget(accent_dot)

        lbl = QLabel(title.upper())
        lbl.setFont(QFont("Poppins", 9, QFont.Weight.DemiBold))
        lbl.setStyleSheet(f"color: {_TEXT_DIM}; letter-spacing: 1px; background: transparent;")
        h_layout.addWidget(lbl)
        h_layout.addStretch()

        layout.addWidget(header)
        return frame

    def _make_inspector_list(self) -> QListWidget:
        lw = QListWidget()
        lw.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        lw.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 7px 10px;
                border-radius: 7px;
                margin: 2px 0;
                color: #C8D0E8;
                font-size: 11px;
                font-family: Consolas, monospace;
            }}
            QListWidget::item:hover {{
                background-color: {_BG_HOVER};
            }}
            QListWidget::item:selected {{
                background-color: rgba(99,102,241,0.18);
                color: #A5B4FC;
            }}
        """)
        return lw

    def _populate_data(self, initial_code):
        self.inputs_list.clear()

        normalized_inputs = {}
        if isinstance(self.raw_inputs, dict):
            normalized_inputs = self.raw_inputs
        elif isinstance(self.raw_inputs, list):
            normalized_inputs = {v: {"value": None, "source": "Upstream Node"} for v in self.raw_inputs}

        if not normalized_inputs:
            item = QListWidgetItem("No connected upstream inputs")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor(_TEXT_DIM))
            self.inputs_list.addItem(item)
        else:
            for key, info in normalized_inputs.items():
                val_preview = ""
                source = "Upstream Node"
                if isinstance(info, dict):
                    source = info.get("source", "Upstream Node")
                    val = info.get("value")
                    val_preview = f" = {repr(val)[:24]}" if val is not None else ""
                else:
                    val_preview = f" = {repr(info)[:24]}" if info is not None else ""

                item_text = f"{key}{val_preview}"
                item = QListWidgetItem(item_text)
                item.setToolTip(f"Variable: {key}\nSource: {source}\nDouble-click to inject into script")
                self.inputs_list.addItem(item)

        self.inputs_list.itemDoubleClicked.connect(self._inject_selected_input)

        code = (
            initial_code.strip()
            if (initial_code and initial_code.strip())
            else TEMPLATE_CODE.strip()
        )
        self.code_edit.setPlainText(code)
        self._on_code_changed()

    def _inject_selected_input(self, item):
        text = item.text().strip()
        if "No connected" in text:
            return
        var_name = text.split("=")[0].strip() if "=" in text else text
        cursor = self.code_edit.textCursor()
        cursor.insertText(f"inputs.get('{var_name}')")

    def _insert_output_template(self):
        cursor = self.code_edit.textCursor()
        cursor.insertText("\noutputs['new_variable'] = 'value'\n")

    def _on_code_changed(self):
        code = self.code_edit.toPlainText()
        ast_keys = parse_code_outputs(code)

        runtime_outputs = getattr(self.node, "outputs", {})
        merged_keys = list(dict.fromkeys(
            ast_keys + (list(runtime_outputs.keys()) if isinstance(runtime_outputs, dict) else [])
        ))

        self.outputs_list.clear()
        if not merged_keys:
            item = QListWidgetItem("No output keys detected yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor(_TEXT_DIM))
            self.outputs_list.addItem(item)
        else:
            for key in merged_keys:
                val_str = ""
                if isinstance(runtime_outputs, dict) and key in runtime_outputs:
                    val_str = f" = {repr(runtime_outputs[key])[:24]}"
                item = QListWidgetItem(f"outputs['{key}']{val_str}")
                item.setForeground(QColor("#34D399"))
                self.outputs_list.addItem(item)

    def _on_accept(self):
        code = self.code_edit.toPlainText()
        outputs_keys = parse_code_outputs(code)

        runtime_outputs = getattr(self.node, "outputs", {})
        if isinstance(runtime_outputs, dict):
            outputs_keys = list(dict.fromkeys(outputs_keys + list(runtime_outputs.keys())))

        self.result_data = {"code": code, "outputs": outputs_keys}
        self.accept()

    def _on_run_code(self):
        self.terminal_output.clear()
        self._set_terminal_status("Executing...", _WARNING)
        QApplication.processEvents()

        code = self.code_edit.toPlainText()
        inputs_dict = {}
        if isinstance(self.raw_inputs, dict):
            for k, v in self.raw_inputs.items():
                inputs_dict[k] = v["value"] if isinstance(v, dict) and "value" in v else v
        elif isinstance(self.raw_inputs, list):
            inputs_dict = {k: None for k in self.raw_inputs}

        try:
            result = run_node_code(code=code, inputs=inputs_dict)
            stdout_text = result.get("stdout", "")
            stderr_text = result.get("stderr", "")

            if stdout_text:
                self.terminal_output.appendPlainText(stdout_text)
            if stderr_text:
                self.terminal_output.appendPlainText(f"[Error] {stderr_text}")

            outputs = result.get("outputs", {}) or {}
            self.node.outputs = outputs
            self._on_code_changed()

            if result.get("returncode", 0) == 0:
                self._set_terminal_status("Success", _SUCCESS)
            else:
                self._set_terminal_status("Failed", _DANGER)
        except Exception as e:
            self.terminal_output.appendPlainText(f"Execution error: {e}")
            self._set_terminal_status("Exception", _DANGER)

    def _set_terminal_status(self, text: str, color: str):
        self.terminal_status.setText(text)
        self.terminal_status.setStyleSheet(f"""
            background-color: rgba({self._hex_to_rgb(color)},0.15);
            color: {color};
            border: 1px solid rgba({self._hex_to_rgb(color)},0.35);
            border-radius: 5px;
            padding: 2px 10px;
            font-size: 10px;
            font-weight: 600;
        """)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        h = hex_color.lstrip("#")
        return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# Node Editor Window (Canvas Editor)
# ---------------------------------------------------------------------------
class NodeEditorWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, automation_name=None):
        super().__init__()
        self.automation_name = automation_name
        self.setWindowTitle(f"Automation Canvas — {automation_name}")

        x, y, width, height = ScreenManager.get_editor_window_geometry()
        self.setGeometry(x, y, width, height)

        min_width, min_height = ScreenManager.calculate_window_size(
            width_percentage=0.6,
            height_percentage=0.6,
            min_width=1000,
            min_height=700,
        )
        self.setMinimumSize(min_width, min_height)
        self.setStyleSheet(f"background-color: {_BG_DEEP}; color: {_TEXT};")

        self.automation_data = self.load_automation()
        self.setup_ui()

    def setup_ui(self):
        from nodebox.ui.canvas.canvas_widget import CanvasWidget

        self.setWindowTitle(f"Editing — {self.automation_name}")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar Palette ──────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(256)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {_BG_BASE};
                border-right: 1px solid {_BORDER};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Sidebar header
        sb_header = QWidget()
        sb_header.setFixedHeight(52)
        sb_header.setStyleSheet(f"""
            background-color: {_BG_RAISED};
            border-bottom: 1px solid {_BORDER};
        """)
        sb_h_layout = QVBoxLayout(sb_header)
        sb_h_layout.setContentsMargins(14, 0, 14, 0)
        sb_h_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        sb_title = QLabel("NODE PALETTE")
        sb_title.setFont(QFont("Poppins", 9, QFont.Weight.DemiBold))
        sb_title.setStyleSheet(f"color: {_TEXT_DIM}; letter-spacing: 1.5px; background: transparent;")
        sb_h_layout.addWidget(sb_title)
        sidebar_layout.addWidget(sb_header)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search nodes...")
        search_bar.setFixedHeight(38)
        search_bar.setFont(QFont("Poppins", 11))
        search_bar.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 14px;
                border: none;
                border-bottom: 1px solid {_BORDER};
                border-radius: 0;
                background-color: {_BG_BASE};
                color: {_TEXT};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-bottom-color: {_ACCENT};
                background-color: #0E1220;
            }}
        """)
        sidebar_layout.addWidget(search_bar)

        # Scrollable node list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background-color: {_BG_BASE};")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(6)

        def _section_label(text):
            lbl = QLabel(text.upper())
            lbl.setFont(QFont("Poppins", 9, QFont.Weight.DemiBold))
            lbl.setStyleSheet(f"""
                color: {_TEXT_DIM};
                letter-spacing: 1.2px;
                padding: 8px 4px 4px 4px;
                background: transparent;
            """)
            return lbl

        scroll_layout.addWidget(_section_label("Built-in Nodes"))

        predefined_nodes = PredefinedNodeRegistry.get_node_names()
        for node_name in predefined_nodes:
            scroll_layout.addWidget(NodePaletteItem(node_name, sidebar))

        scroll_layout.addWidget(_section_label("Custom Nodes"))
        for n in ["Custom Node"]:
            scroll_layout.addWidget(NodePaletteItem(n, sidebar))

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll_area)

        main_layout.addWidget(sidebar)

        # ── Right Panel (Title + Canvas) ────────────────────────────
        right_panel = QWidget()
        right_panel.setStyleSheet(f"background-color: {_BG_DEEP};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(52)
        title_bar.setStyleSheet(f"""
            background-color: {_BG_BASE};
            border-bottom: 1px solid {_BORDER};
        """)
        title_row = QHBoxLayout(title_bar)
        title_row.setContentsMargins(16, 0, 20, 0)
        title_row.setSpacing(14)

        back_btn = QPushButton("Back to Home")
        back_btn.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        back_btn.setFixedHeight(34)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: {_TEXT_SEC};
                border: 1px solid {_BORDER};
                border-radius: 8px;
                padding: 4px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {_BG_HOVER};
                border-color: {_ACCENT};
                color: {_TEXT};
            }}
        """)
        back_btn.clicked.connect(self.close)
        title_row.addWidget(back_btn)

        # Breadcrumb
        crumb_sep = QLabel("/")
        crumb_sep.setStyleSheet(f"color: {_TEXT_DIM}; font-size: 16px; background: transparent;")
        title_row.addWidget(crumb_sep)

        label = QLabel(self.automation_name)
        label.setFont(QFont("Poppins", 13, QFont.Weight.DemiBold))
        label.setStyleSheet(f"color: {_TEXT}; background: transparent;")
        title_row.addWidget(label)

        title_row.addStretch()

        # Save button
        save_button = QPushButton("Save")
        save_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        save_button.setFixedHeight(34)
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: {_TEXT_SEC};
                border: 1px solid {_BORDER};
                border-radius: 8px;
                padding: 4px 18px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {_BG_HOVER};
                border-color: {_ACCENT};
                color: {_TEXT};
            }}
        """)

        # Play button
        play_button = QPushButton("Run Graph")
        svg_path = resource_path("assets/icons/play.svg")
        play_button.setIcon(QIcon(svg_path))
        play_button.setIconSize(QSize(16, 16))
        play_button.setFixedHeight(34)
        play_button.setCursor(Qt.CursorShape.PointingHandCursor)
        play_button.setFont(QFont("Poppins", 10, QFont.Weight.DemiBold))
        play_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {_SUCCESS};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 4px 20px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)

        title_row.addWidget(save_button)
        title_row.addWidget(play_button)
        right_layout.addWidget(title_bar)

        self.canvas_widget = CanvasWidget(
            automation_name=self.automation_name, automation_data=self.automation_data
        )
        right_layout.addWidget(self.canvas_widget, stretch=1)

        main_layout.addWidget(right_panel, stretch=1)

        self.play_button = play_button
        self.play_button.clicked.connect(self.run_automation_with_cursor)

    def run_automation_with_cursor(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.canvas_widget.run_all_nodes()
        finally:
            QApplication.restoreOverrideCursor()

    def load_automation(self):
        path = os.path.expanduser(f"~/.nodebox/automations/{self.automation_name}.json")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump({"nodes": [], "connections": []}, f, indent=2)

        try:
            with open(path, "r+") as f:
                try:
                    data = json.load(f)
                    changed = False
                    if "nodes" not in data:
                        data["nodes"] = []
                        changed = True
                    if "connections" not in data:
                        data["connections"] = []
                        changed = True
                    if changed:
                        f.seek(0)
                        json.dump(data, f, indent=2)
                        f.truncate()
                    return data
                except json.JSONDecodeError:
                    data = {"nodes": [], "connections": []}
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()
                    return data
        except Exception as e:
            print("Failed to read or initialize automation JSON:", e)
            return {"nodes": [], "connections": []}

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


__all__ = ["NodeEditorDialog", "NodeEditorWindow", "CodeEditor", "PythonSyntaxHighlighter"]
