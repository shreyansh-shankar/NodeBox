from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton #type: ignore
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QColor, QFontMetrics, QPainterPath #type: ignore
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal #type: ignore

import uuid

from ui.ports import PortWidget

class NodeWidget(QWidget):

    def __init__(self, title, canvas, pos=None, inputs=None, outputs=None):
        super().__init__(canvas)
        self.id = str(uuid.uuid4())
        self.canvas = canvas
        self.title = title
        self.logical_pos = pos if pos else QPointF(0, 0)
        self.setFixedSize(180, 100)

        # to track if the node is selected or not
        self.selected = False
        
        # to track if the node itself is being dragged or not
        self.is_dragging = False
        self.drag_offset = QPointF()

        self.setMouseTracking(True)

        # Create input and output ports as siblings (parent is canvas, not self)
        self.input_port = PortWidget(parent=canvas, node=self, type="input")
        self.input_port.show()
        self.input_port.raise_()
        self.input_port.clicked.connect(canvas.handle_port_click)
        self.output_port = PortWidget(parent=canvas, node=self, type="output")
        self.output_port.show()
        self.output_port.raise_()
        self.output_port.clicked.connect(canvas.handle_port_click)

        # --- Buttons (hidden by default) ---
        self.delete_button = QPushButton("x", self)
        self.delete_button.setFixedSize(25, 25)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #aa0000;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
        """)
        self.delete_button.hide()

        self.open_button = QPushButton("O", self)
        self.open_button.setFixedSize(25, 25)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #0066aa;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 15px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
        """)
        self.open_button.hide()

        self.delete_button.raise_()
        self.open_button.raise_()

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

        # Position ports (relative to screen position, not local position)
        node_rect = self.geometry()

        # Left center for input
        input_x = node_rect.left() - self.input_port.width() // 2
        input_y = node_rect.top() + node_rect.height() // 2 - self.input_port.height() // 2
        self.input_port.move(input_x, input_y)

        # Right center for output
        output_x = node_rect.right() - self.output_port.width() // 2
        output_y = node_rect.top() + node_rect.height() // 2 - self.output_port.height() // 2
        self.output_port.move(output_x, output_y)

        # Optional: Resize port if zoom is applied
        port_scale = scale
        self.input_port.resize(self.input_port.sizeHint() * port_scale)
        self.output_port.resize(self.output_port.sizeHint() * port_scale)

        # Position buttons at bottom-right corner
        margin = 10
        bx = self.width() - self.delete_button.width() - margin
        by = self.height() - self.delete_button.height() - margin
        self.delete_button.move(bx, by)

        self.open_button.move(bx - self.open_button.width() - margin, by)
    
    def on_delete_clicked(self):
        self.canvas.delete_node(self)

    def paintEvent(self, event):
        super().paintEvent(event)
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

        # Show/hide buttons based on selection
        if self.selected:
            self.delete_button.show()
            self.open_button.show()
        else:
            self.delete_button.hide()
            self.open_button.hide()
    
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