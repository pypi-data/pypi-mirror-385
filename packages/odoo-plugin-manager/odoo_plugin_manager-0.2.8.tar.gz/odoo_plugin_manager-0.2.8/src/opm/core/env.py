from __future__ import annotations
import os
import yaml
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
load_dotenv()

def _expand_env_vars(value):
    """Recursively expand ${VAR} from environment variables in strings of nested dict/list structures.
    If a variable is missing, leave the placeholder as-is.
    """
    if isinstance(value, str):
        # Simple ${VAR} expansion
        import re
        def repl(m):
            var = m.group(1)
            return os.getenv(var, m.group(0))
        return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, value)
    elif isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    return value


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep-merge two dictionaries without mutating inputs. override wins."""
    out = dict(base or {})
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

DEFAULT_CONFIG = {
    "profile": "docker",
    "docker": {
        "odoo_image": "odoo:17.0",
        "postgres_image": "postgres:15",
        "network": None,
        "mounts": [],
        "junit_path": ".opm/artifacts/junit.xml",
        "parallel": 1,
    },
    "runtime": {
        "odoo_url": "http://localhost:8069",
        "db": "odoo",
        "user": "admin",
        "pass": "admin",
        "addons": ["./addons"],
        "vite_proxy": None,
    }
}

class Config:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @property
    def profile(self) -> str:
        return self.data.get("profile", "docker")

    def get(self, *path, default=None):
        cur = self.data
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return default
        return cur

    def resolve_env(self, name: str):
        """Return a lightweight environment object for the given name.
        Supports optional `extends:` (e.g., extends: runtime or another env) and env var expansion.
        """
        envs = self.data.get("environments", {}) or {}
        if name not in envs:
            raise ValueError(f"Environment '{name}' not defined in opm.yaml")
        entry = envs[name] or {}
        base_name = entry.get("extends")

        if base_name:
            # base can be `runtime` or another env under `environments`
            if base_name == "runtime":
                base = self.data.get("runtime", {})
            else:
                base_env = envs.get(base_name)
                if not base_env:
                    raise ValueError(f"Environment '{name}' extends unknown base '{base_name}'")
                base = base_env
            merged = _deep_merge(base, entry)
        else:
            # If no extends, still provide fallback to runtime for missing auth fields
            fallback = self.data.get("runtime", {})
            merged = _deep_merge(fallback, entry)

        kind = merged.get("kind", "runtime")
        merged = _expand_env_vars(merged)
        return type("Env", (), {"kind": kind, "data": merged})()

def load_config(path: str|None = None) -> Config:
    candidates = [path] if path else ["opm.yaml", "opm.yml"]
    data = DEFAULT_CONFIG.copy()
    for c in candidates:
        p = Path(c)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
            # shallow merge
            def merge(a, b):
                for k, v in b.items():
                    if isinstance(v, dict) and isinstance(a.get(k), dict):
                        merge(a[k], v)
                    else:
                        a[k] = v
            merge(data, loaded)
            break
    data = _expand_env_vars(data)
    return Config(data)