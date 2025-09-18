from PyQt6.QtWidgets import QWidget, QInputDialog, QDialog #type: ignore
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent, QKeyEvent, QWheelEvent, QFont, QPainterPath, QTouchEvent #type: ignore
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QTimer, QEvent #type: ignore

from automation_manager.node import NodeWidget
from utils.node_runner import execute_all_nodes

class CanvasWidget(QWidget):
    def __init__(self, automation_name=None, automation_data=None, parent=None):
        super().__init__(parent)
        self.automation_name = automation_name
        self.automation_data = automation_data or {"nodes": [], "connections": []}

        self.grid_size = 50
        self.grid_color = QColor("#404040")  # Light gray grid
        self.bg_color = QColor("#202020")

        self.nodes = {}

        self.offset = QPointF(0, 0)     # Total pan offset
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
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
        self.grabGesture(Qt.GestureType.PanGesture)
        self.grabGesture(Qt.GestureType.PinchGesture)

        # port and connection related logic
        self.pending_connection = None  
        self.connection_start_port = None

        self.connections = []

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

        # Draw all finalized connections
        for connection in self.connections:
            connection.draw(painter)

        # connection related logic
        if self.pending_connection:
            self.pending_connection.draw(painter)

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

    def event(self, event):
        if event.type() == QEvent.Gesture:
            return self.gestureEvent(event)
        if event.type() in (QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate, QEvent.Type.TouchEnd):
            return self.touchEvent(event)
        return super().event(event)

    def touchEvent(self, event: QTouchEvent):
        touch_points = event.touchPoints()
        if len(touch_points) == 1:
            # Single finger touch for panning when space is held
            touch_point = touch_points[0]
            if event.type() == QEvent.Type.TouchBegin and self.space_held:
                self.drag_start = touch_point.pos()
            elif event.type() == QEvent.Type.TouchUpdate and self.space_held and self.drag_start:
                delta = touch_point.pos() - touch_point.lastPos()
                self.offset += delta
                for node in self.nodes.values():
                    node.update_position()
                self.update()
            elif event.type() == QEvent.Type.TouchEnd:
                self.drag_start = None
            event.accept()
            return True
        elif len(touch_points) == 2:
            # Two finger touch for panning or zooming
            p1 = touch_points[0]
            p2 = touch_points[1]

            # Calculate current and last positions midpoint
            current_pos = (p1.pos() + p2.pos()) / 2
            last_pos = (p1.lastPos() + p2.lastPos()) / 2
            delta = current_pos - last_pos

            # Check if CTRL is pressed for zooming
            modifiers = event.modifiers()
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                # Zoom based on distance change between two points
                current_dist = (p1.pos() - p2.pos()).manhattanLength()
                last_dist = (p1.lastPos() - p2.lastPos()).manhattanLength()
                if last_dist != 0:
                    scale_factor = current_dist / last_dist
                    old_scale = self.scale
                    self.scale *= scale_factor
                    self.scale = max(0.1, min(self.scale, 10.0))

                    # Adjust offset to keep zoom centered at midpoint
                    before_scale = (current_pos - self.offset) / old_scale
                    after_scale = (current_pos - self.offset) / self.scale
                    self.offset += (after_scale - before_scale) * self.scale

                    for node in self.nodes.values():
                        node.update_position()
                    self.update()
            else:
                # Pan the canvas by delta
                self.offset += delta
                for node in self.nodes.values():
                    node.update_position()
                self.update()

            event.accept()
            return True
        return super().event(event)

    def gestureEvent(self, event):
        pan = event.gesture(Qt.GestureType.PanGesture)
        if pan and pan.state() == Qt.GestureState.GestureUpdated:
            delta = pan.delta()
            self.offset += delta
            for node in self.nodes.values():
                node.update_position()
            self.update()

        pinch = event.gesture(Qt.GestureType.PinchGesture)
        if pinch and pinch.state() == Qt.GestureState.GestureUpdated:
            scale_factor = pinch.scaleFactor()
            old_scale = self.scale
            self.scale *= scale_factor
            self.scale = max(0.1, min(self.scale, 10.0))

            center = pinch.centerPoint()
            before_scale = (center - self.offset) / old_scale
            after_scale = (center - self.offset) / self.scale
            self.offset += (after_scale - before_scale) * self.scale

            for node in self.nodes.values():
                node.update_position()
            self.update()

        return True

    def center_initial_view(self):
        if not self.initial_centering_done:
            self.offset = QPointF(self.width() / 2, self.height() / 2)
            self.initial_centering_done = True
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
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        node_type = event.mimeData().text()
        pos = (event.position() - self.offset) / self.scale  # convert to logical coords

        if node_type == "Custom Node":
            name, ok = QInputDialog.getText(self, "Create Node", "Enter node name:")
            if ok and name:
                node = NodeWidget(name, self, pos=QPointF(pos))
            else:
                return
        else:
            node = NodeWidget(node_type, self, pos=QPointF(pos))

        # ---- critical: store node and initialize ----
        self.nodes[node.id] = node
        node.logical_pos = QPointF(pos)
        node.update_position()
        node.show()

        self.save_canvas_state()
        event.acceptProposedAction()

    def run_all_nodes(self, *args):
        print("Running all nodes...")
        output = execute_all_nodes(self.nodes.values(), self.connections)
        print(output)
        self.save_canvas_state()