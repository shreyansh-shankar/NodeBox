"""
Screen Resolution Utility Module for NodeBox.
"""

from typing import Optional, Tuple
from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication


class ScreenManager:
    """Manages screen resolution and dynamic sizing calculations."""

    @staticmethod
    def get_screen_geometry() -> QRect:
        screen = QApplication.primaryScreen()
        if screen:
            return screen.geometry()
        return QRect(0, 0, 1920, 1080)

    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        geometry = ScreenManager.get_screen_geometry()
        return geometry.width(), geometry.height()

    @staticmethod
    def get_available_geometry() -> QRect:
        screen = QApplication.primaryScreen()
        if screen:
            return screen.availableGeometry()
        return QRect(0, 0, 1920, 1040)

    @staticmethod
    def calculate_window_size(
        width_percentage: float = 0.75,
        height_percentage: float = 0.75,
        min_width: int = 800,
        min_height: int = 600,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> Tuple[int, int]:
        available_geometry = ScreenManager.get_available_geometry()
        screen_width = available_geometry.width()
        screen_height = available_geometry.height()

        calculated_width = int(screen_width * width_percentage)
        calculated_height = int(screen_height * height_percentage)

        width = max(calculated_width, min_width)
        height = max(calculated_height, min_height)

        if max_width:
            width = min(width, max_width)
        if max_height:
            height = min(height, max_height)

        return width, height

    @staticmethod
    def calculate_window_position(
        window_width: int,
        window_height: int,
        center: bool = True,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> Tuple[int, int]:
        available_geometry = ScreenManager.get_available_geometry()

        if center:
            x = (available_geometry.width() - window_width) // 2 + available_geometry.x()
            y = (available_geometry.height() - window_height) // 2 + available_geometry.y()
        else:
            x = available_geometry.x()
            y = available_geometry.y()

        x += offset_x
        y += offset_y

        return x, y

    @staticmethod
    def get_main_window_geometry() -> Tuple[int, int, int, int]:
        width, height = ScreenManager.calculate_window_size(
            width_percentage=0.75, height_percentage=0.75, min_width=900, min_height=600
        )
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        return x, y, width, height

    @staticmethod
    def get_browse_window_geometry() -> Tuple[int, int, int, int]:
        width, height = ScreenManager.calculate_window_size(
            width_percentage=0.8, height_percentage=0.8, min_width=1000, min_height=700
        )
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        return x, y, width, height

    @staticmethod
    def get_editor_window_geometry() -> Tuple[int, int, int, int]:
        width, height = ScreenManager.calculate_window_size(
            width_percentage=0.85,
            height_percentage=0.85,
            min_width=1200,
            min_height=800,
        )
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        return x, y, width, height

    @staticmethod
    def get_dialog_window_size(
        width_percentage: float = 0.3,
        height_percentage: float = 0.25,
        min_width: int = 400,
        min_height: int = 200,
    ) -> Tuple[int, int]:
        return ScreenManager.calculate_window_size(
            width_percentage=width_percentage,
            height_percentage=height_percentage,
            min_width=min_width,
            min_height=min_height,
        )


__all__ = ["ScreenManager"]
