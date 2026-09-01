"""Configuration store for image-gen providers.

Design notes:
- Config lives INSIDE the skill at config/providers/<name>.json (not the user home root).
- Secrets never enter git (see .gitignore).
- Placeholder values (YOUR_*) are treated as "not configured".
- Environment variables act as an override/fallback.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILL_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = SKILL_ROOT / "config" / "providers"

# Env var fallback per provider
ENV_KEYS: Dict[str, List[str]] = {
    "stepfun": ["STEPFUN_API_KEY"],
    "seedream": ["ARK_API_KEY"],
    "openai": ["OPENAI_API_KEY", "IMAGEGEN_API_KEY"],
}

PLACEHOLDER_PREFIXES = ("YOUR_", "your_", "CHANGEME", "changeme", "<")


def config_path(name: str) -> Path:
    return CONFIG_DIR / f"{name}.json"


def is_placeholder(value: Optional[str]) -> bool:
    if not value or not isinstance(value, str):
        return True
    stripped = value.strip()
    if not stripped:
        return True
    return any(stripped.startswith(p) for p in PLACEHOLDER_PREFIXES)


def load(name: str) -> Dict[str, Any]:
    p = config_path(name)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save(name: str, data: Dict[str, Any]) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    p = config_path(name)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def clear(name: str) -> bool:
    p = config_path(name)
    if p.exists():
        p.unlink()
        return True
    return False


def get_api_key(name: str) -> Optional[str]:
    """Read key from config file, falling back to env vars. Placeholders are ignored."""
    cfg = load(name)
    key = cfg.get("apiKey") or cfg.get("api_key")
    if not is_placeholder(key):
        return key
    for env_name in ENV_KEYS.get(name, []):
        env_val = os.environ.get(env_name)
        if not is_placeholder(env_val):
            return env_val
    return None


def get_base_url(name: str) -> Optional[str]:
    cfg = load(name)
    url = cfg.get("baseUrl") or cfg.get("base_url")
    if not is_placeholder(url):
        return url
    env_val = os.environ.get("IMAGEGEN_BASE_URL")
    return env_val if not is_placeholder(env_val) else None


def status(name: str) -> Dict[str, Any]:
    """Report configuration state for a provider (never returns the key itself)."""
    cfg = load(name)
    key = get_api_key(name)
    from_env = False
    if key:
        file_key = cfg.get("apiKey") or cfg.get("api_key")
        from_env = is_placeholder(file_key)
    return {
        "provider": name,
        "configured": bool(key),
        "keySource": "env" if from_env else ("file" if key else None),
        "baseUrl": get_base_url(name),
        "configPath": str(config_path(name)),
        "configExists": config_path(name).exists(),
    }


def all_known() -> List[str]:
    return ["stepfun", "seedream", "openai"]
