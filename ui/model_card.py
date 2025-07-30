# model_card.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame #type: ignore
from PyQt6.QtGui import QPixmap, QFont #type: ignore
from PyQt6.QtCore import Qt #type: ignore

class ModelCard(QFrame):
    def __init__(self, model_data, parent=None):
        super().__init__(parent)
        self.model = model_data
        self.setFixedSize(480, 240)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #3c3c3c;
                border-radius: 18px;
                padding: 12px;
                background-color: #1a1a1a;
            }
        """)
        
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

        pixmap = QPixmap(model_data['icon'])
        pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(pixmap)

        # Name and Description
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        name = QLabel(model_data["name"])
        name.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 600; border: none;")
        name.setFont(QFont("Poppins", 10))

        description = QLabel(model_data.get("description", ""))
        description.setStyleSheet("color: #aaaaaa; font-size: 12px; border: none;")
        description.setWordWrap(True)
        description.setMaximumHeight(48)

        info_layout.addWidget(name)
        info_layout.addWidget(description)

        top_layout.addWidget(icon_label)
        top_layout.addLayout(info_layout)

        # Bottom: Tags + Sizes
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(6)

        # Tags
        tags_layout = QHBoxLayout()
        for tag in model_data.get("tags", []):
            tag_label = QLabel(tag)
            tag_label.setStyleSheet("""
                background-color: #274049;
                color: #c0c0c0;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
            """)
            tags_layout.addWidget(tag_label)
        tags_layout.addStretch()

        # Sizes
        sizes_layout = QHBoxLayout()
        for size in model_data.get("sizes", []):
            size_label = QLabel(size)
            size_label.setStyleSheet("""
                background-color: #2e4927;
                color: #aaa;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
            """)
            sizes_layout.addWidget(size_label)
        sizes_layout.addStretch()

        bottom_layout.addLayout(tags_layout)
        bottom_layout.addLayout(sizes_layout)

        # Add to main layout
        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)