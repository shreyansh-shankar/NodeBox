import os
import platform
from pathlib import Path

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

# Common files
AUTOMATIONS_FILE = AUTOMATIONS_DIR / "automations.json"
CONFIG_FILE = CONFIG_DIR / "settings.json"

print(f"✅ NodeBox data directories ensured at: {APP_DATA_DIR}")
