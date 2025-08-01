from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QCheckBox, QHBoxLayout
from PyQt6.QtCore import Qt


class FilterWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Options")
        self.setFixedSize(400, 500)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        layout = QVBoxLayout(self)

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

        # --- Tags Tab ---
        tags_tab = QWidget()
        tags_layout = QVBoxLayout(tags_tab)
        for tag in ["Chat", "Instruct", "Code", "Fun"]:
            cb = QCheckBox(tag)
            cb.setStyleSheet("color: white;")
            tags_layout.addWidget(cb)
        self.tabs.addTab(tags_tab, "Tags")

        # --- Company Tab ---
        company_tab = QWidget()
        company_layout = QVBoxLayout(company_tab)
        for company in ["DeepSeek", "Mistral", "Hermes", "Llama", "Phi"]:
            cb = QCheckBox(company)
            cb.setStyleSheet("color: white;")
            company_layout.addWidget(cb)
        self.tabs.addTab(company_tab, "Company")

        # --- Size Tab ---
        size_tab = QWidget()
        size_layout = QVBoxLayout(size_tab)
        for size in ["Small", "Medium", "Large"]:
            cb = QCheckBox(size)
            cb.setStyleSheet("color: white;")
            size_layout.addWidget(cb)
        self.tabs.addTab(size_tab, "Size")

        layout.addWidget(self.tabs)
