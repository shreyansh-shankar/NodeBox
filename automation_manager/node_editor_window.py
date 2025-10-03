import json
import os


from PyQt6.QtCore import QSize, Qt, pyqtSignal  # type: ignore
from PyQt6.QtGui import QIcon  # type: ignore
from PyQt6.QtWidgets import (  # type: ignore
    QApplication,  # ← ADD THIS IMPORT
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


from automation_manager.node_pallete import NodePaletteItem
from canvasmanager.canvas_widget import CanvasWidget
from predefined.registry import PredefinedNodeRegistry
from utils.paths import resource_path
from utils.screen_manager import ScreenManager



class NodeEditorWindow(QMainWindow):
    closed = pyqtSignal()


    def __init__(self, automation_name=None):
        super().__init__()
        self.automation_name = automation_name
        self.setWindowTitle(f"Automation: {automation_name}")


        # Use dynamic window sizing based on screen resolution
        x, y, width, height = ScreenManager.get_editor_window_geometry()
        self.setGeometry(x, y, width, height)


        # Set minimum size to be at least the minimum calculated size
        min_width, min_height = ScreenManager.calculate_window_size(
            width_percentage=0.6,  # Smaller percentage for minimum
            height_percentage=0.6,
            min_width=1000,
            min_height=700,
        )
        self.setMinimumSize(min_width, min_height)


        self.setStyleSheet("background-color: #2a2a2a; color: white;")


        # Load existing automation data
        self.automation_data = self.load_automation()


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
        search_bar.setStyleSheet(
            "padding: 5px; font-size: 14px; background-color: #333333"
        )
        sidebar_layout.addWidget(search_bar)


        # Predefined Nodes Section
        predefined_label = QLabel("Predefined Nodes")
        predefined_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 5px 5px 5px; color: #aaaaaa;"
        )
        sidebar_layout.addWidget(predefined_label)


        # Add all registered predefined nodes
        predefined_nodes = PredefinedNodeRegistry.get_node_names()
        for node_name in predefined_nodes:
            sidebar_layout.addWidget(NodePaletteItem(node_name, sidebar))


        # Custom Nodes Section
        custom_label = QLabel("Custom Nodes")
        custom_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 5px 5px 5px; color: #aaaaaa;"
        )
        sidebar_layout.addWidget(custom_label)


        nodes = ["Custom Node"]
        for n in nodes:
            sidebar_layout.addWidget(NodePaletteItem(n, sidebar))


        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)


        # === RIGHT SIDE: Label + Canvas ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)


        # Title row (label + play button)
        title_row = QHBoxLayout()


        label = QLabel(f"Editing Automation: {self.automation_name}")
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")


        title_row.addWidget(label)
        title_row.addStretch()


        # Play button (SVG)
        play_button = QPushButton()
        svg_path = resource_path("assets/icons/play.svg")
        play_button.setIcon(QIcon(svg_path))
        play_button.setIconSize(QSize(28, 28))
        play_button.setFixedSize(40, 40)
        play_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """
        )


        title_row.addWidget(play_button, alignment=Qt.AlignmentFlag.AlignRight)


        right_layout.addLayout(title_row)


        # Canvas
        self.canvas_widget = CanvasWidget(
            automation_name=self.automation_name, automation_data=self.automation_data
        )
        right_layout.addWidget(self.canvas_widget, stretch=1)


        main_layout.addWidget(right_panel, stretch=1)


        # Store button for later functionality
        self.play_button = play_button
        # Connect to wrapper function instead of direct call
        self.play_button.clicked.connect(self.run_automation_with_cursor)


    def run_automation_with_cursor(self):
        """Run automation with cursor feedback"""
        # Set busy cursor before running
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # Run the automation
            self.canvas_widget.run_all_nodes()
        finally:
            # Restore cursor when done
            QApplication.restoreOverrideCursor()


    def load_automation(self):
        path = os.path.expanduser(f"~/.nodebox/automations/{self.automation_name}.json")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump({"nodes": [], "connections": []}, f, indent=2)


        try:
            with open(path, "r+") as f:
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
