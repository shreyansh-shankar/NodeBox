"""
Optimized Enhanced Main Window - Professional UI with white Feather icons
"""

import json
import os
from PyQt6.QtCore import QTimer

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from browsemodels_manager.browsemodel_window import BrowseModelsWindow
from ui.newautomation_window import NewAutomationWindow
from ui.placeholder_widget import PlaceholderWidget
from utils.paths import AUTOMATIONS_DIR, resource_path
from utils.screen_manager import ScreenManager
from services import OllamaInstaller

class EnhancedMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeBox - Visual Automation Platform")

        x, y, width, height = ScreenManager.get_main_window_geometry()
        self.setGeometry(x, y, width, height)

        self.apply_theme()

        self._feature_widgets = {}
        self._loaded_tabs = set()

        # # Ollama indicator state (string)
        # self._ollama_state = "unknown"

        self.ollama_installer = OllamaInstaller()
        self.ollama_installer.progress_updated.connect(self.update_ollama_indicator)
        self.ollama_installer.download_progress.connect(self.update_download_progress)
        self.ollama_installer.installation_complete.connect(self.on_installation_complete)

        self.init_ui()
        self.setup_connections()
        self.setup_lazy_loading()

    def apply_theme(self):
        """Apply modern dark theme"""
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }

            QMenuBar {
                background-color: #2d2d30;
                color: #e0e0e0;
                border-bottom: 1px solid #3e3e42;
                padding: 4px;
            }

            QMenuBar::item {
                padding: 8px 14px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background-color: #3e3e42;
            }

            QStatusBar {
                background-color: #2d2d30;
                color: #a0a0a0;
                border-top: 1px solid #3e3e42;
            }

            QTabWidget::pane {
                border: 1px solid #3e3e42;
                border-radius: 4px;
                background-color: #252526;
            }

            QTabBar::tab {
                background-color: #2d2d30;
                color: #a0a0a0;
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                font-weight: 500;
            }

            QTabBar::tab:selected {
                background-color: #252526;
                color: #ffffff;
                border-bottom: 2px solid #007acc;
            }

            QTabBar::tab:hover:!selected {
                background-color: #3e3e42;
            }
        """
        )

    def get_icon(self, icon_name):
        """Get white icon from assets"""
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Create menu bar (but place it inside a top_bar alongside the indicator)
        self.create_menu_bar()

        # top_bar holds the menu bar (left) and the ollama indicator (right)
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(8)
        top_bar.setLayout(top_bar_layout)

        # Add menu bar (left)
        top_bar_layout.addWidget(self.menu_bar)

        # Add stretch then the indicator so it sticks to the right
        top_bar_layout.addStretch()

        # Ollama indicator label (top-right)
        self.ollama_indicator = QLabel()
        self.ollama_indicator.setObjectName("ollamaIndicator")
        self.ollama_indicator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ollama_indicator.setMinimumWidth(140)
        self.ollama_indicator.setMinimumHeight(28)
        self.ollama_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ollama_indicator.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        top_bar_layout.addWidget(self.ollama_indicator)

        main_layout.addWidget(top_bar)

        # Status bar (bottom)
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        self.tab_widget = QTabWidget()
        self.tab_widget.setMovable(True)
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_home_tab()
        self.create_templates_tab()
        self.create_scheduler_tab()
        self.create_debug_tab()
        self.create_performance_tab()
        self.create_export_import_tab()
        self.create_models_tab()

        main_layout.addWidget(self.status_bar)

        # Extra stylesheet for the indicator (local)
        # Keep styling consistent with the app palette. Colors updated in update_ollama_indicator.
        self.ollama_indicator.setStyleSheet(
            """
            QLabel#ollamaIndicator {
                background-color: transparent;
                font-size: 11px;
                font-weight: 600;
                padding: 0px;
                margin-right: 8px;
            }
            """
        )
        QTimer.singleShot(3000, self.show_ollama_checking)



    def create_menu_bar(self):
        """Create menu bar with white icons"""
        self.menu_bar = QMenuBar()

        # File menu
        file_menu = self.menu_bar.addMenu("File")

        new_action = QAction(self.get_icon("plus"), " New Automation", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_automation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        import_action = QAction(self.get_icon("download"), " Import Workflows", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.show_import_dialog)
        file_menu.addAction(import_action)

        export_action = QAction(self.get_icon("upload"), " Export Workflows", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.show_export_dialog)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction(self.get_icon("x"), " Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = self.menu_bar.addMenu("Tools")

        templates_action = QAction(self.get_icon("file-text"), " Node Templates", self)
        templates_action.triggered.connect(lambda: self.switch_to_tab(" Templates"))
        tools_menu.addAction(templates_action)

        scheduler_action = QAction(self.get_icon("clock"), " Workflow Scheduler", self)
        scheduler_action.triggered.connect(lambda: self.switch_to_tab(" Scheduler"))
        tools_menu.addAction(scheduler_action)

        debug_action = QAction(self.get_icon("terminal"), " Debug Console", self)
        debug_action.triggered.connect(lambda: self.switch_to_tab(" Debug"))
        tools_menu.addAction(debug_action)

        performance_action = QAction(
            self.get_icon("activity"), " Performance Monitor", self
        )
        performance_action.triggered.connect(lambda: self.switch_to_tab(" Performance"))
        tools_menu.addAction(performance_action)

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")

        about_action = QAction(self.get_icon("info"), " About NodeBox", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # ---- Ollama indicator helpers ----
    def update_ollama_indicator(self, state: str, message: str = ""):
        """
        Update the top-right Ollama indicator with progress.
        
        Extended states: "checking", "found", "installing", "downloading", 
                        "not_found", "ready", "error", "cancelled", "hidden"
        """
        state = (state or "").lower()
        self._ollama_state = state

        mapping = {
            "checking": ("Checking Ollama...", "#007acc"),
            "found": ("Ollama found", "#0f9d4a"),
            "installing": ("Installing Ollama...", "#f39c12"),
            "downloading": (f"Downloading {message}", "#f39c12"),
            "not_found": ("Ollama not found", "#c0392b"),
            "ready": ("Ollama ready", "#0f9d4a"),
            "error": (f"Error: {message}", "#c0392b"),
            "cancelled": ("Installation cancelled", "#a0a0a0"),
            "hidden": ("", "transparent"),
        }

        text, color = mapping.get(state, (state.replace("_", " ").title(), "#a0a0a0"))

        if state == "hidden":
            self.ollama_indicator.setText("")
            self.ollama_indicator.setVisible(False)
            return
        else:
            self.ollama_indicator.setVisible(True)

        self.ollama_indicator.setText(text)

        # Update text color; keep background transparent
        style = f"color: {color};" if color != "transparent" else "color: #e0e0e0;"
        base = """
            QLabel#ollamaIndicator {
                background-color: transparent;
                font-size: 11px;
                font-weight: 600;
            }
        """
        self.ollama_indicator.setStyleSheet(base + style)

    def update_download_progress(self, percentage: int):
        """Update indicator with download progress"""
        if self._ollama_state == "installing":
            self.ollama_indicator.setText(f"Downloading... {percentage}%")

    def on_installation_complete(self, status: str):
        """Handle installation completion"""
        if status == "ready":
            self.status_bar.showMessage("Ollama installed successfully")
        elif status == "error":
            self.status_bar.showMessage("Ollama installation failed")
        elif status == "cancelled":
            self.status_bar.showMessage("Ollama installation cancelled")

    def show_ollama_checking(self):
        """Check Ollama and start background installation if needed"""
        if self.ollama_installer.check_ollama():
            self.update_ollama_indicator("found")
        else:
            self.show_ollama_download_popup()

    def show_ollama_download_popup(self):
        """Show download confirmation dialog"""
        reply = QMessageBox.question(
            self,
            "Ollama Not Found",
            "Ollama is not installed on your system.\nWould you like to download and install it now?\n\nThis will happen in the background.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Start background installation
            self.ollama_installer.download_ollama_background()
        else:
            self.update_ollama_indicator("not_found")

    # Add a method to cancel installation if needed
    def cancel_ollama_installation(self):
        """Cancel ongoing Ollama installation"""
        if self.ollama_installer.is_installing():
            self.ollama_installer.cancel_installation()

    # Update closeEvent to cancel installation if window is closed
    def closeEvent(self, event):
        # Cancel any ongoing Ollama installation
        if hasattr(self, 'ollama_installer') and self.ollama_installer.is_installing():
            self.ollama_installer.cancel_installation()
            # Wait a moment for cleanup
            import time
            time.sleep(0.5)

        if "performance" in self._feature_widgets:
            self._feature_widgets["performance"].stop_monitoring()

        for widget in self._feature_widgets.values():
            if hasattr(widget, "cleanup"):
                widget.cleanup()

        event.accept()
    # ---- rest of your existing methods unchanged (kept below for completeness) ----

    def create_home_tab(self):
        """Create the home tab"""
        home_widget = QWidget()
        home_widget.setStyleSheet("background-color: #252526;")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("NodeBox")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        subtitle = QLabel("Visual Automation Platform")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #a0a0a0; margin-bottom: 16px;")
        layout.addWidget(subtitle)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        create_button = QPushButton("  Create New Automation")
        create_button.setIcon(self.get_icon("plus-circle"))
        create_button.setFont(QFont("Segoe UI", 12))
        create_button.setMinimumHeight(44)
        create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_button.setStyleSheet(
            """
            QPushButton {
                padding: 12px 24px;
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
        """
        )
        create_button.clicked.connect(self.create_new_automation)
        actions_layout.addWidget(create_button)

        browse_button = QPushButton("  Browse Models")
        browse_button.setIcon(self.get_icon("package"))
        browse_button.setFont(QFont("Segoe UI", 12))
        browse_button.setMinimumHeight(44)
        browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_button.setStyleSheet(
            """
            QPushButton {
                padding: 12px 24px;
                background-color: #0d7d3a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0f9d4a;
            }
            QPushButton:pressed {
                background-color: #0b6d32;
            }
        """
        )
        browse_button.clicked.connect(self.open_browse_models_window)
        actions_layout.addWidget(browse_button)

        layout.addLayout(actions_layout)

        list_label = QLabel("Your Automations")
        list_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        list_label.setStyleSheet("color: #ffffff; margin-top: 16px;")
        layout.addWidget(list_label)

        self.automation_list = QListWidget()
        self.automation_list.setFont(QFont("Segoe UI", 12))
        self.automation_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 8px;
                background-color: #1e1e1e;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2d2d30;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QListWidget::item:hover {
                background-color: #2d2d30;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
                color: #ffffff;
            }
        """
        )
        layout.addWidget(self.automation_list)

        help_label = QLabel("Double-click to edit an automation")
        help_label.setFont(QFont("Segoe UI", 11))
        help_label.setStyleSheet("color: #888888; margin-top: 8px;")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_label)

        self.load_automations()

        home_widget.setLayout(layout)
        self.tab_widget.addTab(home_widget, self.get_icon("home"), " Home")

    def create_templates_tab(self):
        placeholder = PlaceholderWidget("Node Templates")
        self.tab_widget.addTab(placeholder, self.get_icon("file-text"), " Templates")

    def create_scheduler_tab(self):
        placeholder = PlaceholderWidget("Workflow Scheduler")
        self.tab_widget.addTab(placeholder, self.get_icon("clock"), " Scheduler")

    def create_debug_tab(self):
        placeholder = PlaceholderWidget("Debug Console")
        self.tab_widget.addTab(placeholder, self.get_icon("terminal"), " Debug")

    def create_performance_tab(self):
        placeholder = PlaceholderWidget("Performance Monitor")
        self.tab_widget.addTab(placeholder, self.get_icon("activity"), " Performance")

    def create_export_import_tab(self):
        placeholder = PlaceholderWidget("Export/Import Manager")
        self.tab_widget.addTab(placeholder, self.get_icon("package"), " Export/Import")

    def create_models_tab(self):
        """Create local models tab - lazy loaded"""
        placeholder = PlaceholderWidget("Local Models Manager")
        self.tab_widget.addTab(placeholder, self.get_icon("database"), " Local Models")

    def setup_connections(self):
        self.automation_list.itemDoubleClicked.connect(self.edit_automation)
        self.automation_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.automation_list.customContextMenuRequested.connect(
            self.show_automation_context_menu
        )

    def setup_lazy_loading(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index < 0 or index in self._loaded_tabs:
            return

        tab_text = self.tab_widget.tabText(index)

        if "Templates" in tab_text:
            self._load_templates_tab(index)
        elif "Scheduler" in tab_text:
            self._load_scheduler_tab(index)
        elif "Debug" in tab_text:
            self._load_debug_tab(index)
        elif "Performance" in tab_text:
            self._load_performance_tab(index)
        elif "Export/Import" in tab_text:
            self._load_export_import_tab(index)
        elif "Local Models" in tab_text:
            self._load_models_tab(index)

        self._loaded_tabs.add(index)

    def _load_templates_tab(self, index):
        from features.node_templates import NodeTemplateWidget

        self.tab_widget.currentChanged.disconnect()
        widget = NodeTemplateWidget()
        self._feature_widgets["templates"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(
            index, widget, self.get_icon("file-text"), " Templates"
        )
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_scheduler_tab(self, index):
        from features.workflow_scheduler import WorkflowScheduler

        self.tab_widget.currentChanged.disconnect()
        widget = WorkflowScheduler()
        widget.schedule_triggered.connect(self.run_scheduled_automation)
        self._feature_widgets["scheduler"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("clock"), " Scheduler")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_debug_tab(self, index):
        from features.debug_console import DebugConsole

        self.tab_widget.currentChanged.disconnect()
        widget = DebugConsole()
        self._feature_widgets["debug"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("terminal"), " Debug")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_performance_tab(self, index):
        from features.performance_monitor import PerformanceMonitor

        self.tab_widget.currentChanged.disconnect()
        widget = PerformanceMonitor()
        self._feature_widgets["performance"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(
            index, widget, self.get_icon("activity"), " Performance"
        )
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_export_import_tab(self, index):
        from features.export_import import ExportImportManager

        self.tab_widget.currentChanged.disconnect()
        widget = ExportImportManager()
        self._feature_widgets["export_import"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(
            index, widget, self.get_icon("package"), " Export/Import"
        )
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_models_tab(self, index):
        """Load the actual models manager widget"""
        from features.model_manager import ModelManagerWidget

        self.tab_widget.currentChanged.disconnect()
        widget = ModelManagerWidget()
        self._feature_widgets["models"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(
            index, widget, self.get_icon("database"), " Local Models"
        )
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def load_automations(self):
        self.automation_list.clear()
        self.status_bar.showMessage("Loading automations...")

        automations = self.fetch_automations()

        if not automations:
            item = QListWidgetItem("No automations found. Create your first!")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setFont(QFont("Segoe UI", 12))
            self.automation_list.addItem(item)
            self.status_bar.showMessage("Ready")
            return

        for name in automations:
            item = QListWidgetItem(self.get_icon("file"), f" {name}")
            item.setFont(QFont("Segoe UI", 12))
            self.automation_list.addItem(item)

        self.status_bar.showMessage(f"Loaded {len(automations)} automation(s)")

    def fetch_automations(self):
        if not AUTOMATIONS_DIR.exists():
            return []

        automations = []
        for file_path in AUTOMATIONS_DIR.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    automations.append(data.get("name", file_path.stem))
            except (json.JSONDecodeError, IOError):
                continue

        return sorted(automations)

    def create_new_automation(self):
        self.status_bar.showMessage("Creating new automation...")
        self.new_automation_window = NewAutomationWindow(main_window=self)
        self.new_automation_window.show()

    def on_editor_closed(self):
        self.show()
        self.load_automations()

    def edit_automation(self, item):
        automation_name = item.text().strip()

        if "No automations found" in automation_name:
            return

        from automation_manager.node_editor_window import NodeEditorWindow

        self.status_bar.showMessage(f"Opening: {automation_name}")

        editor = NodeEditorWindow(automation_name)
        editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        editor.closed.connect(self.on_editor_closed, Qt.ConnectionType.UniqueConnection)

        editor.show()
        self.hide()

        self.editor_window = editor

    def open_browse_models_window(self):
        self.status_bar.showMessage("Opening Browse Models...")
        self.browse_window = BrowseModelsWindow()
        self.browse_window.show()

    def run_scheduled_automation(self, automation_name):
        self.status_bar.showMessage(f"Running: {automation_name}")
        print(f"Running scheduled automation: {automation_name}")

    def show_import_dialog(self):
        self.tab_widget.setCurrentIndex(5)
        self.status_bar.showMessage("Import workflows")

    def show_export_dialog(self):
        self.tab_widget.setCurrentIndex(5)
        self.status_bar.showMessage("Export workflows")

    def show_automation_context_menu(self, position):
        """Show context menu for automation items."""
        item = self.automation_list.itemAt(position)
        if not item:
            return

        automation_name = item.text().strip()
        if "No automations found" in automation_name:
            return

        menu = QMenu(self)

        # Rename action
        rename_action = QAction("Rename Automation", self)
        rename_action.triggered.connect(lambda: self.rename_automation(automation_name))
        menu.addAction(rename_action)

        # Duplicate action
        duplicate_action = QAction("Duplicate Automation", self)
        duplicate_action.triggered.connect(
            lambda: self.duplicate_automation(automation_name)
        )
        menu.addAction(duplicate_action)

        menu.addSeparator()  # Separator before destructive actions

        # Delete action
        delete_action = QAction("Delete Automation", self)
        delete_action.triggered.connect(lambda: self.delete_automation(automation_name))
        menu.addAction(delete_action)

        menu.exec(self.automation_list.mapToGlobal(position))

    def rename_automation(self, current_name):
        """Rename an automation with input dialog."""
        new_name, ok = QInputDialog.getText(
            self, "Rename Automation", "Enter new automation name:", text=current_name
        )

        if not ok or not new_name.strip() or new_name.strip() == current_name:
            return

        new_name = new_name.strip()

        # Check for duplicate names
        existing_automations = self.fetch_automations()
        if new_name in existing_automations:
            QMessageBox.warning(
                self,
                "Duplicate Name",
                f"An automation named '{new_name}' already exists.",
            )
            return

        # Perform the rename
        try:
            self._rename_automation_file(current_name, new_name)
            self.status_bar.showMessage(f"Renamed '{current_name}' to '{new_name}'")
            self.load_automations()
        except Exception as e:
            QMessageBox.critical(
                self, "Rename Failed", f"Failed to rename automation:\n{str(e)}"
            )

    def delete_automation(self, automation_name):
        """Delete an automation with confirmation."""
        reply = QMessageBox.question(
            self,
            "Delete Automation",
            f"Are you sure you want to delete '{automation_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Perform the deletion
        try:
            self._delete_automation_file(automation_name)
            self.status_bar.showMessage(f"Deleted automation '{automation_name}'")
            self.load_automations()
        except Exception as e:
            QMessageBox.critical(
                self, "Delete Failed", f"Failed to delete automation:\n{str(e)}"
            )

    def _rename_automation_file(self, old_name, new_name):
        """Rename automation file on disk and update internal name."""
        old_file = AUTOMATIONS_DIR / f"{old_name}.json"
        new_file = AUTOMATIONS_DIR / f"{new_name}.json"

        if not old_file.exists():
            raise FileNotFoundError(f"Automation file not found: {old_file}")

        # Read current data
        with open(old_file, "r") as f:
            data = json.load(f)

        # Update the name in the JSON data
        data["name"] = new_name

        # Write to new file
        with open(new_file, "w") as f:
            json.dump(data, f, indent=4)

        # Remove old file
        old_file.unlink()

    def _delete_automation_file(self, automation_name):
        """Delete automation file from disk."""
        file_path = AUTOMATIONS_DIR / f"{automation_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Automation file not found: {file_path}")

        file_path.unlink()

    def duplicate_automation(self, automation_name):
        """Duplicate an automation with a new name."""
        base_name = f"{automation_name} Copy"
        counter = 1
        new_name = base_name

        # Find a unique name
        existing_automations = self.fetch_automations()
        while new_name in existing_automations:
            counter += 1
            new_name = f"{base_name} {counter}"

        # Get confirmation from user
        new_name, ok = QInputDialog.getText(
            self, "Duplicate Automation", "Enter name for duplicate:", text=new_name
        )

        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()

        # Check for duplicate names again (in case user changed it)
        if new_name in existing_automations:
            QMessageBox.warning(
                self,
                "Duplicate Name",
                f"An automation named '{new_name}' already exists.",
            )
            return

        # Perform the duplication
        try:
            self._duplicate_automation_file(automation_name, new_name)
            self.status_bar.showMessage(
                f"Duplicated '{automation_name}' as '{new_name}'"
            )
            self.load_automations()
        except Exception as e:
            QMessageBox.critical(
                self, "Duplicate Failed", f"Failed to duplicate automation:\n{str(e)}"
            )

    def _duplicate_automation_file(self, source_name, target_name):
        """Duplicate automation file with new name."""
        source_file = AUTOMATIONS_DIR / f"{source_name}.json"
        target_file = AUTOMATIONS_DIR / f"{target_name}.json"

        if not source_file.exists():
            raise FileNotFoundError(f"Source automation file not found: {source_file}")

        # Read source data
        with open(source_file, "r") as f:
            data = json.load(f)

        # Update the name in the JSON data
        data["name"] = target_name

        # Write to target file
        with open(target_file, "w") as f:
            json.dump(data, f, indent=4)

    def show_about(self):
        about_text = """
        <div style='text-align: center;'>
            <h2 style='color: #0e639c;'>NodeBox</h2>
            <p style='color: #888;'>Visual Automation Platform</p>
            <p><b>Version:</b> 2.0</p>
            <hr style='border: 1px solid #3e3e42; margin: 16px 0;'>
            <p style='text-align: left;'><b>Features:</b></p>
            <ul style='text-align: left; color: #a0a0a0;'>
                <li>Node Templates</li>
                <li>Workflow Scheduler</li>
                <li>Debug Console</li>
                <li>Performance Monitor</li>
                <li>Export/Import System</li>
                <li>Local Models Manager</li>
            </ul>
            <p style='color: #888; font-size: 12px;'>Built with Python & PyQt6</p>
        </div>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About NodeBox")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setStyleSheet(
            """
            QMessageBox {
                background-color: #252526;
            }
            QLabel {
                color: #e0e0e0;
                min-width: 400px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """
        )
        msg_box.exec()

    def closeEvent(self, event):
        if "performance" in self._feature_widgets:
            self._feature_widgets["performance"].stop_monitoring()

        for widget in self._feature_widgets.values():
            if hasattr(widget, "cleanup"):
                widget.cleanup()

        event.accept()

    def find_tab_index_by_text(self, text: str) -> int:
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == text:
                return i
        return -1

    def switch_to_tab(self, text: str):
        idx = self.find_tab_index_by_text(text)
        if idx != -1:
            self.tab_widget.setCurrentIndex(idx)
        else:
            self.status_bar.showMessage(f"Tab '{text}' not found")
