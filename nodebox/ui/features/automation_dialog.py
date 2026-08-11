import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from nodebox.core.paths import AUTOMATIONS_DIR
from nodebox.core.screen import ScreenManager
from nodebox.ui.canvas.dialogs import NodeEditorWindow

_BG_DEEP   = "#0A0C10"
_BG_BASE   = "#0F1117"
_BG_RAISED = "#161922"
_BORDER    = "#1E2538"
_ACCENT    = "#6366F1"
_TEXT      = "#F0F2F8"
_TEXT_SEC  = "#8892B0"
_TEXT_DIM  = "#4A5578"


class NewAutomationWindow(QDialog):
    def __init__(self, main_window=None):
        self.main_window = main_window
        super().__init__()
        self.setWindowTitle("Create New Automation")
        self.setModal(True)

        width, height = ScreenManager.get_dialog_window_size(
            width_percentage=0.3, height_percentage=0.28, min_width=420, min_height=280
        )
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        self.setGeometry(x, y, width, height)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {_BG_DEEP};
                color: {_TEXT};
            }}
        """)

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Gradient header ─────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10132A, stop:0.6 #141830, stop:1 #0E1126);
                border-bottom: 1px solid {_BORDER};
                border-radius: 0;
            }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(28, 16, 28, 16)
        header_layout.setSpacing(3)

        h_title = QLabel("New Automation")
        h_title.setFont(QFont("Poppins", 16, QFont.Weight.Bold))
        h_title.setStyleSheet("color: #F0F2F8; background: transparent; border: none;")
        header_layout.addWidget(h_title)

        h_sub = QLabel("Name your automation workflow to get started")
        h_sub.setFont(QFont("Poppins", 10))
        h_sub.setStyleSheet("color: #8892B0; background: transparent; border: none;")
        header_layout.addWidget(h_sub)

        outer.addWidget(header)

        # ── Body ────────────────────────────────────────────────────
        body = QVBoxLayout()
        body.setContentsMargins(28, 24, 28, 28)
        body.setSpacing(16)

        name_label = QLabel("Automation Name")
        name_label.setFont(QFont("Poppins", 11, QFont.Weight.DemiBold))
        name_label.setStyleSheet(f"color: {_TEXT_SEC}; letter-spacing: 0.3px;")
        body.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Daily CSV Summarizer")
        self.name_input.setFixedHeight(46)
        self.name_input.setFont(QFont("Poppins", 13))
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 16px;
                border-radius: 10px;
                background-color: {_BG_RAISED};
                border: 1px solid {_BORDER};
                color: {_TEXT};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {_ACCENT};
                background-color: #12162A;
            }}
        """)
        self.name_input.returnPressed.connect(self.on_create_button_clicked)
        body.addWidget(self.name_input)

        body.addStretch()

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Poppins", 11, QFont.Weight.DemiBold))
        cancel_btn.setFixedHeight(44)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: {_TEXT_SEC};
                border: 1px solid {_BORDER};
                border-radius: 10px;
                padding: 6px 20px;
            }}
            QPushButton:hover {{
                background-color: #1C2235;
                border-color: {_ACCENT};
                color: {_TEXT};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        create_btn = QPushButton("Create & Open Canvas")
        create_btn.setFont(QFont("Poppins", 11, QFont.Weight.DemiBold))
        create_btn.setFixedHeight(44)
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 6px 24px;
            }}
            QPushButton:hover {{
                background-color: #5153D6;
            }}
            QPushButton:pressed {{
                background-color: #4345B5;
            }}
        """)
        create_btn.clicked.connect(self.on_create_button_clicked)
        btn_row.addWidget(create_btn, stretch=1)

        body.addLayout(btn_row)

        outer.addLayout(body)

    def on_create_button_clicked(self):
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Invalid Input", "Automation name cannot be empty.")
            return

        filename = f"{name}.json"
        file_path = os.path.join(AUTOMATIONS_DIR, filename)

        if os.path.exists(file_path):
            QMessageBox.warning(self, "Duplicate Name", "An automation with this name already exists.")
            return

        try:
            with open(file_path, "w") as f:
                json.dump({}, f, indent=4)

            if self.main_window and hasattr(self.main_window, "load_automations"):
                self.main_window.load_automations()

            self.node_editor = NodeEditorWindow(name)
            self.node_editor.closed.connect(self.reopen_main_window)
            self.node_editor.show()

            if self.main_window:
                self.main_window.close()

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create automation file:\n{str(e)}")

    def reopen_main_window(self):
        if self.main_window:
            self.main_window.show()


__all__ = ["NewAutomationWindow"]
