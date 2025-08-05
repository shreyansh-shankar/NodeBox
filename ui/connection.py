from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor #type: ignore
from PyQt6.QtCore import QPointF, Qt #type: ignore


class BezierConnection:
    def __init__(self, start_port, canvas):
        self.start_port = start_port
        self.end_port = None
        self.canvas = canvas
        self.end_point = None  # will be updated during drag
        self.end_port = None

    def set_end_point(self, point):
        self.end_point = point

    def finalize(self):
        if self.end_port:
            self.end_point = None

    def draw(self, painter):
        if self.end_port:
            end_pos = self.end_port.mapTo(self.canvas, self.end_port.rect().center())
        elif self.end_point:
            end_pos = self.end_point
        else:
            return  # Nothing to draw

        start_pos = self.start_port.mapTo(self.canvas, self.start_port.rect().center())

        # Convert to QPointF for QPainterPath
        start_f = QPointF(start_pos)
        end_f = QPointF(end_pos)

        path = QPainterPath(start_f)

        dx = (end_f.x() - start_f.x()) * 0.5

        c1 = QPointF(start_f.x() + dx, start_f.y())
        c2 = QPointF(end_f.x() - dx, end_f.y())

        path.cubicTo(c1, c2, end_f)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#FFD700"), 2))
        painter.drawPath(path)


    def get_port_pos(self, port):
        if port:
            global_pos = port.mapTo(self.canvas, port.rect().center())
            return QPointF(global_pos)
        return None