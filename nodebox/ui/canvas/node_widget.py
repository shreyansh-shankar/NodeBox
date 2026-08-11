import math
import time
import uuid
from enum import Enum

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import QLineEdit, QMenu, QMessageBox, QPushButton, QWidget

from nodebox.ui.canvas.ports import PortWidget


class ExecutionStatus(Enum):
    """Execution status for nodes during workflow runs."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeWidget(QWidget):
    def __init__(self, title, canvas, pos=None, inputs=None, outputs=None):
        super().__init__(canvas)
        self.id = str(uuid.uuid4())
        self.canvas = canvas
        self.title = title
        self.logical_pos = pos if pos else QPointF(0, 0)
        self.setFixedSize(180, 100)

        self.code = ""
        if outputs is None:
            self.outputs = {}
        elif isinstance(outputs, list):
            self.outputs = dict.fromkeys(outputs)
        elif isinstance(outputs, dict):
            self.outputs = outputs
        else:
            raise TypeError(f"Unexpected outputs type: {type(outputs)}")

        self.selected = False
        self.is_dragging = False
        self.drag_offset = QPointF()

        self.is_editing = False
        self.title_editor = None

        self.execution_status = ExecutionStatus.IDLE
        self.execution_start_time = None
        self.execution_duration = None
        self.execution_error = None

        self.animation_timer = None
        self.animation_counter = 0

        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self.input_port = PortWidget(parent=canvas, node=self, type="input")
        self.input_port.show()
        self.input_port.raise_()
        self.input_port.clicked.connect(canvas.handle_port_click)

        self.output_port = PortWidget(parent=canvas, node=self, type="output")
        self.output_port.show()
        self.output_port.raise_()
        self.output_port.clicked.connect(canvas.handle_port_click)

        self.delete_button = QPushButton("x", self)
        self.delete_button.setFixedSize(25, 25)
        self.delete_button.setStyleSheet(
            """
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
        """
        )
        self.delete_button.hide()

        self.open_button = QPushButton("O", self)
        self.open_button.setFixedSize(25, 25)
        self.open_button.setStyleSheet(
            """
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
        """
        )
        self.open_button.hide()

        self.delete_button.raise_()
        self.open_button.raise_()

        self.open_button.clicked.connect(self.on_open_clicked)
        self.delete_button.clicked.connect(self.on_delete_clicked)

    def validate_node_name(self, new_name):
        if not new_name or not new_name.strip():
            return False, "Node name cannot be empty"

        new_name = new_name.strip()

        for node in self.canvas.nodes.values():
            if node != self and node.title == new_name:
                return False, f"A node with name '{new_name}' already exists"

        return True, new_name

    def start_title_editing(self):
        if self.is_editing:
            return

        self.is_editing = True

        self.title_editor = QLineEdit(self)
        self.title_editor.setText(self.title)
        self.title_editor.setStyleSheet(
            """
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #007acc;
                border-radius: 4px;
                padding: 2px 4px;
                font-family: Arial;
                font-size: 15px;
                font-weight: bold;
                selection-background-color: #007acc;
            }
        """
        )

        title_rect = self.get_title_rect()
        self.title_editor.setGeometry(title_rect)
        self.title_editor.selectAll()

        self.title_editor.returnPressed.connect(self.finish_title_editing)
        self.title_editor.editingFinished.connect(self.cancel_title_editing)
        self.title_editor.installEventFilter(self)

        self.title_editor.show()
        self.title_editor.setFocus()
        self.update()

    def finish_title_editing(self):
        if not self.is_editing or not self.title_editor:
            return

        new_title = self.title_editor.text().strip()
        is_valid, result = self.validate_node_name(new_title)

        if is_valid:
            self.title = result
            self.canvas.save_canvas_state()
            self.cancel_title_editing()
        else:
            QMessageBox.warning(self, "Invalid Name", result)
            self.title_editor.setFocus()
            self.title_editor.selectAll()

    def cancel_title_editing(self):
        if not self.is_editing:
            return

        self.is_editing = False

        if self.title_editor:
            self.title_editor.hide()
            self.title_editor.deleteLater()
            self.title_editor = None

        self.update()

    def get_title_rect(self):
        rect = self.rect().adjusted(1, 1, -1, -1)
        text_height = QFontMetrics(QFont("Arial", 15, QFont.Weight.Bold)).height()
        text_rect = QRectF(rect)
        text_rect.setTop(rect.top() + (rect.height() - text_height) / 2)
        text_rect.setHeight(text_height)
        return text_rect.toRect()

    def get_execution_status_colors(self):
        if self.execution_status == ExecutionStatus.RUNNING:
            return {
                "border": QColor(0, 123, 255),
                "background": QColor(0, 50, 100),
                "pulse": True,
            }
        elif self.execution_status == ExecutionStatus.COMPLETED:
            return {
                "border": QColor(40, 167, 69),
                "background": QColor(34, 34, 34),
                "pulse": False,
            }
        elif self.execution_status == ExecutionStatus.FAILED:
            return {
                "border": QColor(220, 53, 69),
                "background": QColor(80, 20, 20),
                "pulse": False,
            }
        else:
            return {
                "border": QColor(136, 136, 136),
                "background": QColor(34, 34, 34),
                "pulse": False,
            }

    def get_execution_tooltip(self):
        if self.execution_status == ExecutionStatus.IDLE:
            return f"{self.title}\nStatus: Idle"
        elif self.execution_status == ExecutionStatus.RUNNING:
            duration = "Running..."
            if self.execution_start_time:
                elapsed = time.time() - self.execution_start_time
                duration = f"Running... ({elapsed:.1f}s)"
            return f"{self.title}\nStatus: {duration}"
        elif self.execution_status == ExecutionStatus.COMPLETED:
            duration_text = ""
            if self.execution_duration:
                duration_text = f" in {self.execution_duration:.2f}s"
            return f"{self.title}\nStatus: Completed{duration_text}"
        elif self.execution_status == ExecutionStatus.FAILED:
            error_text = ""
            if self.execution_error:
                error_text = f"\nError: {self.execution_error[:50]}..."
            return f"{self.title}\nStatus: Failed{error_text}"
        return f"{self.title}\nStatus: {self.execution_status.value}"

    def set_execution_status(self, status, error=None):
        self.execution_status = status
        if status == ExecutionStatus.RUNNING:
            self.execution_start_time = time.time()
            self.execution_duration = None
            self.execution_error = None
            self.animation_counter = 0
            if self.animation_timer is None:
                self.animation_timer = QTimer(self)
                self.animation_timer.timeout.connect(self._on_animation_tick)
                self.animation_timer.start(50)
        elif status == ExecutionStatus.COMPLETED:
            if self.execution_start_time:
                self.execution_duration = time.time() - self.execution_start_time
            self.execution_error = None
            if self.animation_timer:
                self.animation_timer.stop()
                self.animation_timer = None
        elif status == ExecutionStatus.FAILED:
            if self.execution_start_time:
                self.execution_duration = time.time() - self.execution_start_time
            self.execution_error = error
            if self.animation_timer:
                self.animation_timer.stop()
                self.animation_timer = None
        elif status == ExecutionStatus.IDLE:
            self.execution_start_time = None
            self.execution_duration = None
            self.execution_error = None
            if self.animation_timer:
                self.animation_timer.stop()
                self.animation_timer = None

        self.update()
        if hasattr(self, "canvas") and self.canvas and hasattr(self.canvas, "update"):
            self.canvas.update()

    def _on_animation_tick(self):
        self.animation_counter += 1
        self.update()
        if hasattr(self.canvas, "update"):
            self.canvas.update()

    def reset_execution_status(self):
        self.set_execution_status(ExecutionStatus.IDLE)

    def enterEvent(self, event):
        self.setToolTip(self.get_execution_tooltip())
        self.update()

    def leaveEvent(self, event):
        self.hovered_port = None
        self.update()

    def update_position(self):
        scale = self.canvas.scale
        offset = self.canvas.offset
        screen_pos = self.logical_pos * scale + offset
        self.move(screen_pos.toPoint())
        self.resize(self.sizeHint() * scale)

        node_rect = self.geometry()
        input_x = node_rect.left() - self.input_port.width() // 2
        input_y = (
            node_rect.top() + node_rect.height() // 2 - self.input_port.height() // 2
        )
        self.input_port.move(input_x, input_y)

        output_x = node_rect.right() - self.output_port.width() // 2
        output_y = (
            node_rect.top() + node_rect.height() // 2 - self.output_port.height() // 2
        )
        self.output_port.move(output_x, output_y)

        port_scale = scale
        self.input_port.resize(self.input_port.sizeHint() * port_scale)
        self.output_port.resize(self.output_port.sizeHint() * port_scale)

        margin = 10
        bx = self.width() - self.delete_button.width() - margin
        by = self.height() - self.delete_button.height() - margin
        self.delete_button.move(bx, by)
        self.open_button.move(bx - self.open_button.width() - margin, by)

    def on_open_clicked(self):
        self.canvas.open_node(self)

    def on_delete_clicked(self):
        parent = self.canvas if self.canvas is not None else self
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Delete node")
        msg.setText(f"Delete node '{self.title}'?")
        msg.setInformativeText(
            "This will remove the node and all its connections. This action cannot be undone."
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg.exec()

        if result == QMessageBox.StandardButton.Yes:
            try:
                self.canvas.delete_node(self)
            except Exception as e:
                err = QMessageBox(parent)
                err.setIcon(QMessageBox.Icon.Critical)
                err.setWindowTitle("Delete failed")
                err.setText("Failed to delete the node.")
                err.setInformativeText(str(e))
                err.exec()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        status_colors = self.get_execution_status_colors()

        if self.selected:
            border_color = QColor(255, 215, 0)
        else:
            border_color = status_colors["border"]

        painter.setBrush(status_colors["background"])
        painter.setPen(QPen(border_color, 2))
        painter.drawRoundedRect(rect, 10, 10)

        if status_colors["pulse"] and self.execution_status == ExecutionStatus.RUNNING:
            pulse_intensity = int(
                80 * (0.5 + 0.5 * math.sin(self.animation_counter * 0.3))
            )
            pulse_color = QColor(0, 123 + pulse_intensity, 255)
            painter.setPen(QPen(pulse_color, 3))
            painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), 10, 10)

        painter.setPen(QColor("white"))
        font = QFont("Arial", 15)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        text_rect = QRectF(rect)
        text_height = QFontMetrics(font).height()
        text_rect.setTop(rect.top() + (rect.height() - text_height) / 2)

        if not self.is_editing:
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                self.title,
            )

        if self.selected:
            self.delete_button.show()
            self.open_button.show()
        else:
            self.delete_button.hide()
            self.open_button.hide()

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.selected:
            new_pos = self.mapToParent(event.pos() - self.drag_offset)
            canvas_offset = self.canvas.offset
            scale = self.canvas.scale
            logical_pos = (QPointF(new_pos) - canvas_offset) / scale

            self.logical_pos = logical_pos
            self.canvas.update_node_position(self.id, self.logical_pos)
            self.update_position()

    def eventFilter(self, obj, event):
        if (
            obj == self.title_editor
            and event.type() == event.Type.KeyPress
            and event.key() == Qt.Key.Key_Escape
        ):
            self.cancel_title_editing()
            return True
        return super().eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            local_pos = event.position().toPoint()
            child = self.childAt(local_pos)

            if child not in (self.delete_button, self.open_button):
                self.start_title_editing()
                return

        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        rename_action = menu.addAction("Rename Node")
        rename_action.triggered.connect(self.start_title_editing)
        menu.exec(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            local = event.position().toPoint()
            child = self.childAt(local)
            if child is self.delete_button or child is self.open_button:
                return

            self.canvas.select_node(self)
            self.is_dragging = True
            self.drag_offset = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.canvas.save_canvas_state()


__all__ = ["ExecutionStatus", "NodeWidget"]
