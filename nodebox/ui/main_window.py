import json
import os
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from nodebox.core.paths import AUTOMATIONS_DIR, resource_path
from nodebox.core.screen import ScreenManager
from nodebox.services.ollama import OllamaInstaller
from nodebox.ui.canvas.dialogs import NodeEditorWindow
from nodebox.ui.features.automation_dialog import NewAutomationWindow
from nodebox.ui.features.placeholder import PlaceholderWidget
from nodebox.ui.models.browser import BrowseModelsWindow

# ---------------------------------------------------------------------------
# Design tokens (kept in sync with dark.qss)
# ---------------------------------------------------------------------------
_BG_DEEP    = "#0A0C10"
_BG_BASE    = "#0F1117"
_BG_RAISED  = "#161922"
_BG_HOVER   = "#1C2235"
_BORDER     = "#1E2538"
_ACCENT     = "#6366F1"
_SUCCESS    = "#10B981"
_TEXT       = "#F0F2F8"
_TEXT_DIM   = "#4A5578"
_TEXT_SEC   = "#8892B0"


class EnhancedMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeBox - Visual Automation Platform")

        x, y, width, height = ScreenManager.get_main_window_geometry()
        self.setGeometry(x, y, width, height)

        self.apply_theme()

        self._feature_widgets = {}
        self._loaded_tabs = set()

        self.ollama_installer = OllamaInstaller()
        self.ollama_installer.progress_updated.connect(self.update_ollama_indicator)
        self.ollama_installer.download_progress.connect(self.update_download_progress)
        self.ollama_installer.installation_complete.connect(
            self.on_installation_complete
        )

        self.init_ui()
        self.setup_connections()
        self.setup_lazy_loading()

    def apply_theme(self):
        self.setStyleSheet(f"QWidget {{ background-color: {_BG_DEEP}; color: {_TEXT}; }}")

    def get_icon(self, icon_name):
        icon_path = resource_path(f"assets/icons/{icon_name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    # ------------------------------------------------------------------
    # Main UI construction
    # ------------------------------------------------------------------
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.create_menu_bar()
        main_layout.addWidget(self._build_top_bar())

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        self.tab_widget = QTabWidget()
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(False)
        main_layout.addWidget(self.tab_widget)

        self.create_home_tab()
        self.create_templates_tab()
        self.create_scheduler_tab()
        self.create_debug_tab()
        self.create_performance_tab()
        self.create_export_import_tab()
        self.create_models_tab()

        main_layout.addWidget(self.status_bar)

        QTimer.singleShot(1500, self.show_ollama_checking)

    def _build_top_bar(self):
        """Gradient top navigation bar with logo and Ollama indicator."""
        top_bar = QWidget()
        top_bar.setFixedHeight(52)
        top_bar.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0C0E16, stop:0.4 #0F1117, stop:1 #0C0E16);
                border-bottom: 1px solid {_BORDER};
            }}
        """)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        # Logo wordmark area
        logo_widget = QWidget()
        logo_widget.setFixedWidth(140)
        logo_widget.setStyleSheet("background: transparent; border: none;")
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(8)

        logo_label = QLabel("NodeBox")
        logo_label.setFont(QFont("Poppins", 14, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #F0F2F8; background: transparent; border: none;")
        logo_layout.addWidget(logo_label)

        version_badge = QLabel("2.0")
        version_badge.setFont(QFont("Poppins", 9, QFont.Weight.Medium))
        version_badge.setStyleSheet("""
            background-color: rgba(99,102,241,0.18);
            color: #818CF8;
            border-radius: 4px;
            padding: 1px 6px;
        """)
        logo_layout.addWidget(version_badge)
        layout.addWidget(logo_widget)

        # Menu bar in the center-left area
        layout.addWidget(self.menu_bar)
        layout.addStretch()

        # Ollama status pill
        self.ollama_indicator = QLabel()
        self.ollama_indicator.setObjectName("ollamaIndicator")
        self.ollama_indicator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ollama_indicator.setMinimumWidth(150)
        self.ollama_indicator.setFixedHeight(30)
        self.ollama_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ollama_indicator.setFont(QFont("Poppins", 9, QFont.Weight.DemiBold))
        layout.addWidget(self.ollama_indicator)

        return top_bar

    def create_menu_bar(self):
        self.menu_bar = QMenuBar()
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
                font-size: 13px;
                font-weight: 500;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 14px;
                border-radius: 7px;
                color: #8892B0;
            }
            QMenuBar::item:selected {
                background-color: rgba(99,102,241,0.12);
                color: #A5B4FC;
            }
        """)

        file_menu = self.menu_bar.addMenu("File")

        new_action = QAction(self.get_icon("plus"), "New Automation", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_automation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        import_action = QAction(self.get_icon("download"), "Import Workflows", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.show_import_dialog)
        file_menu.addAction(import_action)

        export_action = QAction(self.get_icon("upload"), "Export Workflows", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.show_export_dialog)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction(self.get_icon("x"), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = self.menu_bar.addMenu("Tools")

        templates_action = QAction(self.get_icon("file-text"), "Node Templates", self)
        templates_action.triggered.connect(lambda: self.switch_to_tab(" Templates"))
        tools_menu.addAction(templates_action)

        scheduler_action = QAction(self.get_icon("clock"), "Workflow Scheduler", self)
        scheduler_action.triggered.connect(lambda: self.switch_to_tab(" Scheduler"))
        tools_menu.addAction(scheduler_action)

        debug_action = QAction(self.get_icon("terminal"), "Debug Console", self)
        debug_action.triggered.connect(lambda: self.switch_to_tab(" Debug"))
        tools_menu.addAction(debug_action)

        performance_action = QAction(self.get_icon("activity"), "Performance Monitor", self)
        performance_action.triggered.connect(lambda: self.switch_to_tab(" Performance"))
        tools_menu.addAction(performance_action)

        help_menu = self.menu_bar.addMenu("Help")

        about_action = QAction(self.get_icon("info"), "About NodeBox", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # ------------------------------------------------------------------
    # Ollama Indicator
    # ------------------------------------------------------------------
    def update_ollama_indicator(self, state: str, message: str = ""):
        state = (state or "").lower()
        self._ollama_state = state

        mapping = {
            "checking":   ("Checking Ollama",        "#818CF8", "rgba(129,140,248,0.15)"),
            "found":      ("Ollama Online",           "#10B981", "rgba(16,185,129,0.15)"),
            "installing": ("Installing Ollama",       "#F59E0B", "rgba(245,158,11,0.15)"),
            "downloading":(f"Downloading {message}",  "#F59E0B", "rgba(245,158,11,0.15)"),
            "not_found":  ("Ollama Offline",          "#EF4444", "rgba(239,68,68,0.15)"),
            "ready":      ("Ollama Ready",             "#10B981", "rgba(16,185,129,0.15)"),
            "error":      (f"Error: {message}",        "#EF4444", "rgba(239,68,68,0.15)"),
            "cancelled":  ("Cancelled",               "#4A5578", "rgba(74,85,120,0.15)"),
            "hidden":     ("",                        "transparent", "transparent"),
        }

        text, color, bg = mapping.get(state, (state.replace("_", " ").title(), "#8892B0", "rgba(136,146,176,0.12)"))

        if state == "hidden":
            self.ollama_indicator.setVisible(False)
            return

        self.ollama_indicator.setVisible(True)
        self.ollama_indicator.setText(text)
        self.ollama_indicator.setStyleSheet(f"""
            QLabel#ollamaIndicator {{
                background-color: {bg};
                color: {color};
                border: 1px solid {color};
                border-radius: 14px;
                padding: 4px 14px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)

    def update_download_progress(self, percentage: int):
        if getattr(self, "_ollama_state", "") == "installing":
            self.ollama_indicator.setText(f"Downloading... {percentage}%")

    def on_installation_complete(self, status: str):
        msgs = {
            "ready": "Ollama installed successfully",
            "error": "Ollama installation failed",
            "cancelled": "Ollama installation cancelled",
        }
        self.status_bar.showMessage(msgs.get(status, ""))

    def show_ollama_checking(self):
        self.update_ollama_indicator("checking")
        if self.ollama_installer.check_ollama():
            self.update_ollama_indicator("found")
        else:
            self.show_ollama_download_popup()

    def show_ollama_download_popup(self):
        reply = QMessageBox.question(
            self,
            "Ollama Not Found",
            "Ollama is not installed on your system.\nWould you like to download and install it now?\n\nThis will happen in the background.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.ollama_installer.download_ollama_background()
        else:
            self.update_ollama_indicator("not_found")

    # ------------------------------------------------------------------
    # Home Tab
    # ------------------------------------------------------------------
    def create_home_tab(self):
        home_widget = QWidget()
        home_widget.setStyleSheet(f"background-color: {_BG_DEEP};")

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(22)

        # ── Hero Banner ──────────────────────────────────────────────
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10132A, stop:0.5 #141830, stop:1 #0E1126);
                border: 1px solid rgba(99,102,241,0.2);
                border-radius: 16px;
                padding: 0;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        hero.setGraphicsEffect(shadow)

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(36, 28, 36, 28)
        hero_layout.setSpacing(6)

        title = QLabel("NodeBox")
        title.setFont(QFont("Poppins", 36, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #F0F2F8; background: transparent; border: none;")
        hero_layout.addWidget(title)

        subtitle = QLabel("Visual Automation Platform  &  Local AI Orchestration")
        subtitle.setFont(QFont("Poppins", 13, QFont.Weight.Medium))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #6366F1; background: transparent; border: none; letter-spacing: 0.3px;")
        hero_layout.addWidget(subtitle)

        layout.addWidget(hero)

        # ── Quick Actions ────────────────────────────────────────────
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)

        create_button = self._action_button(
            label="Create New Automation",
            sub="Design a new workflow from scratch",
            icon_name="plus-circle",
            color=_ACCENT,
            hover="#5153D6",
        )
        create_button.clicked.connect(self.create_new_automation)
        actions_layout.addWidget(create_button)

        browse_button = self._action_button(
            label="Browse AI Models",
            sub="Explore & download local Ollama models",
            icon_name="package",
            color=_SUCCESS,
            hover="#059669",
        )
        browse_button.clicked.connect(self.open_browse_models_window)
        actions_layout.addWidget(browse_button)

        layout.addLayout(actions_layout)

        # ── Automations Section ──────────────────────────────────────
        header_row = QHBoxLayout()
        list_label = QLabel("Your Automations")
        list_label.setFont(QFont("Poppins", 15, QFont.Weight.DemiBold))
        list_label.setStyleSheet("color: #F0F2F8;")
        header_row.addWidget(list_label)
        header_row.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        refresh_btn.setFixedHeight(32)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BG_RAISED};
                color: {_TEXT_SEC};
                border: 1px solid {_BORDER};
                border-radius: 7px;
                padding: 4px 14px;
            }}
            QPushButton:hover {{
                background-color: {_BG_HOVER};
                border-color: {_ACCENT};
                color: {_TEXT};
            }}
        """)
        refresh_btn.clicked.connect(self.load_automations)
        header_row.addWidget(refresh_btn)
        layout.addLayout(header_row)

        self.automation_list = QListWidget()
        self.automation_list.setFont(QFont("Poppins", 12))
        self.automation_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {_BORDER};
                border-radius: 12px;
                padding: 6px;
                background-color: {_BG_BASE};
            }}
            QListWidget::item {{
                padding: 14px 18px;
                border: 1px solid {_BORDER};
                border-radius: 9px;
                margin: 3px 2px;
                background-color: {_BG_RAISED};
                color: #C8D0E8;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background-color: {_BG_HOVER};
                border-color: {_ACCENT};
                color: {_TEXT};
            }}
            QListWidget::item:selected {{
                background-color: rgba(99,102,241,0.18);
                border-color: {_ACCENT};
                border-left: 3px solid {_ACCENT};
                color: #FFFFFF;
            }}
        """)
        layout.addWidget(self.automation_list, stretch=1)

        help_label = QLabel("Double-click an automation to open the canvas editor")
        help_label.setFont(QFont("Poppins", 10))
        help_label.setStyleSheet(f"color: {_TEXT_DIM}; margin-top: 2px;")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_label)

        self.load_automations()

        home_widget.setLayout(layout)
        self.tab_widget.addTab(home_widget, self.get_icon("home"), " Home")

    def _action_button(self, label, sub, icon_name, color, hover):
        """Rich action button with label + sub-text."""
        btn = QPushButton()
        btn.setFont(QFont("Poppins", 13, QFont.Weight.DemiBold))
        btn.setMinimumHeight(72)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Build inner layout
        inner = QHBoxLayout(btn)
        inner.setContentsMargins(20, 0, 20, 0)
        inner.setSpacing(14)

        icon_block = QLabel()
        icon_block.setFixedSize(36, 36)
        icon_block.setStyleSheet(f"""
            background-color: rgba(255,255,255,0.08);
            border-radius: 9px;
        """)
        icon_block.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = self.get_icon(icon_name)
        if not icon.isNull():
            icon_block.setPixmap(icon.pixmap(20, 20))
        inner.addWidget(icon_block)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        main_text = QLabel(label)
        main_text.setFont(QFont("Poppins", 12, QFont.Weight.DemiBold))
        main_text.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        sub_text = QLabel(sub)
        sub_text.setFont(QFont("Poppins", 10))
        sub_text.setStyleSheet("color: rgba(255,255,255,0.65); background: transparent; border: none;")
        text_col.addWidget(main_text)
        text_col.addWidget(sub_text)
        inner.addLayout(text_col)
        inner.addStretch()

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {hover};
                padding-top: 2px;
            }}
        """)
        return btn

    # ------------------------------------------------------------------
    # Other Tab placeholders
    # ------------------------------------------------------------------
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
        placeholder = PlaceholderWidget("Local Models Manager")
        self.tab_widget.addTab(placeholder, self.get_icon("database"), " Local Models")

    # ------------------------------------------------------------------
    # Lazy loading
    # ------------------------------------------------------------------
    def setup_connections(self):
        self.automation_list.itemDoubleClicked.connect(self.edit_automation)
        self.automation_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.automation_list.customContextMenuRequested.connect(self.show_automation_context_menu)

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
        from nodebox.ui.features.templates import NodeTemplateWidget

        self.tab_widget.currentChanged.disconnect()
        widget = NodeTemplateWidget()
        self._feature_widgets["templates"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("file-text"), " Templates")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_scheduler_tab(self, index):
        from nodebox.ui.features.scheduler_widget import WorkflowScheduler

        self.tab_widget.currentChanged.disconnect()
        widget = WorkflowScheduler()
        widget.schedule_triggered.connect(self.run_scheduled_automation)
        self._feature_widgets["scheduler"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("clock"), " Scheduler")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_debug_tab(self, index):
        from nodebox.ui.features.debug_console import DebugConsole

        self.tab_widget.currentChanged.disconnect()
        widget = DebugConsole()
        self._feature_widgets["debug"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("terminal"), " Debug")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_performance_tab(self, index):
        from nodebox.ui.features.performance_monitor import PerformanceMonitor

        self.tab_widget.currentChanged.disconnect()
        widget = PerformanceMonitor()
        self._feature_widgets["performance"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("activity"), " Performance")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_export_import_tab(self, index):
        from nodebox.ui.features.export_import_widget import ExportImportManager

        self.tab_widget.currentChanged.disconnect()
        widget = ExportImportManager()
        self._feature_widgets["export_import"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("package"), " Export/Import")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _load_models_tab(self, index):
        from nodebox.ui.models.manager import ModelManagerWidget

        self.tab_widget.currentChanged.disconnect()
        widget = ModelManagerWidget()
        self._feature_widgets["models"] = widget
        self.tab_widget.removeTab(index)
        self.tab_widget.insertTab(index, widget, self.get_icon("database"), " Local Models")
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    # ------------------------------------------------------------------
    # Automations CRUD
    # ------------------------------------------------------------------
    def load_automations(self):
        self.automation_list.clear()
        self.status_bar.showMessage("Loading automations...")

        automations = self.fetch_automations()

        if not automations:
            item = QListWidgetItem("No automations yet — create your first one above")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setFont(QFont("Poppins", 12))
            item.setForeground(QColor("#4A5578"))
            self.automation_list.addItem(item)
            self.status_bar.showMessage("Ready")
            return

        for name in automations:
            item = QListWidgetItem(self.get_icon("file"), f"  {name}")
            item.setFont(QFont("Poppins", 12, QFont.Weight.Medium))
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
        if "No automations" in automation_name:
            return

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
        item = self.automation_list.itemAt(position)
        if not item:
            return

        automation_name = item.text().strip()
        if "No automations" in automation_name:
            return

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #111420;
                border: 1px solid {_BORDER};
                border-radius: 10px;
                padding: 6px 4px;
            }}
            QMenu::item {{
                padding: 9px 28px 9px 14px;
                border-radius: 7px;
                font-size: 13px;
                color: #C8D0E8;
                margin: 1px 3px;
            }}
            QMenu::item:selected {{
                background-color: {_ACCENT};
                color: #FFFFFF;
            }}
            QMenu::separator {{
                height: 1px;
                background: {_BORDER};
                margin: 5px 10px;
            }}
        """)

        rename_action = QAction(self.get_icon("edit-2"), "Rename Automation", self)
        rename_action.triggered.connect(lambda: self.rename_automation(automation_name))
        menu.addAction(rename_action)

        duplicate_action = QAction(self.get_icon("copy"), "Duplicate Automation", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_automation(automation_name))
        menu.addAction(duplicate_action)

        menu.addSeparator()

        delete_action = QAction(self.get_icon("trash-2"), "Delete Automation", self)
        delete_action.triggered.connect(lambda: self.delete_automation(automation_name))
        menu.addAction(delete_action)

        menu.exec(self.automation_list.mapToGlobal(position))

    def rename_automation(self, current_name):
        new_name, ok = QInputDialog.getText(
            self, "Rename Automation", "Enter new automation name:", text=current_name
        )
        if not ok or not new_name.strip() or new_name.strip() == current_name:
            return

        new_name = new_name.strip()
        existing_automations = self.fetch_automations()
        if new_name in existing_automations:
            QMessageBox.warning(self, "Duplicate Name", f"An automation named '{new_name}' already exists.")
            return

        try:
            self._rename_automation_file(current_name, new_name)
            self.status_bar.showMessage(f"Renamed '{current_name}' to '{new_name}'")
            self.load_automations()
        except Exception as e:
            QMessageBox.critical(self, "Rename Failed", f"Failed to rename automation:\n{str(e)}")

    def delete_automation(self, automation_name):
        reply = QMessageBox.question(
            self,
            "Delete Automation",
            f"Are you sure you want to delete '{automation_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._delete_automation_file(automation_name)
            self.status_bar.showMessage(f"Deleted automation '{automation_name}'")
            self.load_automations()
        except Exception as e:
            QMessageBox.critical(self, "Delete Failed", f"Failed to delete automation:\n{str(e)}")

    def _rename_automation_file(self, old_name, new_name):
        old_file = AUTOMATIONS_DIR / f"{old_name}.json"
        new_file = AUTOMATIONS_DIR / f"{new_name}.json"
        if not old_file.exists():
            raise FileNotFoundError(f"Automation file not found: {old_file}")
        with open(old_file, "r") as f:
            data = json.load(f)
        data["name"] = new_name
        with open(new_file, "w") as f:
            json.dump(data, f, indent=4)
        old_file.unlink()

    def _delete_automation_file(self, automation_name):
        file_path = AUTOMATIONS_DIR / f"{automation_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Automation file not found: {file_path}")
        file_path.unlink()

    def duplicate_automation(self, automation_name):
        base_name = f"{automation_name} Copy"
        counter = 1
        new_name = base_name
        existing_automations = self.fetch_automations()
        while new_name in existing_automations:
            counter += 1
            new_name = f"{base_name} {counter}"

        new_name, ok = QInputDialog.getText(
            self, "Duplicate Automation", "Enter name for duplicate:", text=new_name
        )
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()
        if new_name in existing_automations:
            QMessageBox.warning(self, "Duplicate Name", f"An automation named '{new_name}' already exists.")
            return

        try:
            self._duplicate_automation_file(automation_name, new_name)
            self.status_bar.showMessage(f"Duplicated '{automation_name}' as '{new_name}'")
            self.load_automations()
        except Exception as e:
            QMessageBox.critical(self, "Duplicate Failed", f"Failed to duplicate automation:\n{str(e)}")

    def _duplicate_automation_file(self, source_name, target_name):
        source_file = AUTOMATIONS_DIR / f"{source_name}.json"
        target_file = AUTOMATIONS_DIR / f"{target_name}.json"
        if not source_file.exists():
            raise FileNotFoundError(f"Source automation file not found: {source_file}")
        with open(source_file, "r") as f:
            data = json.load(f)
        data["name"] = target_name
        with open(target_file, "w") as f:
            json.dump(data, f, indent=4)

    # ------------------------------------------------------------------
    # About Dialog
    # ------------------------------------------------------------------
    def show_about(self):
        about_text = """
        <div style='text-align: center; font-family: Poppins, sans-serif;'>
            <h2 style='color: #6366F1; font-size: 22px; margin-bottom: 4px;'>NodeBox</h2>
            <p style='color: #8892B0; font-size: 13px; margin-top: 0;'>Visual Automation & AI Orchestration Platform</p>
            <p style='color: #F0F2F8; font-size: 14px;'><b>Version 2.0</b></p>
            <hr style='border: 1px solid #1E2538; margin: 14px 0;'>
            <ul style='text-align: left; color: #8892B0; font-size: 13px; padding-left: 20px;'>
                <li>Visual Graph Editor with Bezier Wires</li>
                <li>Local Ollama AI Integration</li>
                <li>Node Templates Gallery</li>
                <li>Workflow Scheduler &amp; Automations</li>
                <li>Debug Console &amp; Performance Monitor</li>
            </ul>
            <p style='color: #4A5578; font-size: 11px;'>Built with Python 3 &amp; PyQt6</p>
        </div>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About NodeBox")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: #111420;
            }}
            QLabel {{
                color: #F0F2F8;
                min-width: 420px;
                background: transparent;
            }}
            QPushButton {{
                background-color: {_ACCENT};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                min-width: 80px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #5153D6;
            }}
        """)
        msg_box.exec()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
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

    def closeEvent(self, event):
        if hasattr(self, "ollama_installer") and self.ollama_installer.is_installing():
            self.ollama_installer.cancel_installation()
            time.sleep(0.5)

        if "performance" in self._feature_widgets:
            self._feature_widgets["performance"].stop_monitoring()

        for widget in self._feature_widgets.values():
            if hasattr(widget, "cleanup"):
                widget.cleanup()

        event.accept()


__all__ = ["EnhancedMainWindow"]
