from PyQt6.QtCore import QPointF, Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QPen,
    QWheelEvent,
)
from PyQt6.QtWidgets import QInputDialog, QWidget, QVBoxLayout

from automation_manager.node import NodeWidget
from predefined.registry import PredefinedNodeRegistry
from utils.node_runner import ExecutionSignals, execute_all_nodes
from utils.performance_bus import get_performance_bus
from canvasmanager.output_console import OutputConsole


class ResizeHandle(QWidget):
    """Small draggable handle placed above the OutputConsole."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._start_y = 0
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        self.setStyleSheet("background: transparent;")
        self.setFixedHeight(6)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_y = event.globalPosition().y()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            dy = int(event.globalPosition().y() - self._start_y)
            parent = self.parent()
            if parent and hasattr(parent, "adjust_console_height"):
                parent.adjust_console_height(-dy)
            self._start_y = event.globalPosition().y()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        event.accept()


class CanvasWidget(QWidget):
    def __init__(self, automation_name=None, automation_data=None, parent=None):
        super().__init__(parent)
        self.automation_name = automation_name
        self.automation_data = automation_data or {"nodes": [], "connections": []}

        # Visual
        self.grid_size = 50
        self.grid_color = QColor("#404040")
        self.bg_color = QColor("#202020")

        # Graph data
        self.nodes = {}
        self.connections = []
        self.pending_connection = None

        # Interaction state
        self.offset = QPointF(0, 0)
        self.drag_start = None
        self.space_held = False
        self.last_mouse_pos = QPointF()
        self.selected_node = None

        self.setAcceptDrops(True)
        self.initial_centering_done = False
        QTimer.singleShot(0, self.center_initial_view)

        self.scale = 1.0
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Output console
        self.output_console = OutputConsole(self)
        self.console_visible = False
        self.console_height = 180
        self.output_console.hide()

        # Resize handle
        self.console_handle = ResizeHandle(self)
        self.console_handle.hide()
        self.output_console.setMinimumHeight(80)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # Execution signals
        self.current_execution_signals = None

        self.load_canvas_state()

    # ---------------- Console utilities ----------------
    def show_console(self):
        if not self.console_visible:
            self.console_visible = True
            self.output_console.show()
            self.console_handle.show()
            self.position_console_widgets()

    def hide_console(self):
        if self.console_visible:
            self.console_visible = False
            self.output_console.hide()
            self.console_handle.hide()
            self.update()

    def toggle_console(self):
        if self.console_visible:
            self.hide_console()
        else:
            self.show_console()

    def position_console_widgets(self):
        if not self.console_visible:
            return
        w = self.width()
        ch = max(80, min(self.console_height, int(self.height() * 0.8)))
        handle_h = self.console_handle.height()
        self.output_console.setGeometry(0, self.height() - ch, w, ch)
        self.console_handle.setGeometry(0, self.height() - ch - handle_h, w, handle_h)
        self.output_console.raise_()
        self.console_handle.raise_()

    def adjust_console_height(self, delta_px):
        self.console_height = max(80, min(self.height() - 40, self.console_height + delta_px))
        self.position_console_widgets()

    # ---------------- Drawing ----------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)

        pen = QPen(self.grid_color)
        pen.setWidth(max(1, int(1 / self.scale)))
        painter.setPen(pen)

        left = -self.offset.x() / self.scale
        top = -self.offset.y() / self.scale
        right = left + self.width() / self.scale
        bottom = top + self.height() / self.scale

        x_start = int(left // self.grid_size * self.grid_size)
        y_start = int(top // self.grid_size * self.grid_size)

        for x in range(x_start, int(right), self.grid_size):
            painter.drawLine(int(x), int(top), int(x), int(bottom))
        for y in range(y_start, int(bottom), self.grid_size):
            painter.drawLine(int(left), int(y), int(right), int(y))

        painter.resetTransform()
        self.draw_coordinates(painter)

        for connection in self.connections:
            connection.draw(painter)
        if self.pending_connection:
            self.pending_connection.draw(painter)

    def draw_coordinates(self, painter: QPainter):
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 10))
        canvas_pos = self.mapFromGlobal(self.cursor().pos())
        logical_pos = QPointF(
            (canvas_pos.x() - self.offset.x()) / self.scale,
            -(canvas_pos.y() - self.offset.y()) / self.scale,
        )
        painter.drawText(10, self.height() - 10, f"X: {int(logical_pos.x())}  Y: {int(logical_pos.y())}")

    # ---------------- Run All Nodes ----------------
    def reset_all_node_statuses(self):
        for node in self.nodes.values():
            if hasattr(node, "reset_execution_status"):
                node.reset_execution_status()

    def run_all_nodes(self, *args):
        """Unified version combining console logging + async execution."""
        self.show_console()
        try:
            self.output_console.clear_output() if hasattr(self.output_console, "clear_output") else self.output_console.clear()
        except Exception:
            self.output_console.clear()

        self.output_console.appendPlainText("▶ Starting automation run...")

        bus = get_performance_bus()
        node_exec_times = {}

        def _on_error(node, error):
            msg = f"❌ Error in node {getattr(node, 'title', '?')}: {error}"
            self.output_console.appendPlainText(msg)

        def _on_node_executed(node, duration_s):
            node_exec_times[getattr(node, "title", str(id(node)))] = duration_s
            msg = f"✅ Executed node: {node.title} ({duration_s:.2f}s)"
            self.output_console.appendPlainText(msg)

        def _on_log(line, stream_type):
            self.output_console.appendPlainText(line)

        # Signals for async run
        execution_signals = ExecutionSignals()
        self.current_execution_signals = execution_signals

        def on_execution_completed(result):
            try:
                self.save_canvas_state()
                self.current_execution_signals = None
                metrics = {
                    "active_nodes": len(self.nodes),
                    "total_nodes": result.get("total_nodes", len(self.nodes)),
                    "workflows_running": 0,
                    "execution_time": result.get("total_duration_s", 0.0),
                    "error_count": result.get("error_count", 0),
                    "node_exec_times": node_exec_times,
                }
                bus.metrics_signal.emit(metrics)
            except Exception as e:
                print(f"Error in execution completion handler: {e}")

        execution_signals.execution_completed.connect(on_execution_completed)

        result = execute_all_nodes(
            self.nodes.values(),
            self.connections,
            on_error=_on_error,
            on_node_executed=_on_node_executed,
            on_log=_on_log,
            signals=execution_signals,
        )

        self.output_console.appendPlainText("✔ Automation completed.")
        self.output_console.appendPlainText(f"Summary: {result}")
        self.position_console_widgets()

    # ---------------- Interaction ----------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_on_node = any(
                node.geometry().contains(node.mapFromParent(event.pos()))
                for node in self.nodes.values()
            )
            if not clicked_on_node and self.selected_node:
                self.selected_node.selected = False
                self.selected_node.update()
                self.selected_node = None

        if event.button() == Qt.MouseButton.LeftButton and self.space_held:
            self.drag_start = event.pos()

        if event.button() == Qt.MouseButton.RightButton:
            name, ok = QInputDialog.getText(self, "Create Node", "Enter node name:")
            if ok and name:
                node = NodeWidget(name, self)
                import uuid
                node.id = getattr(node, "id", str(uuid.uuid4()))
                canvas_pos = (event.position() - self.offset) / self.scale
                node.logical_pos = canvas_pos
                node.update_position()
                self.nodes[node.id] = node
                node.show()
                self.save_canvas_state()

        clicked_port = self.get_port_at(event.pos())
        if clicked_port:
            self.handle_port_click(clicked_port)
        elif self.pending_connection:
            self.cancel_connection()

        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.last_mouse_pos = event.position()
        if self.pending_connection:
            self.pending_connection.set_end_point(event.position())
            self.update()
        super().mouseMoveEvent(event)

        if event.buttons() & Qt.MouseButton.LeftButton and self.space_held and self.drag_start:
            delta = QPointF(event.pos() - self.drag_start)
            self.offset += delta
            self.drag_start = event.pos()
            for node in self.nodes.values():
                node.update_position()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.space_held = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.space_held = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta().y()
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor
        old_scale = self.scale
        self.scale *= zoom_in_factor if angle > 0 else zoom_out_factor
        self.scale = max(0.1, min(self.scale, 10.0))
        mouse_pos = event.position()
        before_scale = (mouse_pos - self.offset) / old_scale
        after_scale = (mouse_pos - self.offset) / self.scale
        self.offset = QPointF(self.offset) + (after_scale - before_scale) * self.scale
        self.update()
        for node in self.nodes.values():
            node.update_position()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        node_type = event.mimeData().text()
        pos = (event.position() - self.offset) / self.scale
        predefined_node_class = PredefinedNodeRegistry.get_node(node_type)

        if node_type == "Custom Node":
            name, ok = QInputDialog.getText(self, "Create Node", "Enter node name:")
            if not ok or not name:
                return
            node = NodeWidget(name, self, pos=QPointF(pos))
        elif predefined_node_class:
            node_data = predefined_node_class.get_node_data()
            node = NodeWidget(
                node_data["name"], self, pos=QPointF(pos), outputs=node_data["outputs"]
            )
            node.code = node_data["code"]
        else:
            node = NodeWidget(node_type, self, pos=QPointF(pos))

        self.nodes[node.id] = node
        node.logical_pos = QPointF(pos)
        node.update_position()
        node.show()
        self.save_canvas_state()
        event.acceptProposedAction()

    # ---------------- Utilities ----------------
    def cancel_connection(self):
        self.pending_connection = None
        self.update()

    def get_port_at(self, pos):
        try:
            if hasattr(pos, "toPoint"):
                qpos = pos.toPoint()
            else:
                qpos = pos
            w = self.childAt(qpos)
            if w is None:
                return None
            if hasattr(w, "node") and hasattr(w, "type"):
                return w
            return None
        except Exception:
            return None

    def handle_port_click(self, port_widget):
        try:
            from automation_manager.ports_handler import start_connection, complete_connection
            port_type = getattr(port_widget, "type", "")
            if self.pending_connection is None and port_type == "output":
                start_connection(self, port_widget)
            elif self.pending_connection is not None and port_type == "input":
                complete_connection(self, port_widget)
            elif self.pending_connection is not None and port_type == "output":
                self.pending_connection.start_port = port_widget
                self.update()
        except Exception:
            self.pending_connection = None

    def update_node_position(self, node_id, logical_pos):
        node = self.nodes.get(node_id)
        if not node:
            return
        node.logical_pos = logical_pos
        if hasattr(node, "update_position"):
            node.update_position()

    def save_canvas_state(self):
        try:
            from canvasmanager.saveload_methods import save_canvas_state as _save
            _save(self)
        except Exception:
            return

    def load_canvas_state(self):
        try:
            from canvasmanager.saveload_methods import load_canvas_state as _load
            _load(self)
        except Exception:
            return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.console_visible:
            self.position_console_widgets()
