"""
Node Templates - Optimized pre-built templates
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QComboBox, QLabel, QTextEdit, QVBoxLayout, QWidget


class NodeTemplate:
    def __init__(self, name, description, code_template, category="General"):
        self.name = name
        self.description = description
        self.code_template = code_template
        self.category = category


class NodeTemplateManager:
    def __init__(self):
        self.templates = self._load_default_templates()
        self._category_cache = None

    def _load_default_templates(self):
        """Load optimized default templates"""
        return [
            NodeTemplate(
                name="Text Processor",
                description="Process and transform text data",
                code_template="def process(input_data):\n    return input_data.upper()",
                category="Data Processing",
            ),
            NodeTemplate(
                name="Simple Calculator",
                description="Basic arithmetic operations",
                code_template="def calculate(a, b, operation):\n    if operation == 'add':\n        return a + b\n    elif operation == 'subtract':\n        return a - b\n    return 0",
                category="Math",
            ),
        ]

    def get_templates_by_category(self, category):
        """Get templates filtered by category - optimized"""
        return [t for t in self.templates if t.category == category]

    def get_all_categories(self):
        """Get all available categories - cached"""
        if self._category_cache is None:
            self._category_cache = list({t.category for t in self.templates})
        return self._category_cache

    def get_template_by_name(self, name):
        """Get template by name - optimized"""
        return next((t for t in self.templates if t.name == name), None)


class NodeTemplateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = NodeTemplateManager()
        self._current_templates = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Minimalist title
        title = QLabel("Templates")
        title.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Category selector
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.addItems(self.template_manager.get_all_categories())
        self.category_combo.currentTextChanged.connect(self.filter_templates)
        layout.addWidget(self.category_combo)

        # Template list - optimized
        self.template_list = QTextEdit()
        self.template_list.setReadOnly(True)
        self.template_list.setMaximumHeight(150)
        self.template_list.setStyleSheet("font-family: 'Consolas'; font-size: 11px;")
        layout.addWidget(self.template_list)

        self.setLayout(layout)
        self.filter_templates()

    def filter_templates(self):
        """Optimized template filtering"""
        category = self.category_combo.currentText()

        if category == "All":
            self._current_templates = self.template_manager.templates
        else:
            self._current_templates = self.template_manager.get_templates_by_category(
                category
            )

        # Build template text efficiently
        template_text = "\n".join(
            f"• {t.name} ({t.category})\n  {t.description}"
            for t in self._current_templates
        )

        self.template_list.setPlainText(template_text)

    def get_selected_template(self):
        """Get currently selected template"""
        return self._current_templates[0] if self._current_templates else None
