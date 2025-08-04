import json
from pathlib import Path
from utils.paths import AUTOMATIONS_FILE

def load_automations():
    if AUTOMATIONS_FILE.exists():
        with open(AUTOMATIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_automation(new_automation: dict, filename: str):
    with open(filename, 'w') as f:
        json.dump(new_automation, f, indent=4)
