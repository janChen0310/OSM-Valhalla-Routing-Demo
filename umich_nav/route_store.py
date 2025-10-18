import json
from typing import Any, Dict


def save_route(route: Dict[str, Any], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)


def load_route(filename: str) -> Dict[str, Any]:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
