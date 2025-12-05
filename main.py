import subprocess
import sys
from typing import Optional

from PyQt6.QtGui import QFontDatabase, QIcon  # type: ignore
from PyQt6.QtWidgets import QApplication, QMessageBox  # type: ignore

from ui.enhanced_main_window import EnhancedMainWindow
from utils.font_loader import load_custom_fonts, set_default_font
from utils.logger import get_logger
from utils.paths import resource_path

# Initialize logger
logger = get_logger("nodebox.main")


def start_ollama() -> Optional[subprocess.Popen]:
    """
    Start Ollama serve in the background.

    Returns:
        Subprocess instance if successful, None otherwise.
    """
    try:
        logger.info("Starting Ollama server...")
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("Ollama server started successfully")
        return process
    except FileNotFoundError:
        logger.warning("Ollama is not installed or not in PATH. AI features will be unavailable.")
        return None
    except Exception as e:
        logger.error(f"Failed to start Ollama: {e}")
        return None


def load_application_fonts() -> bool:
    """
    Load custom application fonts.

    Returns:
        True if fonts loaded successfully, False otherwise.
    """
    font_files = [
        "assets/fonts/Poppins-Regular.ttf",
        "assets/fonts/Poppins-Medium.ttf",
        "assets/fonts/Poppins-SemiBold.ttf",
    ]

    success = True
    for font_file in font_files:
        try:
            font_path = resource_path(font_file)
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                logger.warning(f"Failed to load font: {font_file}")
                success = False
            else:
                logger.debug(f"Loaded font: {font_file}")
        except Exception as e:
            logger.error(f"Error loading font {font_file}: {e}")
            success = False

    return success


def load_stylesheet(app: QApplication) -> bool:
    """
    Load and apply application stylesheet.

    Args:
        app: QApplication instance

    Returns:
        True if stylesheet loaded successfully, False otherwise.
    """
    try:
        qss_file = resource_path("qss/dark.qss")
        with open(qss_file, "r", encoding="utf-8") as file:
            stylesheet = file.read()
            app.setStyleSheet(stylesheet)
            logger.info("Stylesheet loaded successfully")
            return True
    except FileNotFoundError:
        logger.warning("Stylesheet file not found, using default styling")
        # Apply basic dark theme as fallback
        app.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                color: #e0e0e0;
            }
        """)
        return False
    except Exception as e:
        logger.error(f"Error loading stylesheet: {e}")
        return False


def cleanup_ollama_process(process: Optional[subprocess.Popen]) -> None:
    """
    Safely cleanup Ollama process.

    Args:
        process: Subprocess instance to cleanup
    """
    if not process:
        return

    try:
        logger.info("Shutting down Ollama server...")
        process.terminate()
        try:
            process.wait(timeout=5)
            logger.info("Ollama server stopped successfully")
        except subprocess.TimeoutExpired:
            logger.warning("Ollama server did not respond to terminate, forcing kill...")
            process.kill()
            process.wait(timeout=2)
            logger.info("Ollama server killed")
    except Exception as e:
        logger.error(f"Error during Ollama cleanup: {e}")


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("NodeBox Application Starting")
    logger.info("=" * 60)

    # Start Ollama first
    ollama_process = start_ollama()

    try:
        app = QApplication(sys.argv)

        # Set application icon
        try:
            icon_path = resource_path("assets/icons/favicon.png")
            app.setWindowIcon(QIcon(icon_path))
            logger.debug("Application icon set")
        except Exception as e:
            logger.warning(f"Could not set application icon: {e}")

        # Load custom fonts
        if not load_application_fonts():
            logger.warning("Some fonts failed to load, continuing with available fonts")

        # Apply stylesheet
        load_stylesheet(app)

        # Load fonts and set default size
        try:
            load_custom_fonts()
            set_default_font(10)
        except Exception as e:
            logger.error(f"Error in font configuration: {e}")

        # Create and show main window
        try:
            window = EnhancedMainWindow()
            window.show()
            logger.info("Main window displayed successfully")
        except Exception as e:
            logger.critical(f"Failed to create main window: {e}", exc_info=True)
            QMessageBox.critical(
                None,
                "Startup Error",
                f"Failed to start NodeBox:\n{str(e)}\n\nCheck the log file for details.",
            )
            cleanup_ollama_process(ollama_process)
            sys.exit(1)

        # Run application
        logger.info("Application initialized, entering main loop")
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")

    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        exit_code = 1
    finally:
        # Cleanup after Qt loop finishes
        cleanup_ollama_process(ollama_process)
        logger.info("NodeBox Application Shutdown Complete")
        logger.info("=" * 60)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
