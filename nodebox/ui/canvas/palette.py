from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QLabel


class NodePaletteItem(QLabel):
    """Drag-and-drop node item for the node palette sidebar."""

    def __init__(self, node_type, parent=None):
        super().__init__(node_type, parent)
        self.node_type = node_type
        self.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                background-color: #444;
                border-radius: 5px;
            }
            QLabel:hover {
                background-color: #666;
            }
        """
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.node_type)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)


__all__ = ["NodePaletteItem"]
