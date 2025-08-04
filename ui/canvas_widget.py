from PyQt6.QtWidgets import QWidget, QInputDialog #type: ignore
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent, QKeyEvent, QWheelEvent, QFont, QPainterPath #type: ignore
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QTimer #type: ignore

import os, json

from ui.node import NodeWidget

class CanvasWidget(QWidget):
    def __init__(self, automation_name=None, automation_data=None, parent=None):
        super().__init__(parent)
        self.automation_name = automation_name
        self.automation_data = automation_data or {"nodes": [], "connections": []}

        self.grid_size = 50
        self.grid_color = QColor("#404040")  # Light gray grid
        self.bg_color = QColor("#202020")

        self.nodes = {}
        self.connections = []

        self.offset = QPointF(0, 0)     # Total pan offset
        self.drag_start = None
        self.space_held = False
        self.last_mouse_pos = QPointF()

        self.selected_node = None

        self.initial_centering_done = False
        QTimer.singleShot(0, self.center_initial_view)

        self.scale = 1.0

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.dragging_connection = False
        self.connection_start_pos = None
        self.connection_current_pos = None
        self.connection_start_port = None

        self.load_canvas_state()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)

        # Setup zoom and pan
        painter.translate(self.offset)
        painter.scale(self.scale, self.scale)

        pen = QPen(self.grid_color)
        pen.setWidth(max(1, int(1 / self.scale)))
        painter.setPen(pen)

        # Calculate grid spacing
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

        #Draw coordinates
        painter.resetTransform()
        self.draw_coordinates(painter)

        # Draw dragging Bezier connection if active
        if self.dragging_connection and self.connection_start_pos and self.connection_current_pos:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor(200, 200, 0), 2))

            start = self.connection_start_pos
            end = self.connection_current_pos

            # Choose control points based on the drag start port
            if self.connection_start_port == 'output':
                cp1 = QPointF(start.x() + 40, start.y())
                cp2 = QPointF(end.x() - 40, end.y())
            elif self.connection_start_port == 'input':
                cp1 = QPointF(start.x() - 40, start.y())
                cp2 = QPointF(end.x() + 40, end.y())
            else:
                cp1 = start
                cp2 = end

            path = QPainterPath()
            path.moveTo(QPointF(start))
            path.cubicTo(cp1, cp2, QPointF(end))
            painter.drawPath(path)

            painter.setPen(QPen(QColor(200, 200, 0), 2, Qt.PenStyle.SolidLine))
            painter.drawPath(path)

    def update_node_position(self, node_id, logical_pos):
        self.save_canvas_state()

    def draw_coordinates(self, painter: QPainter):
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Arial", 10))
        canvas_pos = self.mapFromGlobal(self.cursor().pos())
        canvas_pos = QPointF(canvas_pos)

        logical_pos = QPointF(
            (canvas_pos.x() - self.offset.x()) / self.scale,
            -(canvas_pos.y() - self.offset.y()) / self.scale  # Flip Y axis
        )
        text = f"X: {int(logical_pos.x())}  Y: {int(logical_pos.y())}"
        painter.drawText(10, self.height() - 10, text)
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_on_node = any(node.geometry().contains(node.mapFromParent(event.pos())) for node in self.nodes.values())
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

    def mouseMoveEvent(self, event: QMouseEvent):
        self.last_mouse_pos = event.position()

        if event.buttons() & Qt.MouseButton.LeftButton and self.space_held and self.drag_start:
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

    def start_connection_drag(self, port_type, start_pos):
        self.dragging_connection = True
        self.connection_start_port = port_type
        self.connection_start_pos = start_pos
        self.connection_current_pos = start_pos
        self.update()

    def update_connection_drag(self, current_pos):
        if self.dragging_connection:
            self.connection_current_pos = current_pos
            self.update()

    def end_connection_drag(self):
        self.dragging_connection = False
        self.connection_start_pos = None
        self.connection_current_pos = None
        self.connection_start_port = None
        self.update()

    def select_node(self, node):
        # Deselect previous
        if self.selected_node and self.selected_node != node:
            self.selected_node.selected = False
            self.selected_node.update()

        # Select new
        self.selected_node = node
        node.selected = True
        node.update()
    
    def save_canvas_state(self):
        os.makedirs(os.path.expanduser("~/.nodebox/automations"), exist_ok=True)

        nodes_data = []
        for node in self.nodes.values():
            nodes_data.append({
                "id": node.id,
                "name": node.title,
                "position": [int(node.logical_pos.x()), int(node.logical_pos.y())]
            })

        connections_data = []
        for conn in self.connections:
            connections_data.append({
                "from": conn.output_port.node.id,
                "to": conn.input_port.node.id
            })

        automation_data = {
            "nodes": nodes_data,
            "connections": connections_data
        }

        path = os.path.expanduser(f"~/.nodebox/automations/{self.automation_name}.json")
        with open(path, 'w') as f:
            json.dump(automation_data, f, indent=4)

    def add_connection(self, from_node, to_node):
        print(f"[DEBUG] Connection added from {from_node.title} to {to_node.title}")
        # TODO: Implement actual connection object/visuals


    def load_canvas_state(self):
        # Load nodes
        for node_data in self.automation_data.get("nodes", []):
            node_id = node_data["id"]
            title = node_data["name"]
            pos = QPointF(*node_data["position"])

            node = NodeWidget(title=title, canvas=self, pos=pos)
            node.id = node_id
            self.nodes[node_id] = node
            node.update_position()
            node.show()

        # Load connections
        for conn in self.automation_data.get("connections", []):
            from_id = conn["from"]
            to_id = conn["to"]

            from_node = self.nodes.get(from_id)
            to_node = self.nodes.get(to_id)

            if from_node and to_node:
                self.add_connection(from_node, to_node)
