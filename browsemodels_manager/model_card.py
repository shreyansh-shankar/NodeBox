import os
import sys

from PyQt6.QtCore import QSize, Qt, QUrl, pyqtSignal  # type: ignore
from PyQt6.QtGui import QCursor, QDesktopServices, QFont, QIcon, QPixmap  # type: ignore
from PyQt6.QtWidgets import (  # type: ignore
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


# resource_path helper
def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and in PyInstaller bundle"""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # Go one level up from the script folder to reach project root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


class ModelCard(QFrame):
    downloadRequested = pyqtSignal(dict)

    def __init__(self, model_data, parent=None):
        super().__init__(parent)
        self.model = model_data

        self.setObjectName("ModelCard")
        self.setFixedSize(480, 240)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMouseTracking(True)

        self.setStyleSheet(
            """
            QFrame {
                border: 1px solid #3c3c3c;
                border-radius: 18px;
                padding: 12px;
                background-color: #1a1a1a;
            }
            #ModelCard {
                border: 1px solid #3c3c3c;
                border-radius: 18px;
                padding: 12px;
                background-color: #1a1a1a;
            }
            #ModelCard:hover {
                background-color: #232323;
            }
        """
        )

        self.init_ui(model_data)

    def init_ui(self, model_data):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Top: Icon + Name & Description
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(72, 72)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center image in the box

        icon_path = resource_path(model_data["icon"])
        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(
            48,
            48,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        icon_label.setPixmap(pixmap)

        # Name and Description
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        name = QLabel(model_data["name"])
        name.setStyleSheet(
            "color: #ffffff; font-size: 18px; font-weight: 600; border: none;"
        )
        name.setFont(QFont("Poppins", 10))

        description = QLabel(model_data.get("description", ""))
        description.setStyleSheet("color: #aaaaaa; font-size: 12px; border: none;")
        description.setWordWrap(True)
        description.setMaximumHeight(96)

        info_layout.addWidget(name)
        info_layout.addWidget(description)

        # Download Button (Top-Right)
        self.download_button = QPushButton()
        svg_path = resource_path("assets/icons/download.svg")
        self.download_button.setIcon(QIcon(svg_path))
        self.download_button.setIconSize(QSize(32, 32))
        self.download_button.setFixedSize(42, 42)
        self.download_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid white;
                border-radius: 16px;
                border: 0px;
                background-color: #262626;
            }
            QPushButton:hover {
                background-color: #058401;
            }
            QPushButton:pressed {
                background-color: #059e00;
            }
        """
        )

        # Place button on far right
        right_layout = QVBoxLayout()
        right_layout.addWidget(
            self.download_button,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        right_layout.addStretch()

        top_layout.addWidget(icon_label)
        top_layout.addLayout(info_layout)
        top_layout.addLayout(right_layout)

        # Bottom: Tags + Sizes
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(6)

        # Tags
        tags_layout = QHBoxLayout()
        for tag in model_data.get("tags", []):
            tag_label = QLabel(tag)
            tag_label.setStyleSheet(
                """
                background-color: #274049;
                color: #eeeeee;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
            """
            )
            tags_layout.addWidget(tag_label)
        tags_layout.addStretch()

        # Sizes
        sizes_layout = QHBoxLayout()
        for size in model_data.get("sizes", []):
            size_label = QLabel(size)
            size_label.setStyleSheet(
                """
                background-color: #2e4927;
                color: #eeeeee;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
            """
            )
            sizes_layout.addWidget(size_label)
        sizes_layout.addStretch()

        bottom_layout.addLayout(tags_layout)
        bottom_layout.addLayout(sizes_layout)

        # Add to main layout
        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        # Connect download button
        self.download_button.clicked.connect(
            lambda: self.downloadRequested.emit(self.model)
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            model_name = self.model["name"].lower().replace(" ", "-")
            url = QUrl(f"https://ollama.com/library/{model_name}")
            QDesktopServices.openUrl(url)
