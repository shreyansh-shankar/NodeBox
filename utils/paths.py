import os
import platform
import sys
from functools import lru_cache
from pathlib import Path
from typing import Union

# App directory name
APP_DIR_NAME = ".nodebox"

# Get the current platform
SYSTEM = platform.system()

# Platform-specific app directory resolution
if SYSTEM == "Windows":
    # On Windows, use %APPDATA% or fallback to home
    base_dir = Path(os.getenv("APPDATA", Path.home()))
    APP_DATA_DIR = base_dir / APP_DIR_NAME
else:
    # On Linux/macOS, use ~/.nodebox
    APP_DATA_DIR = Path.home() / APP_DIR_NAME

# Subdirectories
AUTOMATIONS_DIR = APP_DATA_DIR / "automations"
CONFIG_DIR = APP_DATA_DIR / "config"
CACHE_DIR = APP_DATA_DIR / "cache"
LOGS_DIR = APP_DATA_DIR / "logs"

# Create folders if they don't exist
for path in [APP_DATA_DIR, AUTOMATIONS_DIR, CONFIG_DIR, CACHE_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def _bundle_base_path() -> Path:
    """Return the base directory for resource loading in dev and frozen builds."""
    if getattr(sys, "frozen", False):
        # PyInstaller >= 6.x puts resources in _internal folder
        # sys.executable points to NodeBox.exe, _internal is alongside it
        exe_dir = Path(sys.executable).parent
        internal_dir = exe_dir / "_internal"
        if internal_dir.exists():
            return internal_dir
        # Fallback for older PyInstaller versions
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return exe_dir
    # In development, resolve to the repository root (one level above utils/)
    return Path(__file__).resolve().parent.parent


def resource_path(relative_path: Union[str, Path]) -> str:
    """Return an absolute path to a bundled resource.

    Works transparently in development and PyInstaller distributions. Accepts either
    string or ``Path`` inputs and normalises the result so it can be passed directly to
    Qt APIs that expect filesystem paths.
    """

    relative = Path(relative_path)
    full_path = (_bundle_base_path() / relative).resolve()
    return str(full_path)


# Common files
AUTOMATIONS_FILE = AUTOMATIONS_DIR / "automations.json"
CONFIG_FILE = CONFIG_DIR / "settings.json"
