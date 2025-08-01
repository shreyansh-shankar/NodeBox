from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QCheckBox, QHBoxLayout, QPushButton, QScrollArea, QFrame
from PyQt6.QtCore import Qt

class FilterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Options")
        self.setFixedSize(306, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #2e2e2e;
                color: white;
                padding: 8px;
                min-width: 80px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #3e3e3e;
            }
        """)

        def create_scrollable_tab(items):
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            content_widget = QFrame()
            content_layout = QVBoxLayout(content_widget)
            for item in items:
                cb = QCheckBox(item)
                cb.setStyleSheet("color: white;")
                content_layout.addWidget(cb)
            content_layout.addStretch()

            scroll_area.setWidget(content_widget)
            return scroll_area

        # Tabs
        self.tabs.addTab(create_scrollable_tab(["Chat", "Instruct", "Code", "Fun"]), "Tags")
        self.tabs.addTab(create_scrollable_tab(["DeepSeek", "Mistral", "Hermes", "Llama", "Phi"]), "Company")
        self.tabs.addTab(create_scrollable_tab(["Small", "Medium", "Large"]), "Size")

        main_layout.addWidget(self.tabs)

        # Buttons at the bottom
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        apply_btn.clicked.connect(self.apply_filters)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        close_btn.clicked.connect(self.close)

        button_layout.addWidget(apply_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)

    def apply_filters(self):
        # You can insert filter logic here if needed
        self.close()
