# ui/node_editor.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QListWidget,
    QPlainTextEdit,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

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

        self.setWindowTitle(f"Edit Node — {node.title}")
        self.setModal(True)
        # Set a reasonable starting size, but allow it to be resized freely
        self.resize(1200, 800)

        self._init_ui()
        self._populate_data(initial_code)

    def _init_ui(self):
        """Initialize the user interface components and layout."""

        # --- Create Widgets ---
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        self.outputs_edit = QTextEdit()
        self.outputs_edit.setReadOnly(True)

        self.code_edit = QTextEdit()
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)

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
        self.play_button = self.button_box.addButton(
            "▶ Run Code", QDialogButtonBox.ButtonRole.ActionRole
        )
        self.play_button.clicked.connect(self.on_run_code)
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        # --- Set Final Layout ---
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

        # --- Apply Styles ---
        self._apply_styles()

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
        """Helper to format and display the outputs dictionary."""
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
        # The outputs are now derived purely from running the code
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
        """Run the code and show output in terminal and outputs panel."""
        code = self.code_edit.toPlainText()
        actual_inputs = self.inputs if isinstance(self.inputs, dict) else {}
        if not actual_inputs:
            actual_inputs = {"text": "example input", "user_id": 123}

        # We run user code in a subprocess via run_node_code; no local/global dicts needed here
        self.terminal_output.clear()

        # Use the subprocess-based runner to execute node code safely and capture outputs
        from utils.node_runner import run_node_code

        try:
            result = run_node_code(
                code, self.inputs if isinstance(self.inputs, dict) else {}
            )
            # show stdout/stderr
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
