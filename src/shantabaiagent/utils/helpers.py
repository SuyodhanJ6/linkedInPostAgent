import json
from typing import Any

def save_to_json(data: Any, filename: str) -> None:
    """Save data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_from_json(filename: str) -> Any:
    """Load data from a JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    return text.strip().replace('\n', ' ').replace('\r', '')
