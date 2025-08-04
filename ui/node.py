from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QColor, QFontMetrics, QPainterPath
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal

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

        self.selected = False
        
        self.is_dragging = False
        self.drag_offset = QPointF()

        self.dragging = False
        self.drag_start_port = None
        self.drag_current_pos = None

        # Port-related state
        self.input_port_pos = None
        self.output_port_pos = None
        self.port_radius = 12
        self.hovered_port = None  # 'input' or 'output'

        self.setMouseTracking(True)

    def is_in_input_port(self, pos: QPoint):
        return (pos - self.input_port_pos).manhattanLength() < self.port_radius


    def is_in_output_port(self, pos: QPoint):
        port_center = QPoint(self.width(), self.height() // 2)
        return (pos - self.output_port_pos).manhattanLength() < self.port_radius

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.hovered_port = None
        self.update()


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

        if self.selected:
            border_color = QColor(255, 215, 0)
        else:
            border_color = QColor(136, 136, 136)

        painter.setBrush(QColor(34, 34, 34))
        painter.setPen(QPen(border_color, 2))
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

        # Draw input port (left)
        self.input_port_pos = QPoint(self.port_radius - 5, rect.center().y())
        painter.setBrush(QColor(200, 80, 80) if self.hovered_port == 'input' else QColor(120, 120, 120))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.input_port_pos, self.port_radius, self.port_radius)

        # Draw output port (right)
        self.output_port_pos = QPoint(rect.width() - self.port_radius + 5, rect.center().y())
        painter.setBrush(QColor(80, 200, 80) if self.hovered_port == 'output' else QColor(120, 120, 120))
        painter.drawEllipse(self.output_port_pos, self.port_radius, self.port_radius)

    
    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        if self.is_dragging and self.selected:
            new_pos = self.mapToParent(event.pos() - self.drag_offset)
            
            canvas_offset = self.canvas.offset
            scale = self.canvas.scale
            logical_pos = (QPointF(new_pos) - canvas_offset) / scale

            self.logical_pos = logical_pos
            self.canvas.update_node_position(self.id, self.logical_pos)
            self.update_position()

        if self.dragging:
            scene_pos = self.mapToParent(pos)
            self.canvas.update_connection_drag(scene_pos)
        else:
            prev_hover = self.hovered_port
            if self.is_in_input_port(pos):
                self.hovered_port = 'input'
            elif self.is_in_output_port(pos):
                self.hovered_port = 'output'
            else:
                self.hovered_port = None

            if self.hovered_port != prev_hover:
                self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_in_input_port(event.pos()):
                self.dragging = True
                self.drag_start_port = 'input'
                scene_pos = self.mapToParent(self.input_port_pos)
                self.canvas.start_connection_drag('input', scene_pos)
            elif self.is_in_output_port(event.pos()):
                self.dragging = True
                self.drag_start_port = 'output'
                scene_pos = self.mapToParent(self.output_port_pos)
                self.canvas.start_connection_drag('output', scene_pos)
            else:
                self.canvas.select_node(self)
                self.is_dragging = True
                self.drag_offset = event.pos()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.canvas.save_canvas_state()

        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.canvas.end_connection_drag()
            self.dragging = False
            self.drag_start_port = None
            self.drag_current_pos = None
            self.update()