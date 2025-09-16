"""
Screen Resolution Utility Module

This module provides functions to dynamically calculate window sizes
based on the user's screen resolution, enabling responsive UI across
different monitor sizes and devices.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect
from typing import Tuple, Optional


class ScreenManager:
    """Manages screen resolution and provides dynamic sizing calculations."""
    
    @staticmethod
    def get_screen_geometry() -> QRect:
        """
        Get the geometry of the primary screen.
        
        Returns:
            QRect: The geometry (x, y, width, height) of the primary screen
        """
        screen = QApplication.primaryScreen()
        if screen:
            return screen.geometry()
        # Fallback values if screen detection fails
        return QRect(0, 0, 1920, 1080)
    
    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """
        Get the width and height of the primary screen.
        
        Returns:
            Tuple[int, int]: (width, height) of the primary screen
        """
        geometry = ScreenManager.get_screen_geometry()
        return geometry.width(), geometry.height()
    
    @staticmethod
    def get_available_geometry() -> QRect:
        """
        Get the available geometry (excluding taskbars, docks, etc.).
        
        Returns:
            QRect: The available geometry of the primary screen
        """
        screen = QApplication.primaryScreen()
        if screen:
            return screen.availableGeometry()
        # Fallback values if screen detection fails
        return QRect(0, 0, 1920, 1040)  # Slightly smaller to account for taskbar
    
    @staticmethod
    def calculate_window_size(
        width_percentage: float = 0.75, 
        height_percentage: float = 0.75,
        min_width: int = 800,
        min_height: int = 600,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Calculate dynamic window size based on screen resolution.
        
        Args:
            width_percentage: Percentage of screen width (0.0-1.0)
            height_percentage: Percentage of screen height (0.0-1.0)
            min_width: Minimum window width in pixels
            min_height: Minimum window height in pixels
            max_width: Maximum window width in pixels (None for no limit)
            max_height: Maximum window height in pixels (None for no limit)
            
        Returns:
            Tuple[int, int]: (width, height) for the window
        """
        available_geometry = ScreenManager.get_available_geometry()
        screen_width = available_geometry.width()
        screen_height = available_geometry.height()
        
        # Calculate desired size based on percentages
        calculated_width = int(screen_width * width_percentage)
        calculated_height = int(screen_height * height_percentage)
        
        # Apply minimum constraints
        width = max(calculated_width, min_width)
        height = max(calculated_height, min_height)
        
        # Apply maximum constraints if specified
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
        offset_y: int = 0
    ) -> Tuple[int, int]:
        """
        Calculate window position on screen.
        
        Args:
            window_width: Width of the window
            window_height: Height of the window
            center: Whether to center the window on screen
            offset_x: Horizontal offset from calculated position
            offset_y: Vertical offset from calculated position
            
        Returns:
            Tuple[int, int]: (x, y) position for the window
        """
        available_geometry = ScreenManager.get_available_geometry()
        
        if center:
            x = (available_geometry.width() - window_width) // 2 + available_geometry.x()
            y = (available_geometry.height() - window_height) // 2 + available_geometry.y()
        else:
            x = available_geometry.x()
            y = available_geometry.y()
        
        # Apply offsets
        x += offset_x
        y += offset_y
        
        return x, y
    
    @staticmethod
    def get_main_window_geometry() -> Tuple[int, int, int, int]:
        """
        Get geometry for the main application window.
        Uses 75% of screen size with appropriate minimums.
        
        Returns:
            Tuple[int, int, int, int]: (x, y, width, height)
        """
        width, height = ScreenManager.calculate_window_size(
            width_percentage=0.75,
            height_percentage=0.75,
            min_width=900,
            min_height=600
        )
        
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        
        return x, y, width, height
    
    @staticmethod
    def get_browse_window_geometry() -> Tuple[int, int, int, int]:
        """
        Get geometry for the browse models window.
        Uses 80% of screen size with appropriate minimums for browsing.
        
        Returns:
            Tuple[int, int, int, int]: (x, y, width, height)
        """
        width, height = ScreenManager.calculate_window_size(
            width_percentage=0.8,
            height_percentage=0.8,
            min_width=1000,
            min_height=700
        )
        
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        
        return x, y, width, height
    
    @staticmethod
    def get_editor_window_geometry() -> Tuple[int, int, int, int]:
        """
        Get geometry for the node editor window.
        Uses 85% of screen size with larger minimums for the canvas.
        
        Returns:
            Tuple[int, int, int, int]: (x, y, width, height)
        """
        width, height = ScreenManager.calculate_window_size(
            width_percentage=0.85,
            height_percentage=0.85,
            min_width=1200,
            min_height=800
        )
        
        x, y = ScreenManager.calculate_window_position(width, height, center=True)
        
        return x, y, width, height
    
    @staticmethod
    def get_dialog_window_size(
        width_percentage: float = 0.3,
        height_percentage: float = 0.25,
        min_width: int = 400,
        min_height: int = 200
    ) -> Tuple[int, int]:
        """
        Get size for dialog windows (relative to screen size).
        
        Args:
            width_percentage: Percentage of screen width
            height_percentage: Percentage of screen height
            min_width: Minimum dialog width
            min_height: Minimum dialog height
            
        Returns:
            Tuple[int, int]: (width, height)
        """
        return ScreenManager.calculate_window_size(
            width_percentage=width_percentage,
            height_percentage=height_percentage,
            min_width=min_width,
            min_height=min_height
        )