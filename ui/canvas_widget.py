from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QMouseEvent, QKeyEvent, QWheelEvent, QFont
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_size = 50
        self.grid_color = QColor("#404040")  # Light gray grid
        self.bg_color = QColor("#202020")

        self.offset = QPointF(0, 0)     # Total pan offset
        self.drag_start = None
        self.space_held = False
        self.last_mouse_pos = QPointF()

        self.scale = 1.0

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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

        painter.resetTransform()
        self.draw_coordinates(painter)

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
        if event.button() == Qt.MouseButton.LeftButton and self.space_held:
            self.drag_start = event.pos()
        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and self.space_held):
            self.drag_start = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton and self.space_held and self.drag_start:
            delta = QPointF(event.pos() - self.drag_start)
            self.offset += delta  # Invert to drag canvas
            self.drag_start = event.pos()
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
