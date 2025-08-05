from PyQt6.QtWidgets import QWidget #type: ignore
from PyQt6.QtGui import QPainterPath, QColor, QPen #type: ignore
from PyQt6.QtCore import Qt, QPointF #type: ignore

class Connection:
    def __init__(self, start_port, end_port=None):
        self.start_port = start_port
        self.end_port = end_port
        self.current_mouse_pos = None  # For pending connection following cursor

    def draw(self, painter):
        start = self.start_port.scene_pos()
        end = (
            self.end_port.scene_pos()
            if self.end_port
            else self.current_mouse_pos
        )

        if not start or not end:
            return

        path = QPainterPath(QPointF(start))
        ctrl1 = QPointF(start.x() + 100, start.y())
        ctrl2 = QPointF(end.x() - 100, end.y())
        path.cubicTo(ctrl1, ctrl2, QPointF(end))

        painter.setPen(QPen(Qt.black, 2))
        painter.drawPath(path)
