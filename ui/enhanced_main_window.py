"""
Optimized Enhanced Main Window - Minimalist and efficient
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTabWidget, QListWidget, QMenuBar, QMenu, QStatusBar, 
                             QMessageBox, QListWidgetItem)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, pyqtSignal

from browsemodels_manager.browsemodel_window import BrowseModelsWindow
from ui.newautomation_window import NewAutomationWindow
from utils.paths import AUTOMATIONS_DIR
from utils.screen_manager import ScreenManager

# Import optimized features
from features.node_templates import NodeTemplateWidget
from features.workflow_scheduler import WorkflowScheduler
from features.debug_console import DebugConsole
from features.performance_monitor import PerformanceMonitor
from features.export_import import ExportImportManager

import json
from pathlib import Path

class EnhancedMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeBox")
        
        # Use dynamic window sizing based on screen resolution
        x, y, width, height = ScreenManager.get_main_window_geometry()
        self.setGeometry(x, y, width, height)

        # Initialize feature widgets lazily
        self._feature_widgets = {}
        
        self.init_ui()
        self.setup_connections()

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
        create_button.setStyleSheet("""
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
        """)
        create_button.clicked.connect(self.create_new_automation)
        actions_layout.addWidget(create_button)
        
        browse_button = QPushButton("Browse Models")
        browse_button.setStyleSheet("""
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
        """)
        browse_button.clicked.connect(self.open_browse_models_window)
        actions_layout.addWidget(browse_button)
        
        layout.addLayout(actions_layout)
        
        # Automation list
        layout.addWidget(QLabel("Your Automations:"))
        self.automation_list = QListWidget()
        self.automation_list.setStyleSheet("""
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
        """)
        layout.addWidget(self.automation_list)
        
        # Load automations
        self.load_automations()
        
        home_widget.setLayout(layout)
        self.tab_widget.addTab(home_widget, "Home")

    def create_templates_tab(self):
        """Create node templates tab - lazy loaded"""
        if 'templates' not in self._feature_widgets:
            self._feature_widgets['templates'] = NodeTemplateWidget()
        self.tab_widget.addTab(self._feature_widgets['templates'], "Templates")

    def create_scheduler_tab(self):
        """Create workflow scheduler tab - lazy loaded"""
        if 'scheduler' not in self._feature_widgets:
            self._feature_widgets['scheduler'] = WorkflowScheduler()
            self._feature_widgets['scheduler'].schedule_triggered.connect(self.run_scheduled_automation)
        self.tab_widget.addTab(self._feature_widgets['scheduler'], "Scheduler")

    def create_debug_tab(self):
        """Create debug console tab - lazy loaded"""
        if 'debug' not in self._feature_widgets:
            self._feature_widgets['debug'] = DebugConsole()
        self.tab_widget.addTab(self._feature_widgets['debug'], "Debug")

    def create_performance_tab(self):
        """Create performance monitor tab - lazy loaded"""
        if 'performance' not in self._feature_widgets:
            self._feature_widgets['performance'] = PerformanceMonitor()
        self.tab_widget.addTab(self._feature_widgets['performance'], "Performance")

    def create_export_import_tab(self):
        """Create export/import tab - lazy loaded"""
        if 'export_import' not in self._feature_widgets:
            self._feature_widgets['export_import'] = ExportImportManager()
        self.tab_widget.addTab(self._feature_widgets['export_import'], "Export/Import")

    def setup_connections(self):
        """Setup signal connections"""
        self.automation_list.itemDoubleClicked.connect(self.edit_automation)

    def load_automations(self):
        """Load available automations"""
        self.automation_list.clear()
        
        automations = self.fetch_automations()
        
        if not automations:
            item = QListWidgetItem("No automations found. Create your first automation!")
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
        QMessageBox.about(self, "About NodeBox Enhanced", 
                         "NodeBox Enhanced v2.0\n\n"
                         "A powerful visual automation platform with:\n"
                         "• Node Templates\n"
                         "• Workflow Scheduler\n"
                         "• Debug Console\n"
                         "• Performance Monitor\n"
                         "• Export/Import System\n\n"
                         "Built with Python and PyQt6")

    def closeEvent(self, event):
        """Optimized window close event"""
        # Stop any running monitors
        if 'performance' in self._feature_widgets:
            self._feature_widgets['performance'].stop_monitoring()
        
        # Clean up feature widgets
        for widget in self._feature_widgets.values():
            if hasattr(widget, 'cleanup'):
                widget.cleanup()
        
        event.accept()
