from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QMessageBox, QHBoxLayout, QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
import os, json

from ui.canvas_widget import CanvasWidget

class NodeEditorWindow(QMainWindow):

    closed = pyqtSignal()

    def __init__(self, automation_name=None):
        super().__init__()
        self.automation_name = automation_name
        self.setWindowTitle(f"Automation: {automation_name}")
        self.setMinimumSize(1600, 900)
        self.setStyleSheet("background-color: #2a2a2a; color: white;")

        layout = QVBoxLayout(self)
        label = QLabel(f"Node Editor for: {automation_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Load existing automation data
        self.automation_data = self.load_automation()
        print("Loaded automation data:", self.automation_data)

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Editing Automation: {self.automation_name}")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # === MAIN LAYOUT ===
        main_layout = QHBoxLayout(central_widget)

        # === SIDEBAR (Left Panel) ===
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #202020;")
        sidebar_layout = QVBoxLayout(sidebar)

        # Search Bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search nodes...")
        search_bar.setStyleSheet("padding: 5px; font-size: 14px; background-color: #333333")
        sidebar_layout.addWidget(search_bar)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # === RIGHT SIDE: Label + Canvas ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Label
        label = QLabel(f"Editing Automation: {self.automation_name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        right_layout.addWidget(label)

        # Canvas
        self.canvas_widget = CanvasWidget()
        right_layout.addWidget(self.canvas_widget, stretch=1)

        main_layout.addWidget(right_panel, stretch=1)


    def load_automation(self):
        path = os.path.expanduser(f"~/.nodebox/automations/{self.automation_name}.json")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump({"nodes": [], "connections": []}, f, indent=2)
        
        try:
            with open(path, 'r+') as f:
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
                    # File is empty or corrupted
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
