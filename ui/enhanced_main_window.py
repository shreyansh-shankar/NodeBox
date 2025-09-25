"""
Optimized Enhanced Main Window - Minimalist and efficient
"""
import json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from browsemodels_manager.browsemodel_window import BrowseModelsWindow

# Import optimized features
from ui.newautomation_window import NewAutomationWindow
from ui.placeholder_widget import PlaceholderWidget
from utils.paths import AUTOMATIONS_DIR
from utils.screen_manager import ScreenManager


class EnhancedMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeBox")

        # Use dynamic window sizing based on screen resolution
        x, y, width, height = ScreenManager.get_main_window_geometry()
        self.setGeometry(x, y, width, height)

        # Initialize feature widgets lazily
        self._feature_widgets = {}
        self._loaded_tabs = set()  # Track which tabs have been loaded

        self.init_ui()
        self.setup_connections()
        self.setup_lazy_loading()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Menu bar
        self.create_menu_bar()
        main_layout.addWidget(self.menu_bar)

        # Main content area with tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Home tab
        self.create_home_tab()

        # Node Templates tab
        self.create_templates_tab()

        # Scheduler tab
        self.create_scheduler_tab()

        # Debug Console tab
        self.create_debug_tab()

        # Performance Monitor tab
        self.create_performance_tab()

        # Export/Import tab
        self.create_export_import_tab()

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)

    def create_menu_bar(self):
        """Create menu bar with enhanced options"""
        self.menu_bar = QMenuBar()

        # File menu
        file_menu = self.menu_bar.addMenu("File")

        new_action = QAction("New Automation", self)
        new_action.triggered.connect(self.create_new_automation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        import_action = QAction("Import Workflows", self)
        import_action.triggered.connect(self.show_import_dialog)
        file_menu.addAction(import_action)

        export_action = QAction("Export Workflows", self)
        export_action.triggered.connect(self.show_export_dialog)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = self.menu_bar.addMenu("Tools")

        templates_action = QAction("Node Templates", self)
        templates_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        tools_menu.addAction(templates_action)

        scheduler_action = QAction("Workflow Scheduler", self)
        scheduler_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        tools_menu.addAction(scheduler_action)

        debug_action = QAction("Debug Console", self)
        debug_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        tools_menu.addAction(debug_action)

        performance_action = QAction("Performance Monitor", self)
        performance_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        tools_menu.addAction(performance_action)

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")

        about_action = QAction("About NodeBox", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_home_tab(self):
        """Create the home tab with automation list"""
        home_widget = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("NodeBox - Enhanced Automation Studio")
        title.setFont(QFont("Poppins", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Visual automation platform with advanced features")
        subtitle.setFont(QFont("Poppins", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888;")
        layout.addWidget(subtitle)

        # Quick actions
        actions_layout = QHBoxLayout()

        create_button = QPushButton("Create New Automation")
        create_button.setStyleSheet(
            """
        QPushButton {
            font-family: 'Poppins';
            padding: 12px 20px;
            font-size: 16px;
            background-color: #007acc;
            color: white;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        """
        )
        create_button.clicked.connect(self.create_new_automation)
        actions_layout.addWidget(create_button)

        browse_button = QPushButton("Browse Models")
        browse_button.setStyleSheet(
            """
        QPushButton {
            font-family: 'Poppins';
            padding: 12px 20px;
            font-size: 16px;
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #1e7e34;
        }
        """
        )
        browse_button.clicked.connect(self.open_browse_models_window)
        actions_layout.addWidget(browse_button)

        layout.addLayout(actions_layout)

        # Automation list
        layout.addWidget(QLabel("Your Automations:"))
        self.automation_list = QListWidget()
        self.automation_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px;
                background-color: #2a2a2a;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #007acc;
            }
        """
        )
        layout.addWidget(self.automation_list)

        # Load automations
        self.load_automations()

        home_widget.setLayout(layout)
        self.tab_widget.addTab(home_widget, "Home")

    def create_templates_tab(self):
        """Create node templates tab - lazy loaded"""
        placeholder = PlaceholderWidget("Node Templates")
        self.tab_widget.addTab(placeholder, "Templates")

    def create_scheduler_tab(self):
        """Create workflow scheduler tab - lazy loaded"""
        placeholder = PlaceholderWidget("Workflow Scheduler")
        self.tab_widget.addTab(placeholder, "Scheduler")

    def create_debug_tab(self):
        """Create debug console tab - lazy loaded"""
        placeholder = PlaceholderWidget("Debug Console")
        self.tab_widget.addTab(placeholder, "Debug")

    def create_performance_tab(self):
        """Create performance monitor tab - lazy loaded"""
        placeholder = PlaceholderWidget("Performance Monitor")
        self.tab_widget.addTab(placeholder, "Performance")

    def create_export_import_tab(self):
        """Create export/import tab - lazy loaded"""
        placeholder = PlaceholderWidget("Export/Import Manager")
        self.tab_widget.addTab(placeholder, "Export/Import")

    def setup_connections(self):
        """Setup signal connections"""
        self.automation_list.itemDoubleClicked.connect(self.edit_automation)

    def setup_lazy_loading(self):
        """Setup lazy loading for tabs"""
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        """Handle tab change for lazy loading"""
        if index < 0:
            return

        # Skip if this tab has already been loaded
        if index in self._loaded_tabs:
            return

        # Get the tab text to determine which feature to load
        tab_text = self.tab_widget.tabText(index)

        if tab_text == "Templates" and index not in self._loaded_tabs:
            self._load_templates_tab(index)
        elif tab_text == "Scheduler" and index not in self._loaded_tabs:
            self._load_scheduler_tab(index)
        elif tab_text == "Debug" and index not in self._loaded_tabs:
            self._load_debug_tab(index)
        elif tab_text == "Performance" and index not in self._loaded_tabs:
            self._load_performance_tab(index)
        elif tab_text == "Export/Import" and index not in self._loaded_tabs:
            self._load_export_import_tab(index)

        # Mark this tab as loaded
        self._loaded_tabs.add(index)

    def _load_templates_tab(self, index):
        """Load the actual templates widget"""
        from features.node_templates import NodeTemplateWidget

        # Temporarily disconnect signal to avoid infinite loop
        self.tab_widget.currentChanged.disconnect()

        widget = NodeTemplateWidget()
        self._feature_widgets["templates"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, "Templates")
        self.tab_widget.setCurrentIndex(index)

        # Reconnect signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_scheduler_tab(self, index):
        """Load the actual scheduler widget"""
        from features.workflow_scheduler import WorkflowScheduler

        # Temporarily disconnect signal to avoid infinite loop
        self.tab_widget.currentChanged.disconnect()

        widget = WorkflowScheduler()
        widget.schedule_triggered.connect(self.run_scheduled_automation)
        self._feature_widgets["scheduler"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, "Scheduler")
        self.tab_widget.setCurrentIndex(index)

        # Reconnect signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_debug_tab(self, index):
        """Load the actual debug console widget"""
        from features.debug_console import DebugConsole

        # Temporarily disconnect signal to avoid infinite loop
        self.tab_widget.currentChanged.disconnect()

        widget = DebugConsole()
        self._feature_widgets["debug"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, "Debug")
        self.tab_widget.setCurrentIndex(index)

        # Reconnect signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_performance_tab(self, index):
        """Load the actual performance monitor widget"""
        from features.performance_monitor import PerformanceMonitor

        # Temporarily disconnect signal to avoid infinite loop
        self.tab_widget.currentChanged.disconnect()

        widget = PerformanceMonitor()
        self._feature_widgets["performance"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, "Performance")
        self.tab_widget.setCurrentIndex(index)

        # Reconnect signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_export_import_tab(self, index):
        """Load the actual export/import widget"""
        from features.export_import import ExportImportManager

        # Temporarily disconnect signal to avoid infinite loop
        self.tab_widget.currentChanged.disconnect()

        widget = ExportImportManager()
        self._feature_widgets["export_import"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, "Export/Import")
        self.tab_widget.setCurrentIndex(index)

        # Reconnect signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def load_automations(self):
        """Load available automations"""
        self.automation_list.clear()

        automations = self.fetch_automations()

        if not automations:
            item = QListWidgetItem(
                "No automations found. Create your first automation!"
            )
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
            self.automation_list.addItem(item)
            return

        for name in automations:
            item = QListWidgetItem(name)
            self.automation_list.addItem(item)

    def fetch_automations(self):
        """Optimized automation fetching"""
        if not AUTOMATIONS_DIR.exists():
            return []

        automations = []
        for file_path in AUTOMATIONS_DIR.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    automations.append(data.get("name", file_path.stem))
            except (json.JSONDecodeError, IOError):
                continue  # Skip invalid files silently

        return automations

    def create_new_automation(self):
        """Create a new automation"""
        self.new_automation_window = NewAutomationWindow(main_window=self)
        self.new_automation_window.show()

    def edit_automation(self, item):
        """Edit selected automation"""
        automation_name = item.text()
        if automation_name == "No automations found. Create your first automation!":
            return

        from automation_manager.node_editor_window import NodeEditorWindow

        self.editor_window = NodeEditorWindow(automation_name)
        self.editor_window.closed.connect(self.show)
        self.editor_window.show()
        self.hide()

    def open_browse_models_window(self):
        """Open browse models window"""
        self.browse_window = BrowseModelsWindow()
        self.browse_window.show()

    def run_scheduled_automation(self, automation_name):
        """Run a scheduled automation"""
        self.status_bar.showMessage(f"Running scheduled automation: {automation_name}")
        # This would integrate with the actual automation runner
        print(f"Running scheduled automation: {automation_name}")

    def show_import_dialog(self):
        """Show import dialog"""
        self.tab_widget.setCurrentIndex(5)  # Switch to export/import tab

    def show_export_dialog(self):
        """Show export dialog"""
        self.tab_widget.setCurrentIndex(5)  # Switch to export/import tab

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About NodeBox Enhanced",
            "NodeBox Enhanced v2.0\n\n"
            "A powerful visual automation platform with:\n"
            "• Node Templates\n"
            "• Workflow Scheduler\n"
            "• Debug Console\n"
            "• Performance Monitor\n"
            "• Export/Import System\n\n"
            "Built with Python and PyQt6",
        )

    def closeEvent(self, event):
        """Optimized window close event"""
        # Stop any running monitors
        if "performance" in self._feature_widgets:
            self._feature_widgets["performance"].stop_monitoring()

        # Clean up feature widgets
        for widget in self._feature_widgets.values():
            if hasattr(widget, "cleanup"):
                widget.cleanup()

        event.accept()
