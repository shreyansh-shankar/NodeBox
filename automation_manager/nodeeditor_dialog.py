# ui/node_editor.py
import io
import sys

from PyQt6.QtWidgets import (  # type: ignore
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
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
    Basic Node Editor UI:
    - Title (editable)
    - Inputs list (read-only)
    - Code editor (QTextEdit)
    - Outputs (comma-separated)
    - Save / Cancel buttons
    """

    def __init__(self, node, inputs=None, initial_code="", parent=None):
        super().__init__(parent)
        self.node = node
        self.setWindowTitle(f"Edit Node — {node.title}")
        self.setModal(True)
        self.setMinimumSize(1200, 800)

        # Inputs: list of variable names (strings)
        self.inputs = inputs or []  # list[str]

        # Result stored after accept
        self.result_data = None

        # --- UI widgets ---
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        if isinstance(self.inputs, dict):
            for k, v in self.inputs.items():
                self.inputs_list.addItem(f"{k} = {v}")
        else:
            for v in self.inputs:
                self.inputs_list.addItem(str(v))

        self.code_edit = QTextEdit()
        # Prefill code if node provides stored code (optional attr 'code')
        existing_code = initial_code if initial_code else getattr(node, "code", "")
        if not (existing_code and existing_code.strip()):
            existing_code = TEMPLATE_CODE
        self.code_edit.setPlainText(existing_code)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        # Add Play button
        self.play_button = self.button_box.addButton(
            "▶ Run", QDialogButtonBox.ButtonRole.ActionRole
        )
        self.play_button.clicked.connect(self.on_run_code)

        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Available Inputs"))
        left_layout.addWidget(self.inputs_list)

        # Outputs edit background (moved here)
        self.outputs_edit = QTextEdit()
        self.outputs_edit.setReadOnly(True)
        self.outputs_edit.setFixedWidth(300)
        self.outputs_edit.setFixedHeight(500)
        self.outputs_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
            }
        """
        )
        left_layout.addWidget(QLabel("Detected Outputs"))
        left_layout.addWidget(self.outputs_edit)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Python Code"))
        right_layout.addWidget(self.code_edit)
        self.terminal_output = QPlainTextEdit()
        right_layout.addWidget(QLabel("Terminal Window"))
        right_layout.addWidget(self.terminal_output)

        # Main layout: inputs on left (narrow), code on right (wide)
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget, 1)
        main_layout.addLayout(right_layout, 2)

        outer = QVBoxLayout(self)
        outer.addLayout(main_layout)
        outer.addWidget(self.button_box)

        # Inputs list background
        self.inputs_list.setFixedWidth(300)
        self.inputs_list.setFixedHeight(500)
        self.inputs_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
            }
        """
        )

        # Code editor background
        self.code_edit.setFixedWidth(900)
        self.code_edit.setFixedHeight(700)
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

        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFixedHeight(200)
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

        # If node already has saved outputs, show them
        existing_outputs = getattr(node, "outputs", None)
        if existing_outputs:
            if isinstance(existing_outputs, dict):
                formatted = "\n".join(f"{k}: {v}" for k, v in existing_outputs.items())
                self.outputs_edit.setText(formatted)
            elif isinstance(existing_outputs, (list, tuple)):
                formatted = "\n".join(map(str, existing_outputs))
                self.outputs_edit.setText(formatted)
            else:
                self.outputs_edit.setText(str(existing_outputs))

    def on_save(self):
        code = self.code_edit.toPlainText()
        outputs_raw = self.outputs_edit.toPlainText()

        # Always define output_vars
        if isinstance(self.node.outputs, dict):
            output_vars = list(self.node.outputs.keys())
        else:
            output_vars = [o.strip() for o in outputs_raw.split(",") if o.strip()]
            self.node.outputs = dict.fromkeys(output_vars)

        self.node.code = code
        self.node.canvas.save_canvas_state()

        # Prepare result dict
        self.result_data = {
            "code": code,
            "outputs": output_vars,
        }

        self.accept()

    def on_run_code(self):
        """Run the code and show output in terminal window."""
        code = self.code_edit.toPlainText()

        actual_inputs = self.inputs if isinstance(self.inputs, dict) else {}
        if not actual_inputs:
            # fallback to dummy values
            actual_inputs = {"text": "example input", "user_id": 123}

        local_vars = {}
        global_vars = {
            "__builtins__": __builtins__,
            "inputs": actual_inputs,
            **actual_inputs,
        }

        self.terminal_output.clear()

        # Redirect stdout/stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = stdout_buffer, stderr_buffer

        try:
            exec(code, global_vars, local_vars)
            outputs = local_vars.get("outputs", {})
            if isinstance(outputs, dict):
                self.node.outputs = outputs
                formatted = "\n".join(f"{k}: {v}" for k, v in outputs.items())
                self.outputs_edit.setText(formatted)

        except Exception as e:
            self.terminal_output.appendPlainText(f"Error: {e}")
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

        # Show output in terminal
        output_text = stdout_buffer.getvalue() + stderr_buffer.getvalue()
        if output_text.strip():
            self.terminal_output.appendPlainText(output_text)
