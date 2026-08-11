import math
import time
import uuid
from enum import Enum

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QMenu, QMessageBox, QPushButton, QWidget

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
        self.setFixedSize(210, 115)

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

        self.delete_button = QPushButton("X", self)
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(239,68,68,0.85);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #EF4444;
            }
        """
        )
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.hide()

        self.open_button = QPushButton("Edit", self)
        self.open_button.setFixedSize(40, 20)
        self.open_button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(99,102,241,0.85);
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #6366F1;
            }
        """
        )
        self.open_button.clicked.connect(self.on_open_clicked)
        self.open_button.hide()

    def get_category_info(self):
        title_lower = self.title.lower()
        if any(k in title_lower for k in ["file", "csv", "read", "write", "folder"]):
            return {
                "grad_start": QColor("#047857"),
                "grad_end": QColor("#10B981"),
                "category": "File Ops",
                "accent": QColor("#10B981"),
            }
        elif any(k in title_lower for k in ["llm", "ai", "ollama", "gpt", "model", "prompt"]):
            return {
                "grad_start": QColor("#3730A3"),
                "grad_end": QColor("#6366F1"),
                "category": "AI Model",
                "accent": QColor("#6366F1"),
            }
        elif any(k in title_lower for k in ["data", "json", "parse", "filter", "db"]):
            return {
                "grad_start": QColor("#B45309"),
                "grad_end": QColor("#F59E0B"),
                "category": "Data",
                "accent": QColor("#F59E0B"),
            }
        elif any(k in title_lower for k in ["code", "script", "python", "custom"]):
            return {
                "grad_start": QColor("#5B21B6"),
                "grad_end": QColor("#8B5CF6"),
                "category": "Script",
                "accent": QColor("#8B5CF6"),
            }
        else:
            return {
                "grad_start": QColor("#0369A1"),
                "grad_end": QColor("#38BDF8"),
                "category": "Node",
                "accent": QColor("#38BDF8"),
            }

    def get_summary_text(self):
        if hasattr(self, "outputs") and self.outputs:
            if isinstance(self.outputs, dict):
                outs = list(self.outputs.keys())
            elif isinstance(self.outputs, list):
                outs = self.outputs
            else:
                outs = []
            if outs:
                return f"out: {', '.join(outs[:2])}"

        if hasattr(self, "code") and self.code:
            lines = [
                l.strip()
                for l in self.code.splitlines()
                if l.strip() and not l.strip().startswith("#")
            ]
            if lines:
                return lines[0][:24]
        return "Double click to edit"

    def get_execution_status_colors(self):
        if self.execution_status == ExecutionStatus.RUNNING:
            return {
                "border": QColor("#F59E0B"),
                "background": QColor("#13151E"),
                "pulse": True,
                "status_text": "Running",
                "status_color": QColor("#FBB040"),
            }
        elif self.execution_status == ExecutionStatus.COMPLETED:
            return {
                "border": QColor("#10B981"),
                "background": QColor("#13151E"),
                "pulse": False,
                "status_text": "Done",
                "status_color": QColor("#34D399"),
            }
        elif self.execution_status == ExecutionStatus.FAILED:
            return {
                "border": QColor("#EF4444"),
                "background": QColor("#13151E"),
                "pulse": False,
                "status_text": "Error",
                "status_color": QColor("#F87171"),
            }
        else:
            return {
                "border": QColor("#1E2538"),
                "background": QColor("#13151E"),
                "pulse": False,
                "status_text": "Idle",
                "status_color": QColor("#4A5578"),
            }

    def get_execution_tooltip(self):
        if self.execution_status == ExecutionStatus.IDLE:
            return f"{self.title}\nStatus: Idle\nDouble-click to configure node code"
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
        elif status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            if self.execution_start_time:
                self.execution_duration = time.time() - self.execution_start_time
            self.execution_error = error if status == ExecutionStatus.FAILED else None
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

        margin = 6
        bx = self.width() - self.delete_button.width() - margin
        by = margin + 4
        self.delete_button.move(bx, by)
        self.open_button.move(bx - self.open_button.width() - 4, by)

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

        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        cat_info = self.get_category_info()
        status_colors = self.get_execution_status_colors()

        if self.selected:
            border_color = QColor("#6366F1")
            border_width = 2.0
        else:
            border_color = status_colors["border"]
            border_width = 1.0

        # ── Background Card ──────────────────────────────────────────
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)

        bg_grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        bg_grad.setColorAt(0.0, QColor("#1A1E2E"))
        bg_grad.setColorAt(1.0, QColor("#11141D"))

        painter.fillPath(path, bg_grad)
        painter.setPen(QPen(border_color, border_width))
        painter.drawPath(path)

        # ── Category Header Strip (top 32px) ─────────────────────────
        header_height = 32
        header_rect = QRectF(rect.x(), rect.y(), rect.width(), header_height)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 12, 12)

        header_grad = QLinearGradient(header_rect.topLeft(), header_rect.topRight())
        header_grad.setColorAt(0.0, cat_info["grad_start"])
        header_grad.setColorAt(1.0, cat_info["grad_end"])

        painter.save()
        painter.setClipPath(path)
        painter.fillPath(header_path, header_grad)
        painter.restore()

        # ── Header Title ─────────────────────────────────────────────
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Poppins", 10, QFont.Weight.DemiBold)
        painter.setFont(font)
        title_rect = QRectF(rect.x() + 12, rect.y(), rect.width() - 52, header_height)
        title_text = self.title
        fm = painter.fontMetrics()
        if fm.horizontalAdvance(title_text) > title_rect.width():
            title_text = fm.elidedText(title_text, Qt.TextElideMode.ElideRight, int(title_rect.width()))
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            title_text,
        )

        # ── Category Chip (top-right) ─────────────────────────────────
        cat_text = cat_info["category"]
        font_chip = QFont("Poppins", 7, QFont.Weight.Bold)
        painter.setFont(font_chip)
        chip_w = 42
        chip_rect = QRectF(rect.right() - chip_w - 6, rect.y() + 8, chip_w, 16)
        chip_path = QPainterPath()
        chip_path.addRoundedRect(chip_rect, 4, 4)
        painter.fillPath(chip_path, QColor(0, 0, 0, 50))
        painter.setPen(QColor(255, 255, 255, 160))
        painter.drawText(chip_rect, Qt.AlignmentFlag.AlignCenter, cat_text)

        # ── Body ──────────────────────────────────────────────────────
        body_y = header_rect.bottom() + 6

        # Summary text
        font_sub = QFont("Consolas", 8)
        painter.setFont(font_sub)
        painter.setPen(QColor("#8892B0"))
        summary_rect = QRectF(rect.x() + 12, body_y, rect.width() - 24, 22)
        summary_str = self.get_summary_text()
        painter.drawText(
            summary_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            summary_str,
        )

        # ── Status Dot + Text in footer ───────────────────────────────
        status_text = status_colors["status_text"]
        status_color = status_colors["status_color"]
        footer_y = rect.bottom() - 18

        dot_rect = QRectF(rect.x() + 12, footer_y + 4, 6, 6)
        dot_path = QPainterPath()
        dot_path.addEllipse(dot_rect)
        painter.fillPath(dot_path, status_color)

        font_status = QFont("Poppins", 8)
        painter.setFont(font_status)
        painter.setPen(status_color)
        status_rect = QRectF(rect.x() + 22, footer_y, rect.width() - 30, 14)
        painter.drawText(
            status_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            status_text,
        )

        # ── Pulse ring when running ───────────────────────────────────
        if status_colors["pulse"] and self.execution_status == ExecutionStatus.RUNNING:
            pulse_intensity = int(80 * (0.5 + 0.5 * math.sin(self.animation_counter * 0.3)))
            pulse_color = QColor(245, 158, 11, 120 + pulse_intensity)
            painter.setPen(QPen(pulse_color, 2.0))
            painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), 14, 14)

        # ── Show / hide control buttons on hover / selection ──────────
        if self.selected or self.underMouse():
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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            local_pos = event.position().toPoint()
            child = self.childAt(local_pos)
            if child not in (self.delete_button, self.open_button):
                self.on_open_clicked()
                return

        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = menu.addAction("Configure Node Script")
        open_action.triggered.connect(self.on_open_clicked)
        delete_action = menu.addAction("Delete Node")
        delete_action.triggered.connect(self.on_delete_clicked)
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
