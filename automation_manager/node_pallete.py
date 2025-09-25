from PyQt6.QtCore import QMimeData, Qt  # type: ignore
from PyQt6.QtGui import QDrag  # type: ignore
from PyQt6.QtWidgets import QLabel  # type: ignore


class NodePaletteItem(QLabel):
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
            mime_data.setText(self.node_type)  # Pass node type
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)
