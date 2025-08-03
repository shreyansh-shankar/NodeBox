from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPainterPath, QPen, QColor
from PyQt6.QtCore import QPointF

class GraphSceneWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging_connection = False
        self.connection_start_pos = None
        self.connection_start_port = None
        self.connection_current_pos = None

    def addNode(self, node):
        node.startConnectionDrag.connect(self.start_connection_drag)
        self.layout().addWidget(node)  # Or however you're adding nodes

    def start_connection_drag(self, port_type, start_pos):
        self.dragging_connection = True
        self.connection_start_port = port_type
        self.connection_start_pos = start_pos
        self.connection_current_pos = start_pos
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if self.dragging_connection:
            self.connection_current_pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_connection = False
        self.connection_start_pos = None
        self.connection_current_pos = None
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.dragging_connection and self.connection_start_pos and self.connection_current_pos:
            start = QPointF(self.connection_start_pos)
            end = QPointF(self.connection_current_pos)

            cp1 = QPointF(start.x() + 40, start.y())
            cp2 = QPointF(end.x() - 40, end.y())

            path = QPainterPath()
            path.moveTo(start)
            path.cubicTo(cp1, cp2, end)

            painter.setPen(QPen(QColor(200, 200, 0), 2))
            painter.drawPath(path)
