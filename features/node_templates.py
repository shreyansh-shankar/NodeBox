"""
Node Templates - Optimized pre-built templates
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QComboBox, QLabel, QTextEdit, QVBoxLayout, QWidget


class NodeTemplate:
    __slots__ = ["name", "description", "code_template", "category"]

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
                category="Data Processing",
                code_template="""def process(input_data):
    # Process text input
    result = input_data.upper()
    return result""",
            ),
            NodeTemplate(
                name="File Watcher",
                description="Monitor file system changes",
                category="File Operations",
                code_template="""import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def watch_directory(path):
    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory:
                print(f"File modified: {event.src_path}")

    observer = Observer()
    observer.schedule(Handler(), path, recursive=True)
    observer.start()
    return observer""",
            ),
            NodeTemplate(
                name="HTTP Request",
                description="Make HTTP requests to APIs",
                category="Web",
                code_template=r"""import requests
import json

def make_request(url, method="GET", data=None, headers=None):
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)

        return {
            "status_code": response.status_code,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {"error": str(e)}""",
            ),
            NodeTemplate(
                name="Data Validator",
                description="Validate and clean data",
                category="Data Processing",
                code_template=r"""import re
import json

def validate_data(data, validation_rules):
    errors = []

    for field, rules in validation_rules.items():
        if field not in data:
            errors.append(f"Missing field: {field}")
            continue

        value = data[field]

        if "required" in rules and not value:
            errors.append(f"{field} is required")

        if "type" in rules:
            if rules["type"] == "email" and not re.match(r"[^@]+@[^@]+\.[^@]+", str(value)):
                errors.append(f"{field} must be a valid email")
            elif rules["type"] == "number" and not str(value).replace('.', '').isdigit():
                errors.append(f"{field} must be a number")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "cleaned_data": data
    }""",
            ),
            NodeTemplate(
                name="Database Connector",
                description="Connect to databases",
                category="Database",
                code_template="""import sqlite3
import json

def connect_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        return {"error": str(e)}

def execute_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        else:
            conn.commit()
            return {"rows_affected": cursor.rowcount}
    except Exception as e:
        return {"error": str(e)}""",
            ),
            NodeTemplate(
                name="Email Sender",
                description="Send emails programmatically",
                category="Communication",
                code_template="""import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(smtp_server, port, username, password, to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        text = msg.as_string()
        server.sendmail(username, to_email, text)
        server.quit()

        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}""",
            ),
        ]
        return self.templates

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
