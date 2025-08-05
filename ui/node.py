from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout #type: ignore
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QColor, QFontMetrics, QPainterPath #type: ignore
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal #type: ignore

import uuid

class NodeWidget(QWidget):

    startConnectionDrag = pyqtSignal(str, QPoint)

    def __init__(self, title, canvas, pos=None, inputs=None, outputs=None):
        super().__init__(canvas)
        self.id = str(uuid.uuid4())
        self.canvas = canvas
        self.title = title
        self.logical_pos = pos if pos else QPointF(0, 0)
        self.setFixedSize(150, 80)

        # to track if the node is selected or not
        self.selected = False
        
        # to track if the node itself is being dragged or not
        self.is_dragging = False
        self.drag_offset = QPointF()

        # to track if a connection is tried to be dragged
        self.dragging = False
        self.drag_start_port = None

        # Port-related state
        self.input_port_pos = None
        self.output_port_pos = None
        
        self.port_radius = 12

        # to track which port is hovered currently of the node
        self.hovered_port = None

        self.setMouseTracking(True)

    # on mouse enter or leave it updates visual feedback
    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.hovered_port = None
        self.update()

    # updates position on the canvas when it is zoomed or panned
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

        # static ui rendering of the node
        rect = self.rect().adjusted(1, 1, -1, -1)

        if self.selected:
            border_color = QColor(255, 215, 0)
        else:
            border_color = QColor(136, 136, 136)

        painter.setBrush(QColor(34, 34, 34))
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(rect, 10, 10)

        painter.setPen(QColor('white'))
        font = QFont('Arial', 15)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        text_rect = QRectF(rect)
        text_height = QFontMetrics(font).height()
        text_rect.setTop(rect.top() + (rect.height() - text_height) / 2)

        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self.title)
    
    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        # to check if we are trying to drag the node itself
        if self.is_dragging and self.selected:
            new_pos = self.mapToParent(event.pos() - self.drag_offset)
            
            canvas_offset = self.canvas.offset
            scale = self.canvas.scale
            logical_pos = (QPointF(new_pos) - canvas_offset) / scale

            self.logical_pos = logical_pos
            self.canvas.update_node_position(self.id, self.logical_pos)
            self.update_position()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # to initiate the dragging of the node itself on the canvas
            self.canvas.select_node(self)
            self.is_dragging = True
            self.drag_offset = event.pos()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.canvas.save_canvas_state()