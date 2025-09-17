from PyQt6.QtWidgets import QWidget #type: ignore
from PyQt6.QtGui import QPainter, QColor #type: ignore
from PyQt6.QtCore import Qt, QSize, pyqtSignal #type: ignore

class PortWidget(QWidget):
    clicked = pyqtSignal(object)

    def __init__(self, parent=None, node=None, type = None):
        super().__init__(parent)
        self.type = type
        self.radius = 10
        self.node = node

        self.default_color = QColor("#D1D1D1")
        self.hover_color = QColor("#FFFFFF")
        self.clicked_color = QColor("#FFD700")

        self.color = self.default_color
        self.is_hovered = False
        self.is_pressed = False

        self.setFixedSize(QSize(self.radius * 2, self.radius * 2))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.radius * 2, self.radius * 2)

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
