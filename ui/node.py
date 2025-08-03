from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, QPointF

class NodeWidget(QWidget):
    def __init__(self, title, canvas, pos=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.title = title
        self.logical_pos = pos if pos else QPointF(0, 0)
        self.setFixedSize(150, 80)
        self._initUI()

    def _initUI(self):
        self.label = QLabel(self.title, self)
        self.label.move(10, 10)
        self.setStyleSheet("background-color: #333333; color: white; border: 1px solid #888888;")

    def update_position(self):
        """ Update screen position based on canvas pan and zoom """
        scale = self.canvas.scale
        offset = self.canvas.offset
        screen_pos = self.logical_pos * scale + offset
        self.move(screen_pos.toPoint())
        self.resize(self.sizeHint() * scale)

    def paintEvent(self, event):
        # Optional custom node painting
        painter = QPainter(self)
        painter.setBrush(Qt.GlobalColor.lightGray)
        painter.drawRect(self.rect())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.title)