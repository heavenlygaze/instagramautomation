from pathlib import Path
import json
from typing import Any, Dict


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_state(state_path: Path) -> Dict[str, Any]:
    return load_json(state_path, default={"user_id_cache": {}, "last_seen": {}})

def save_state(state_path: Path, state: Dict[str, Any]) -> None:
    save_json(state_path, state)
