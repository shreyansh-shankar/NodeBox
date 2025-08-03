from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QColor, QFontMetrics
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF

class NodeWidget(QWidget):
    def __init__(self, title, canvas, pos=None, inputs=None, outputs=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.title = title
        self.logical_pos = pos if pos else QPointF(0, 0)
        self.setFixedSize(150, 80)

    def update_position(self):
        """ Update screen position based on canvas pan and zoom """
        scale = self.canvas.scale
        offset = self.canvas.offset
        screen_pos = self.logical_pos * scale + offset
        self.move(screen_pos.toPoint())
        self.resize(self.sizeHint() * scale)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background rectangle
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setBrush(QColor(34, 34, 34))
        painter.setPen(QPen(QColor(136, 136, 136), 2))
        painter.drawRoundedRect(rect, 10, 10)

        # Draw centered text
        painter.setPen(QColor('white'))
        font = QFont('Arial', 15)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        text_rect = QRectF(rect)
        text_height = QFontMetrics(font).height()
        text_rect.setTop(rect.top() + (rect.height() - text_height) / 2)

        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self.title)