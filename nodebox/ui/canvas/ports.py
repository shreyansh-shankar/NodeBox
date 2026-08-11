from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class PortWidget(QWidget):
    clicked = pyqtSignal(object)

    def __init__(self, parent=None, node=None, type=None):
        super().__init__(parent)
        self.type = type
        self.radius = 8
        self.node = node

        self.default_color = QColor("#818CF8")
        self.hover_color = QColor("#A5B4FC")
        self.clicked_color = QColor("#10B981")
        self.border_color = QColor("#121418")

        self.color = self.default_color
        self.is_hovered = False
        self.is_pressed = False

        self.setFixedSize(QSize(self.radius * 2 + 4, self.radius * 2 + 4))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Outer glow/border
        if self.is_hovered:
            painter.setPen(QPen(QColor("#6366F1"), 2))
        else:
            painter.setPen(QPen(self.border_color, 2))

        painter.setBrush(self.color)
        painter.drawEllipse(2, 2, self.radius * 2, self.radius * 2)

    def enterEvent(self, event):
        self.is_hovered = True
        self.color = self.hover_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update()

    def leaveEvent(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.color = self.default_color
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = True
            self.color = self.clicked_color
            self.update()
            self.clicked.emit(self)

    def mouseReleaseEvent(self, event):
        if self.is_hovered:
            self.color = self.hover_color
        else:
            self.color = self.default_color
        self.is_pressed = False
        self.update()


__all__ = ["PortWidget"]
