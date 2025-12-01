# ui/node_editor.py

import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

from automation_manager.code_editor import CodeEditor
from automation_manager.live_code_runner import LiveCodeRunner

# Starter template shown when code editor is blank
TEMPLATE_CODE = """# Node code template
# ------------------
# - Use `inputs` (dict) to access all incoming variables:
#       inputs['variable_name']
# - Input variables (valid identifiers) are also injected as local variables:
#       e.g., `text` if an upstream node provided `text`
# - At the end of this script, set the `outputs` dict to expose values to downstream nodes.
#
# Example structure:
#   1) Read inputs
#   2) Process them
#   3) Assign results into `outputs = { ... }`
#
# NOTE: Keep values serializable (str, int, float, list, dict, etc.)

# --- Example ---
text = inputs.get("text", "")
user_id = inputs.get("user_id", None)

# Sample processing:
cleaned_text = text.strip()
summary = cleaned_text[:200]  # naive "summary"

# Provide outputs as a dict named `outputs`
outputs = {
    "cleaned_text": cleaned_text,
    "summary": summary,
}
"""


class NodeEditorDialog(QDialog):
    """
    A redesigned, fully responsive Node Editor UI.
    - Uses QSplitter for adjustable panels.
    - Uses QGroupBox for clean visual separation of UI elements.
    - Avoids all fixed sizes to ensure smooth scaling across resolutions.
    """

    def __init__(self, node, inputs=None, initial_code="", parent=None):
        super().__init__(parent)
        self.node = node
        self.inputs = inputs or []
        self.result_data = None
        self.runner = LiveCodeRunner(self)
        self._stdout_streamed = False
        self._stderr_streamed = False
        self._latest_prelude_lines = 0

        self.setWindowTitle(f"Edit Node — {node.title}")
        self.setModal(True)
        # Set a reasonable starting size, but allow it to be resized freely
        self.resize(1200, 800)

        self._init_ui()
        self._connect_runner_signals()
        self._init_shortcuts()
        self._populate_data(initial_code)

    def _init_ui(self):
        """Initialize the user interface components and layout."""

        # --- Create Widgets ---
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        self.outputs_edit = QTextEdit()
        self.outputs_edit.setReadOnly(True)

        self.code_edit = CodeEditor()
        self.code_edit.request_run.connect(self.on_run_code)
        self.code_edit.request_save.connect(self.on_quick_save)
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.run_button = QPushButton("▶ Run")
        self.run_button.clicked.connect(self.on_run_code)
        self.stop_button = QPushButton("■ Stop")
        self.stop_button.clicked.connect(self.on_stop_code)
        self.stop_button.setEnabled(False)
        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("runnerStatusLabel")

        # --- Create GroupBoxes for clean UI separation ---
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
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)
        toolbar_layout.addWidget(self.run_button)
        toolbar_layout.addWidget(self.stop_button)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.status_label)
        code_layout.addLayout(toolbar_layout)
        code_layout.addWidget(self.code_edit)
        code_group.setLayout(code_layout)

        terminal_group = QGroupBox("Terminal Window")
        terminal_layout = QVBoxLayout()
        terminal_layout.addWidget(self.terminal_output)
        terminal_group.setLayout(terminal_layout)

        # --- Create Splitters for a flexible, draggable layout ---
        # Left panel splitter (vertical)
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.addWidget(inputs_group)
        left_splitter.addWidget(outputs_group)
        left_splitter.setStretchFactor(0, 1)  # Give inputs more space initially
        left_splitter.setStretchFactor(1, 1)

        # Right panel splitter (vertical)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(code_group)
        right_splitter.addWidget(terminal_group)
        right_splitter.setStretchFactor(0, 3)  # Give code editor much more space
        right_splitter.setStretchFactor(1, 1)

        # Main splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 1)  # Give left panel less space
        main_splitter.setStretchFactor(1, 3)  # Give right panel much more space

        # --- Create Buttons ---
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        # --- Set Final Layout ---
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        # --- Apply Styles ---
        self._apply_styles()

    def _connect_runner_signals(self):
        self.runner.stdout.connect(self._handle_stdout)
        self.runner.stderr.connect(self._handle_stderr)
        self.runner.finished.connect(self._handle_execution_finished)
        self.runner.failed.connect(self._handle_execution_failed)
        self.runner.cancelled.connect(self._handle_execution_cancelled)
        self.runner.state_changed.connect(self._handle_runner_state)

    def _init_shortcuts(self):
        self._shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self._shortcut_save.activated.connect(self.on_quick_save)
        self._shortcut_run = QShortcut(QKeySequence("Ctrl+Return"), self)
        self._shortcut_run.activated.connect(self.on_run_code)
        self._shortcut_run_alt = QShortcut(QKeySequence("Ctrl+Enter"), self)
        self._shortcut_run_alt.activated.connect(self.on_run_code)
    def _populate_data(self, initial_code):
        """Fill the UI widgets with initial data."""
        # Populate inputs list
        if isinstance(self.inputs, dict):
            for k, v in self.inputs.items():
                self.inputs_list.addItem(f"{k} = {v}")
        else:
            for v in self.inputs:
                self.inputs_list.addItem(str(v))

        # Populate code editor
        existing_code = initial_code if initial_code else getattr(self.node, "code", "")
        if not (existing_code and existing_code.strip()):
            existing_code = TEMPLATE_CODE
        self.code_edit.setPlainText(existing_code)

        # Populate outputs if they already exist
        existing_outputs = getattr(self.node, "outputs", None)
        if existing_outputs:
            self._update_outputs_display(existing_outputs)

    def _apply_styles(self):
        """Consolidate all stylesheet settings here for maintainability."""
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
            QPlainTextEdit {
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
        self.run_button.setStyleSheet(
            """
            QPushButton {
                background-color: #1f5e3b;
                color: #d4ffd4;
                border: 1px solid #2e8b57;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #1f5e3b;
                color: #8a998a;
                border-color: #2e8b57;
                opacity: 0.4;
            }
        """
        )
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #5e1f1f;
                color: #ffd4d4;
                border: 1px solid #8b2e2e;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                opacity: 0.4;
            }
        """
        )
        self.status_label.setStyleSheet(
            """
            QLabel#runnerStatusLabel {
                color: #8ab4f8;
                font-weight: 500;
            }
        """
        )

    def _set_running_state(self, running: bool):
        self.run_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        if running:
            self.status_label.setText("Running…")
        elif self.status_label.text().startswith("Running"):
            self.status_label.setText("Idle")

    def _handle_runner_state(self, state: str):
        state_map = {
            "starting": "Preparing…",
            "running": "Running…",
            "idle": "Idle",
        }
        if state in state_map:
            self.status_label.setText(state_map[state])

    def _handle_stdout(self, text: str):
        if not text:
            return
        self._stdout_streamed = True
        self.terminal_output.appendPlainText(text)

    def _append_stderr_chunk(self, text: str):
        if not text:
            return
        for line in text.splitlines():
            self.terminal_output.appendPlainText(f"[stderr] {line}")

    def _handle_stderr(self, text: str):
        if not text:
            return
        self._stderr_streamed = True
        self._append_stderr_chunk(text)

    def _handle_execution_finished(self, result: dict):
        self._set_running_state(False)
        prelude_lines = result.get("prelude_lines", 0)
        self._latest_prelude_lines = prelude_lines
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")

        if stdout.strip() and not self._stdout_streamed:
            self.terminal_output.appendPlainText(stdout)
        if stderr.strip() and not self._stderr_streamed:
            self._append_stderr_chunk(stderr)

        if stderr.strip():
            self._highlight_error(stderr, prelude_lines)
        else:
            self.code_edit.clear_error_marker()

        outputs = result.get("outputs", {}) or {}
        self.node.outputs = outputs
        self._update_outputs_display(outputs)

    def _handle_execution_failed(self, message: str):
        self._set_running_state(False)
        self._append_stderr_chunk(message)
        self.code_edit.show_error_marker(1, message)

    def _handle_execution_cancelled(self):
        self._set_running_state(False)
        self.terminal_output.appendPlainText("[info] Execution cancelled.")

    def _highlight_error(self, stderr_text: str, prelude_lines: int):
        matches = list(re.finditer(r"line (\d+)", stderr_text))
        if not matches:
            return
        reported_line = int(matches[-1].group(1))
        user_line = max(1, reported_line - prelude_lines)
        last_line = stderr_text.strip().splitlines()[-1] if stderr_text.strip() else ""
        self.code_edit.show_error_marker(user_line, last_line)

    def _update_outputs_display(self, outputs):
        """Helper to format and display the outputs dictionary."""
        if isinstance(outputs, dict):
            formatted = "\n".join(f"{k}: {v}" for k, v in outputs.items())
            self.outputs_edit.setText(formatted)
        elif isinstance(outputs, (list, tuple)):
            formatted = "\n".join(map(str, outputs))
            self.outputs_edit.setText(formatted)
        else:
            self.outputs_edit.setText(str(outputs))

    def _persist_code(self):
        code = self.code_edit.toPlainText()
        output_vars = (
            list(self.node.outputs.keys())
            if isinstance(self.node.outputs, dict)
            else []
        )
        self.node.code = code
        self.node.canvas.save_canvas_state()
        self.result_data = {"code": code, "outputs": output_vars}
        return code

    def on_save(self):
        self._persist_code()
        self.accept()

    def on_quick_save(self):
        self._persist_code()
        self.status_label.setText("Saved")

    def on_run_code(self):
        """Run the code asynchronously and stream output to the terminal."""
        if self.runner.is_running():
            return

        code = self.code_edit.toPlainText()
        actual_inputs = self.inputs if isinstance(self.inputs, dict) else {}
        if not actual_inputs:
            actual_inputs = {"text": "example input", "user_id": 123}

        self.terminal_output.clear()
        self._stdout_streamed = False
        self._stderr_streamed = False
        self.code_edit.clear_error_marker()

        started = self.runner.run(code, actual_inputs)
        if started:
            self._set_running_state(True)

    def on_stop_code(self):
        if self.runner.is_running():
            self.status_label.setText("Stopping…")
            self.runner.stop()

    def reject(self):
        if self.runner.is_running():
            self.runner.stop()
        super().reject()
