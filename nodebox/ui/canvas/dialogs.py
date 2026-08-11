import json
import os

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
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

TEMPLATE_CODE = """# Node code template
# ------------------
# - Use `inputs` (dict) to access all incoming variables:
#       inputs['variable_name']
# - Input variables (valid identifiers) are also injected as local variables:
#       e.g., `text` if an upstream node provided `text`
# - At the end of this script, set the `outputs` dict to expose values to downstream nodes.

text = inputs.get("text", "")
user_id = inputs.get("user_id", None)

cleaned_text = text.strip()
summary = cleaned_text[:200]

outputs = {
    "cleaned_text": cleaned_text,
    "summary": summary,
}
"""


class NodeEditorDialog(QDialog):
    def __init__(self, node, inputs=None, initial_code="", parent=None):
        super().__init__(parent)
        self.node = node
        self.inputs = inputs or []
        self.result_data = None

        self.setWindowTitle(f"Edit Node — {node.title}")
        self.setModal(True)
        self.resize(1200, 800)

        self._init_ui()
        self._populate_data(initial_code)

    def _init_ui(self):
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        self.outputs_edit = QTextEdit()
        self.outputs_edit.setReadOnly(True)

        self.code_edit = QTextEdit()
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)

        inputs_group = QGroupBox("Available Inputs")
        inputs_layout = QVBoxLayout()
        inputs_layout.addWidget(self.inputs_list)
        inputs_group.setLayout(inputs_layout)

        outputs_group = QGroupBox("Detected Outputs")
        outputs_layout = QVBoxLayout()
        outputs_layout.addWidget(self.outputs_edit)
        outputs_group.setLayout(outputs_layout)

        code_group = QGroupBox("Python Code")
        code_layout = QVBoxLayout()
        code_layout.addWidget(self.code_edit)
        code_group.setLayout(code_layout)

        terminal_group = QGroupBox("Terminal Window")
        terminal_layout = QVBoxLayout()
        terminal_layout.addWidget(self.terminal_output)
        terminal_group.setLayout(terminal_layout)

        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.addWidget(inputs_group)
        left_splitter.addWidget(outputs_group)
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(code_group)
        right_splitter.addWidget(terminal_group)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 1)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.play_button = self.button_box.addButton(
            "▶ Run Code", QDialogButtonBox.ButtonRole.ActionRole
        )
        self.play_button.clicked.connect(self.on_run_code)
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        self._apply_styles()

    def _populate_data(self, initial_code):
        if isinstance(self.inputs, dict):
            for k, v in self.inputs.items():
                self.inputs_list.addItem(f"{k} = {v}")
        else:
            for v in self.inputs:
                self.inputs_list.addItem(str(v))

        existing_code = initial_code if initial_code else getattr(self.node, "code", "")
        if not (existing_code and existing_code.strip()):
            existing_code = TEMPLATE_CODE
        self.code_edit.setPlainText(existing_code)

        existing_outputs = getattr(self.node, "outputs", None)
        if existing_outputs:
            self._update_outputs_display(existing_outputs)

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2a2a2a;
            }
            QGroupBox {
                color: #d4d4d4;
                border: 1px solid #444444;
                margin-top: 10px;
                padding: 10px 5px 5px 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                left: 10px;
            }
            QLabel {
                color: #d4d4d4;
            }
        """
        )
        self.inputs_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444444;
            }
        """
        )
        self.outputs_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444444;
            }
        """
        )
        self.code_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #151515;
                color: #d4d4d4;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
                border: 1px solid #444444;
            }
        """
        )
        self.terminal_output.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #000000;
                color: #00ff00;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #444444;
            }
        """
        )

    def _update_outputs_display(self, outputs):
        if isinstance(outputs, dict):
            formatted = "\n".join(f"{k}: {v}" for k, v in outputs.items())
            self.outputs_edit.setText(formatted)
        elif isinstance(outputs, (list, tuple)):
            formatted = "\n".join(map(str, outputs))
            self.outputs_edit.setText(formatted)
        else:
            self.outputs_edit.setText(str(outputs))

    def on_save(self):
        code = self.code_edit.toPlainText()
        output_vars = (
            list(self.node.outputs.keys())
            if isinstance(self.node.outputs, dict)
            else []
        )

        self.node.code = code
        self.node.canvas.save_canvas_state()
        self.result_data = {"code": code, "outputs": output_vars}
        self.accept()

    def on_run_code(self):
        code = self.code_edit.toPlainText()
        self.terminal_output.clear()

        try:
            result = run_node_code(
                code, self.inputs if isinstance(self.inputs, dict) else {}
            )
            stdout_text = result.get("stdout", "") or ""
            stderr_text = result.get("stderr", "") or ""
            if stdout_text.strip():
                self.terminal_output.appendPlainText(stdout_text)
            if stderr_text.strip():
                self.terminal_output.appendPlainText(stderr_text)

            outputs = result.get("outputs", {}) or {}
            self.node.outputs = outputs
            self._update_outputs_display(outputs)
        except Exception as e:
            self.terminal_output.appendPlainText(f"Execution error: {e}")


class NodeEditorWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, automation_name=None):
        super().__init__()
        self.automation_name = automation_name
        self.setWindowTitle(f"Automation: {automation_name}")

        x, y, width, height = ScreenManager.get_editor_window_geometry()
        self.setGeometry(x, y, width, height)

        min_width, min_height = ScreenManager.calculate_window_size(
            width_percentage=0.6,
            height_percentage=0.6,
            min_width=1000,
            min_height=700,
        )
        self.setMinimumSize(min_width, min_height)
        self.setStyleSheet("background-color: #2a2a2a; color: white;")

        self.automation_data = self.load_automation()
        self.setup_ui()

    def setup_ui(self):
        from nodebox.ui.canvas.canvas_widget import CanvasWidget

        self.setWindowTitle(f"Editing Automation: {self.automation_name}")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #202020;")
        sidebar_layout = QVBoxLayout(sidebar)

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search nodes...")
        search_bar.setStyleSheet(
            "padding: 5px; font-size: 14px; background-color: #333333"
        )
        sidebar_layout.addWidget(search_bar)

        predefined_label = QLabel("Predefined Nodes")
        predefined_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 5px 5px 5px; color: #aaaaaa;"
        )
        sidebar_layout.addWidget(predefined_label)

        predefined_nodes = PredefinedNodeRegistry.get_node_names()
        for node_name in predefined_nodes:
            sidebar_layout.addWidget(NodePaletteItem(node_name, sidebar))

        custom_label = QLabel("Custom Nodes")
        custom_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 5px 5px 5px; color: #aaaaaa;"
        )
        sidebar_layout.addWidget(custom_label)

        nodes = ["Custom Node"]
        for n in nodes:
            sidebar_layout.addWidget(NodePaletteItem(n, sidebar))

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        title_row = QHBoxLayout()
        label = QLabel(f"Editing Automation: {self.automation_name}")
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")

        title_row.addWidget(label)
        title_row.addStretch()

        play_button = QPushButton()
        svg_path = resource_path("assets/icons/play.svg")
        play_button.setIcon(QIcon(svg_path))
        play_button.setIconSize(QSize(28, 28))
        play_button.setFixedSize(40, 40)
        play_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """
        )

        title_row.addWidget(play_button, alignment=Qt.AlignmentFlag.AlignRight)
        right_layout.addLayout(title_row)

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


__all__ = ["NodeEditorDialog", "NodeEditorWindow"]
