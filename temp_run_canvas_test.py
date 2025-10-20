# temp_run_canvas_test.py
import sys

from PyQt6.QtWidgets import QApplication

from automation_manager.node_editor_window import NodeEditorWindow

app = QApplication(sys.argv)
win = NodeEditorWindow("TestAutomation")
win.show()
sys.exit(app.exec())
