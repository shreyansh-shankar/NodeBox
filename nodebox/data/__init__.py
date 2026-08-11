import json
from pathlib import Path

from nodebox.core.paths import resource_path


def load_model_catalog():
    """Load model catalog from JSON file."""
    json_path = resource_path("data/models.json")
    if Path(json_path).exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


__all__ = ["load_model_catalog"]
