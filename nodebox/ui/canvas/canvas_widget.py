import contextlib
import json
import os
import uuid

from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QNativeGestureEvent,
    QPainter,
    QPen,
    QWheelEvent,
)
from PyQt6.QtWidgets import QDialog, QInputDialog, QVBoxLayout, QWidget

from nodebox.core.bus import get_performance_bus
from nodebox.core.engine import ExecutionSignals, execute_all_nodes
from nodebox.nodes.registry import PredefinedNodeRegistry
from nodebox.ui.canvas.connection import BezierConnection
from nodebox.ui.canvas.dialogs import NodeEditorDialog
from nodebox.ui.canvas.node_widget import NodeWidget
from nodebox.ui.canvas.output_console import OutputConsole


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

        self.grid_size = 50
        self.grid_color = QColor("#1A2040")
        self.dot_color = QColor("#252D42")
        self.bg_color = QColor("#0A0C10")

        self.nodes = {}
        self.connections = []
        self.pending_connection = None
        self.connection_start_port = None

        self.offset = QPointF(0, 0)
        self.drag_start = None
        self.space_held = False
        self.is_panning = False
        self.last_mouse_pos = QPointF()
        self.selected_node = None

        self.setAcceptDrops(True)
        self.initial_centering_done = False
        QTimer.singleShot(0, self.center_initial_view)

        self.scale = 1.0
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.output_console = OutputConsole(self)
        self.console_visible = False
        self.console_height = 180
        self.output_console.hide()

        self.console_handle = ResizeHandle(self)
        self.console_handle.hide()
        self.output_console.setMinimumHeight(80)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.current_execution_signals = None
        self.load_canvas_state()

    def open_node(self, node):
        from nodebox.ui.canvas.dialogs import parse_code_outputs

        inputs_dict = {}
        for conn in self.connections:
            if conn.end_port and conn.end_port.node == node:
                upstream_node = conn.start_port.node
                source_title = getattr(upstream_node, "title", "Upstream Node")
                upstream_outputs = getattr(upstream_node, "outputs", {})

                if isinstance(upstream_outputs, dict) and upstream_outputs:
                    for k, v in upstream_outputs.items():
                        inputs_dict[k] = {"value": v, "source": source_title}
                else:
                    ast_detected = parse_code_outputs(
                        getattr(upstream_node, "code", "")
                    )
                    if ast_detected:
                        for var in ast_detected:
                            inputs_dict[var] = {"value": None, "source": source_title}
                    elif isinstance(upstream_outputs, list):
                        for var in upstream_outputs:
                            inputs_dict[var] = {"value": None, "source": source_title}
                    else:
                        inputs_dict["data"] = {"value": None, "source": source_title}

        initial_code = getattr(node, "code", "")
        dlg = NodeEditorDialog(
            node=node, inputs=inputs_dict, initial_code=initial_code, parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            node.code = data.get("code", "")
            node.output_vars = data.get("outputs", [])
            node.update()
            with contextlib.suppress(Exception):
                node.update_position()
            with contextlib.suppress(Exception):
                self.save_canvas_state()

    def delete_node(self, node):
        if self.pending_connection:
            sp = self.pending_connection.start_port
            ep = self.pending_connection.end_port
            if (sp and sp.node == node) or (ep and ep.node == node):
                self.cancel_connection()

        new_connections = []
        for conn in self.connections:
            sp = getattr(conn, "start_port", None)
            ep = getattr(conn, "end_port", None)
            if (sp and sp.node == node) or (ep and ep.node == node):
                continue
            new_connections.append(conn)
        self.connections = new_connections

        try:
            if hasattr(node, "input_port") and node.input_port:
                node.input_port.deleteLater()
            if hasattr(node, "output_port") and node.output_port:
                node.output_port.deleteLater()
        except Exception:
            pass

        if node.id in self.nodes:
            del self.nodes[node.id]

        if self.selected_node is node:
            self.selected_node = None

        node.deleteLater()

        with contextlib.suppress(Exception):
            self.save_canvas_state()
        self.update()

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
        self.console_height = max(
            80, min(self.height() - 40, self.console_height + delta_px)
        )
        self.position_console_widgets()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)

        # Dot grid
        left = -self.offset.x() / self.scale
        top = -self.offset.y() / self.scale
        right = left + self.width() / self.scale
        bottom = top + self.height() / self.scale

        x_start = int(left // self.grid_size * self.grid_size)
        y_start = int(top // self.grid_size * self.grid_size)

        dot_size = max(1.5, 1.5 / self.scale)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.dot_color)

        for x in range(x_start, int(right) + self.grid_size, self.grid_size):
            for y in range(y_start, int(bottom) + self.grid_size, self.grid_size):
                painter.drawEllipse(
                    QPointF(float(x), float(y)), dot_size, dot_size
                )

        painter.resetTransform()
        self.draw_coordinates(painter)

        for connection in self.connections:
            connection.draw(painter)
        if self.pending_connection:
            self.pending_connection.draw(painter)

    def draw_coordinates(self, painter: QPainter):
        painter.setPen(QColor("#2C3352"))
        painter.setFont(QFont("Poppins", 9))
        canvas_pos = self.mapFromGlobal(self.cursor().pos())
        logical_pos = QPointF(
            (canvas_pos.x() - self.offset.x()) / self.scale,
            -(canvas_pos.y() - self.offset.y()) / self.scale,
        )
        painter.drawText(
            10,
            self.height() - 10,
            f"X: {int(logical_pos.x())}  Y: {int(logical_pos.y())}",
        )

    def reset_all_node_statuses(self):
        for node in self.nodes.values():
            if hasattr(node, "reset_execution_status"):
                node.reset_execution_status()

    def run_all_nodes(self, *args):
        self.show_console()
        try:
            self.output_console.clear_output()
        except Exception:
            self.output_console.clear()

        self.output_console.appendPlainText("Starting automation run...")

        bus = get_performance_bus()
        node_exec_times = {}

        def _on_error(node, error):
            msg = f"[Error] Error in node {getattr(node, 'title', '?')}: see console for details"
            self.output_console.appendError(msg)

        def _on_node_executed(node, duration_s):
            node_exec_times[getattr(node, "title", str(id(node)))] = duration_s
            msg = f"[OK] Executed node: {node.title} ({duration_s:.2f}s)"
            self.output_console.appendPlainText(msg)

        def _on_log(line, stream_type):
            if stream_type and stream_type.lower() in ("stderr", "error"):
                self.output_console.appendError(line)
            else:
                self.output_console.appendPlainText(line)

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
                self.output_console.appendPlainText("Automation completed.")
                self.output_console.appendPlainText(f"Summary: {result}")
                self.position_console_widgets()
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
        if result is not None:
            self.output_console.appendPlainText("Automation completed.")
            self.output_console.appendPlainText(f"Summary: {result}")
            self.position_console_widgets()

    def _apply_zoom(self, zoom_factor, mouse_pos):
        old_scale = self.scale
        self.scale *= zoom_factor
        self.scale = max(0.1, min(self.scale, 10.0))
        before_scale = (mouse_pos - self.offset) / old_scale
        after_scale = (mouse_pos - self.offset) / self.scale
        self.offset = QPointF(self.offset) + (after_scale - before_scale) * self.scale
        self.update()
        for node in self.nodes.values():
            node.update_position()

    def event(self, event):
        if isinstance(event, QNativeGestureEvent):
            gtype = event.gestureType()
            if gtype == Qt.NativeGestureType.ZoomNativeGesture:
                factor = 1.0 + event.value()
                self._apply_zoom(factor, event.position())
                return True
            elif gtype == Qt.NativeGestureType.PanNativeGesture:
                delta = event.delta()
                self.offset += QPointF(delta.x(), delta.y())
                for node in self.nodes.values():
                    node.update_position()
                self.update()
                return True
        return super().event(event)

    def mousePressEvent(self, event: QMouseEvent):
        btn = event.button()
        modifiers = event.modifiers()

        # Canvas panning trigger: Middle Mouse, Alt+Left Drag, or Space+Left Drag
        if btn == Qt.MouseButton.MiddleButton or (
            btn == Qt.MouseButton.LeftButton
            and (self.space_held or bool(modifiers & Qt.KeyboardModifier.AltModifier))
        ):
            self.is_panning = True
            self.drag_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        if btn == Qt.MouseButton.LeftButton:
            clicked_on_node = any(
                node.geometry().contains(node.mapFromParent(event.pos()))
                for node in self.nodes.values()
            )
            if not clicked_on_node and self.selected_node:
                self.selected_node.selected = False
                self.selected_node.update()
                self.selected_node = None

        if btn == Qt.MouseButton.RightButton:
            name, ok = QInputDialog.getText(self, "Create Node", "Enter node name:")
            if ok and name:
                node = NodeWidget(name, self)
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

        if self.is_panning and self.drag_start:
            delta = QPointF(event.pos() - self.drag_start)
            self.offset += delta
            self.drag_start = event.pos()
            for node in self.nodes.values():
                node.update_position()
            self.update()
            return

        if self.pending_connection:
            self.pending_connection.set_end_point(event.position())
            self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.is_panning:
            self.is_panning = False
            self.drag_start = None
            if self.space_held:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.space_held = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.space_held = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        modifiers = event.modifiers()
        pixel_delta = event.pixelDelta()
        angle_delta = event.angleDelta()

        is_ctrl_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        is_shift_pressed = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

        has_pixel_delta = not pixel_delta.isNull() and (
            pixel_delta.x() != 0 or pixel_delta.y() != 0
        )
        has_horiz_angle = angle_delta.x() != 0

        if is_ctrl_pressed:
            # Ctrl + Scroll / Wheel = Zoom centered at cursor
            dy = pixel_delta.y() if has_pixel_delta else angle_delta.y()
            if dy != 0:
                factor = 1.15 if dy > 0 else (1 / 1.15)
                self._apply_zoom(factor, event.position())
        elif has_pixel_delta or has_horiz_angle or is_shift_pressed:
            # Trackpad 2-finger scroll or Shift+Wheel = Pan canvas
            if has_pixel_delta:
                dx = pixel_delta.x()
                dy = pixel_delta.y()
            elif is_shift_pressed:
                dx = angle_delta.y() / 4.0
                dy = 0.0
            else:
                dx = angle_delta.x() / 4.0
                dy = angle_delta.y() / 4.0

            self.offset += QPointF(dx, dy)
            for node in self.nodes.values():
                node.update_position()
            self.update()
        else:
            # Traditional physical mouse wheel notch scroll
            dy = angle_delta.y()
            if dy != 0:
                if abs(dy) >= 120:
                    factor = 1.1 if dy > 0 else (1 / 1.1)
                    self._apply_zoom(factor, event.position())
                else:
                    self.offset += QPointF(0, dy / 2.0)
                    for node in self.nodes.values():
                        node.update_position()
                    self.update()

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

    def start_connection(self, port_widget):
        self.connection_start_port = port_widget
        self.pending_connection = BezierConnection(start_port=port_widget, canvas=self)
        self.update()

    def complete_connection(self, target_port):
        if not (self.pending_connection and self.connection_start_port):
            self.cancel_connection()
            return

        start_port = self.connection_start_port
        if start_port == target_port or start_port.node == target_port.node:
            self.cancel_connection()
            return
        if start_port.type == target_port.type:
            self.cancel_connection()
            return

        self.pending_connection.end_port = target_port
        self.pending_connection.finalize()
        self.connections.append(self.pending_connection)
        self.pending_connection = None
        self.connection_start_port = None
        self.save_canvas_state()
        self.update()

    def cancel_connection(self):
        self.pending_connection = None
        self.connection_start_port = None
        self.update()

    def handle_port_click(self, port):
        port_type = getattr(port, "type", "")
        if self.pending_connection is None and port_type == "output":
            self.start_connection(port)
        elif self.pending_connection is not None and port_type == "input":
            self.complete_connection(port)
        elif self.pending_connection is not None and port_type == "output":
            self.pending_connection.start_port = port
            self.update()

    def get_port_at(self, pos):
        try:
            qpos = pos.toPoint() if hasattr(pos, "toPoint") else pos
            w = self.childAt(qpos)
            if w and hasattr(w, "node") and hasattr(w, "type"):
                return w
            return None
        except Exception:
            return None

    def update_node_position(self, node_id, logical_pos):
        node = self.nodes.get(node_id)
        if not node:
            return
        node.logical_pos = logical_pos
        if hasattr(node, "update_position"):
            node.update_position()

    def save_canvas_state(self):
        os.makedirs(os.path.expanduser("~/.nodebox/automations"), exist_ok=True)
        nodes_data = []
        for node in self.nodes.values():
            outputs_data = getattr(node, "outputs", {})
            if isinstance(outputs_data, list):
                outputs_data = dict.fromkeys(outputs_data)

            nodes_data.append(
                {
                    "id": node.id,
                    "name": node.title,
                    "position": [int(node.logical_pos.x()), int(node.logical_pos.y())],
                    "code": getattr(node, "code", ""),
                    "outputs": outputs_data,
                }
            )

        connections_data = []
        for connection in self.connections:
            from_port = connection.start_port
            to_port = connection.end_port
            if not from_port or not to_port:
                continue

            connections_data.append(
                {
                    "from_node_id": from_port.node.id,
                    "from_port_type": from_port.type,
                    "to_node_id": to_port.node.id,
                    "to_port_type": to_port.type,
                }
            )

        automation_data = {"nodes": nodes_data, "connections": connections_data}
        path = os.path.expanduser(f"~/.nodebox/automations/{self.automation_name}.json")
        with open(path, "w") as f:
            json.dump(automation_data, f, indent=4)

    def load_canvas_state(self):
        for node_data in self.automation_data.get("nodes", []):
            node_id = node_data["id"]
            title = node_data["name"]
            pos = QPointF(*node_data["position"])
            code = node_data.get("code", "")
            outputs = node_data.get("outputs", {})

            if isinstance(outputs, list):
                outputs = dict.fromkeys(outputs)

            node = NodeWidget(title=title, canvas=self, pos=pos)
            node.id = node_id
            self.nodes[node_id] = node
            node.code = code
            node.outputs = outputs
            node.update_position()
            node.show()

        for conn_data in self.automation_data.get("connections", []):
            from_node = self.nodes.get(conn_data["from_node_id"])
            to_node = self.nodes.get(conn_data["to_node_id"])

            if not from_node or not to_node:
                continue

            from_port = getattr(from_node, f'{conn_data["from_port_type"]}_port', None)
            to_port = getattr(to_node, f'{conn_data["to_port_type"]}_port', None)

            if from_port and to_port:
                connection = BezierConnection(start_port=from_port, canvas=self)
                connection.end_port = to_port
                connection.finalize()
                self.connections.append(connection)
                self.update()

    def center_initial_view(self):
        if getattr(self, "initial_centering_done", False):
            return

        try:
            if self.nodes:
                xs = [n.logical_pos.x() for n in self.nodes.values()]
                ys = [n.logical_pos.y() for n in self.nodes.values()]
                minx, maxx = min(xs), max(xs)
                miny, maxy = min(ys), max(ys)
                logical_center = QPointF((minx + maxx) / 2.0, (miny + maxy) / 2.0)
                screen_cx = self.width() / 2.0
                screen_cy = self.height() / 2.0
                self.offset = (
                    QPointF(screen_cx, screen_cy) - logical_center * self.scale
                )
            else:
                self.offset = QPointF(self.width() / 2.0, self.height() / 2.0)

            for node in self.nodes.values():
                node.update_position()

            self.initial_centering_done = True
            self.update()
        except Exception as e:
            print("[CanvasWidget] center_initial_view error:", e)

    def select_node(self, node):
        if getattr(self, "selected_node", None) and self.selected_node != node:
            try:
                self.selected_node.selected = False
                self.selected_node.update()
            except Exception:
                pass

        self.selected_node = node
        node.selected = True
        node.update()

        try:
            node.raise_()
            if hasattr(node, "input_port") and node.input_port:
                node.input_port.raise_()
            if hasattr(node, "output_port") and node.output_port:
                node.output_port.raise_()
        except Exception:
            pass

        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.console_visible:
            self.position_console_widgets()


__all__ = ["CanvasWidget", "ResizeHandle"]
