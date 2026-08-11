from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QDrag, QFont
from PyQt6.QtWidgets import QLabel


class NodePaletteItem(QLabel):
    """Drag-and-drop node item for the node palette sidebar."""

    def __init__(self, node_type, parent=None):
        super().__init__(node_type, parent)
        self.node_type = node_type
        self.setFont(QFont("Poppins", 10, QFont.Weight.Medium))
        self.setStyleSheet(
            """
            QLabel {
                padding: 10px 14px;
                background-color: #222733;
                border: 1px solid #2E3444;
                border-radius: 8px;
                color: #F9FAFB;
            }
            QLabel:hover {
                background-color: #2A303F;
                border-color: #6366F1;
                color: #818CF8;
            }
        """
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.node_type)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)


__all__ = ["NodePaletteItem"]
