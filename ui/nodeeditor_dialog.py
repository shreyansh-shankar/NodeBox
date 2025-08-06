# ui/node_editor.py
from PyQt6.QtWidgets import ( #type: ignore
    QDialog, QLabel, QLineEdit, QTextEdit, QListWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt #type: ignore

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
        self.resize(1200, 800)

        # Inputs: list of variable names (strings)
        self.inputs = inputs or []  # list[str]

        # Result stored after accept
        self.result_data = None

        # --- UI widgets ---
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        for v in self.inputs:
            self.inputs_list.addItem(str(v))

        self.code_edit = QTextEdit()
        # Prefill code if node provides stored code (optional attr 'code')
        existing_code = initial_code if initial_code else getattr(node, "code", "")
        self.code_edit.setPlainText(existing_code)

        self.outputs_edit = QTextEdit()
        # If node already has outputs metadata, show them
        existing_outputs = getattr(node, "output_vars", None)
        if existing_outputs:
            if isinstance(existing_outputs, (list, tuple)):
                self.outputs_edit.setText(", ".join(existing_outputs))
            else:
                self.outputs_edit.setText(str(existing_outputs))

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.on_save)
        self.button_box.rejected.connect(self.reject)

        # Layouts
        form = QFormLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Available Inputs"))
        left_layout.addWidget(self.inputs_list)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Python Code"))
        right_layout.addWidget(self.code_edit)
        right_layout.addWidget(QLabel("Output variable names"))
        right_layout.addWidget(self.outputs_edit)

        # Main layout: inputs on left (narrow), code on right (wide)
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget, 1)
        main_layout.addLayout(right_layout, 2)

        outer = QVBoxLayout(self)
        outer.addLayout(main_layout)
        outer.addWidget(self.button_box)

        # Inputs list background
        self.inputs_list.setFixedWidth(300)
        self.inputs_list.setFixedHeight(1000)
        self.inputs_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
            }
        """)

        # Code editor background
        self.code_edit.setFixedWidth(900)
        self.code_edit.setFixedHeight(700)
        self.code_edit.setStyleSheet("""
            QTextEdit {
                background-color: #151515;
                color: #d4d4d4;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
                border: 1px solid #444444;
            }
        """)

        # Outputs edit background
        # self.outputs_edit.setReadOnly(True)
        self.outputs_edit.setFixedWidth(900)
        self.outputs_edit.setFixedHeight(165)
        self.outputs_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
            }
        """)

    def on_save(self):
        code = self.code_edit.toPlainText()
        outputs_raw = self.outputs_edit.text().strip()

        # parse outputs: split by comma, strip spaces; ignore empty names
        outputs = [o.strip() for o in outputs_raw.split(",") if o.strip()]

        # Prepare result dict
        self.result_data = {
            "code": code,
            "outputs": outputs,
        }

        self.accept()
