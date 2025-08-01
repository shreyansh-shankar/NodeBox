import json
from pathlib import Path
from utils.paths import AUTOMATIONS_FILE

def load_automations():
    if AUTOMATIONS_FILE.exists():
        with open(AUTOMATIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_automation(new_automation: dict):
    automations = load_automations()
    automations.append(new_automation)
    with open(AUTOMATIONS_FILE, 'w') as f:
        json.dump(automations, f, indent=4)
