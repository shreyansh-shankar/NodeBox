from PyQt6.QtCore import QPointF, Qt, QTimer
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
from utils.node_runner import execute_all_nodes
from utils.performance_bus import get_performance_bus
from canvasmanager.output_console import OutputConsole


class ResizeHandle(QWidget):
    """
    Small draggable handle placed above the OutputConsole.
    Dragging it vertically will change the console height.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._start_y = 0
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        # keep it visually subtle
        self.setStyleSheet("background: transparent;")
        self.setFixedHeight(6)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_y = event.globalPosition().y()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self._dragging:
            dy = int(event.globalPosition().y() - self._start_y)
            parent = self.parent()
            if parent and hasattr(parent, "adjust_console_height"):
                parent.adjust_console_height(-dy)  # negative because dragging up should increase height
            self._start_y = event.globalPosition().y()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        event.accept()


class CanvasWidget(QWidget):
    def __init__(self, automation_name=None, automation_data=None, parent=None):
        super().__init__(parent)
        self.automation_name = automation_name
        self.automation_data = automation_data or {"nodes": [], "connections": []}

        # Visuals
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

        # --- Output console (child) ---
        # Create console but keep it hidden until run
        self.output_console = OutputConsole(self)
        self.console_visible = False
        self.console_height = 180  # default height in px
        self.output_console.hide()

        # Resize handle sits above the console and allows resizing by dragging
        self.console_handle = ResizeHandle(self)
        self.console_handle.hide()

        # Ensure console can expand a bit
        self.output_console.setMinimumHeight(80)

        # Use a simple layout for the main widget (canvas itself paints directly)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # No widgets are added to this layout because CanvasWidget handles its painting.
        self.setLayout(self.main_layout)

        self.load_canvas_state()

    # -------------------------
    # Console utilities
    # -------------------------
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
            self.update()  # redraw without console

    def toggle_console(self):
        if self.console_visible:
            self.hide_console()
        else:
            self.show_console()

    def position_console_widgets(self):
        """
        Place the console and handle at the bottom of the CanvasWidget.
        Call this from resizeEvent or whenever console_height changes.
        """
        if not self.console_visible:
            return

        w = self.width()
        ch = max(80, min(self.console_height, int(self.height() * 0.8)))  # clamp
        handle_h = self.console_handle.height()
        # Console sits at bottom
        self.output_console.setGeometry(0, self.height() - ch, w, ch)
        # Handle sits just above it
        self.console_handle.setGeometry(0, self.height() - ch - handle_h, w, handle_h)
        # Ensure console is on top
        self.output_console.raise_()
        self.console_handle.raise_()

    def adjust_console_height(self, delta_px):
        """
        Increase/decrease console height by delta_px (positive increases height).
        Called by ResizeHandle.
        """
        self.console_height = max(80, min(self.height() - 40, self.console_height + delta_px))
        self.position_console_widgets()

    # -------------------------
    # Drawing and interaction
    # -------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)

        # Setup zoom and pan (canvas painting)
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

        # Draw connections and pending connection
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
        text = f"X: {int(logical_pos.x())}  Y: {int(logical_pos.y())}"
        painter.drawText(10, self.height() - 10, text)

    # -------------------------
    # Execution & logging
    # -------------------------

    def run_all_nodes(self, *args):
        print("Running all nodes...")

        # --- Show and prepare console ---
        self.show_console()
        # clear console contents using the public method on OutputConsole
        try:
            # prefer a clear method if available
            if hasattr(self.output_console, "clear_output"):
                self.output_console.clear_output()
            else:
                self.output_console.clear()
        except Exception:
            self.output_console.clear()

        # Log start
        if hasattr(self.output_console, "log_signal"):
            self.output_console.log_signal.emit("▶ Starting automation run...", "info")
        else:
            # fallback: append raw text
            self.output_console.appendPlainText("▶ Starting automation run...")

        bus = get_performance_bus()

        def _on_error(node, error):
            msg = f"❌ Error in node {getattr(node, 'title', '?')}: {error}"
            if hasattr(self.output_console, "log_signal"):
                self.output_console.log_signal.emit(msg, "error")
            else:
                self.output_console.appendPlainText(msg)

        node_exec_times = {}

        def _on_node_executed(node, duration_s):
            node_exec_times[getattr(node, "title", str(id(node)))] = duration_s
            msg = f"✅ Executed node: {node.title} ({duration_s:.2f}s)"
            if hasattr(self.output_console, "log_signal"):
                self.output_console.log_signal.emit(msg, "info")
            else:
                self.output_console.appendPlainText(msg)

        # If your execute_all_nodes supports an on_log hook, use it; otherwise we just use the on_node_executed/on_error hooks.
        def _on_log(line, stream_type):
            if stream_type == "stderr":
                if hasattr(self.output_console, "log_signal"):
                    self.output_console.log_signal.emit(line, "error")
                else:
                    self.output_console.appendPlainText(line)
            else:
                if hasattr(self.output_console, "log_signal"):
                    self.output_console.log_signal.emit(line, "info")
                else:
                    self.output_console.appendPlainText(line)

        # Execute nodes (note: execute_all_nodes signature may or may not accept on_log)
        # Try to pass on_log if supported, else call without it.
        try:
            result = execute_all_nodes(
                self.nodes.values(),
                self.connections,
                on_error=_on_error,
                on_node_executed=_on_node_executed,
                on_log=_on_log,
            )
        except TypeError:
            # older signature without on_log
            result = execute_all_nodes(
                self.nodes.values(),
                self.connections,
                on_error=_on_error,
                on_node_executed=_on_node_executed,
            )

        # --- Display summary ---
        if hasattr(self.output_console, "log_signal"):
            self.output_console.log_signal.emit("✔ Automation completed.", "info")
            self.output_console.log_signal.emit(f"Summary: {result}", "info")
        else:
            self.output_console.appendPlainText("✔ Automation completed.")
            self.output_console.appendPlainText(f"Summary: {result}")

        self.position_console_widgets()
        self.save_canvas_state()

        # Emit app metrics to performance tab
        metrics = {
            "active_nodes": len(self.nodes),
            "total_nodes": result.get("total_nodes", len(self.nodes)),
            "workflows_running": 0,
            "execution_time": result.get("total_duration_s", 0.0),
            "error_count": result.get("error_count", 0),
            "node_exec_times": node_exec_times,
        }
        bus.metrics_signal.emit(metrics)

    # -------------------------
    # Interaction events
    # -------------------------

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
                canvas_pos = (event.position() - self.offset) / self.scale
                node.logical_pos = canvas_pos
                node.update_position()
                self.nodes[node.id] = node
                node.show()
                self.save_canvas_state()

        clicked_port = self.get_port_at(event.pos())
        if clicked_port:
            self.handle_port_click(clicked_port)
        else:
            if self.pending_connection:
                self.cancel_connection()

        self.update()  # Trigger repaint

    def mouseMoveEvent(self, event: QMouseEvent):
        self.last_mouse_pos = event.position()
        if self.pending_connection:
            self.pending_connection.set_end_point(event.position())
            self.update()
        super().mouseMoveEvent(event)

        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and self.space_held
            and self.drag_start
        ):
            delta = QPointF(event.pos() - self.drag_start)
            self.offset += delta  # Invert to drag canvas
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
        # Zooming centered at cursor
        angle = event.angleDelta().y()
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor

        old_scale = self.scale
        if angle > 0:
            self.scale *= zoom_in_factor
        else:
            self.scale *= zoom_out_factor

        # Prevent zooming too far
        self.scale = max(0.1, min(self.scale, 10.0))

        # Adjust offset to keep zoom centered at mouse
        mouse_pos = event.position()
        before_scale = (mouse_pos - self.offset) / old_scale
        after_scale = (mouse_pos - self.offset) / self.scale
        self.offset = QPointF(self.offset) + (after_scale - before_scale) * self.scale

        self.update()

        for node in self.nodes.values():
            node.update_position()

    def center_initial_view(self):
        if not self.initial_centering_done:
            self.offset = QPointF(self.width() / 2, self.height() / 2)
            self.initial_centering_done = True
            self.update()

    # -------------------------
    # Basic utilities
    # -------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Reposition console and handle if necessary
        if self.console_visible:
            self.position_console_widgets()
