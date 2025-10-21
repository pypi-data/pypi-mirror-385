from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Dict, Any

STATE_DIR = Path(".opm")
STATE_FILE = STATE_DIR / "config.json"

DEFAULT_STATE = {
    "default_env": None,
    "default_addons": None,
}

def load_state() -> Dict[str, Any]:
    try:
        if STATE_FILE.exists():
            return {**DEFAULT_STATE, **json.loads(STATE_FILE.read_text(encoding="utf-8"))}
    except Exception:
        pass
    return DEFAULT_STATE.copy()

def save_state(updates: Dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state.update({k: v for k, v in updates.items() if v is not None})
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def get_default_env() -> Optional[str]:
    return load_state().get("default_env")

def set_default_env(name: Optional[str]) -> None:
    save_state({"default_env": name})

def get_default_addons() -> Optional[str]:
    return load_state().get("default_addons")

def set_default_addons(path: Optional[str]) -> None:
    save_state({"default_addons": path})