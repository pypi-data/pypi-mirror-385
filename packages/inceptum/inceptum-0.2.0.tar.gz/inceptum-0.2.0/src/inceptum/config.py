# [code by GPT-5](urn:uuid:2a730199-19b3-8597-a62a-a384fe1923d8)
# [Adding support for extras/[name]/config.{yaml,yml,json}](urn:uuid:2a730199-1a08-8aeb-9a2a-425e432f5db1)

import json
import os
import socket
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Optional

__all__ = ["config"]

# Cache keyed by (base_dir, env, host, name)
_CACHE: dict[tuple[str, str, str, str], dict] = {}


def _user_config_root() -> Path:
    """
    Return the per-user config root for the current platform, without the app suffix.
    - Linux and other Unix: $XDG_CONFIG_HOME or ~/.config
    - macOS: ~/Library/Application Support
    - Windows: %APPDATA%
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        return Path(base) if base else Path.home() / "AppData" / "Roaming"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    base = os.environ.get("XDG_CONFIG_HOME")
    return Path(base) if base else Path.home() / ".config"


def _venv_root() -> Optional[Path]:
    """
    Detect the current virtual environment root if any.
    Priority:
      - VIRTUAL_ENV
      - CONDA_PREFIX
      - sys.prefix if it differs from sys.base_prefix
    """
    ve = os.environ.get("VIRTUAL_ENV")
    if ve:
        return Path(ve)
    cp = os.environ.get("CONDA_PREFIX")
    if cp:
        return Path(cp)
    base_prefix = getattr(sys, "base_prefix", sys.prefix)
    if sys.prefix and sys.prefix != base_prefix:
        return Path(sys.prefix)
    return None


def _base_dir_from_env() -> Path:
    """
    Resolve the base config directory.
    Priority:
      1. INCEPTUM if set
      2. If inside a venv or conda and a venv override exists, use it:
           <venv>/config/inceptum  or  <venv>/inceptum
      3. Platform config root + "inceptum"
    """
    env_dir = os.environ.get("INCEPTUM")
    if env_dir:
        return Path(env_dir).expanduser().absolute()

    venv = _venv_root()
    if venv:
        for candidate in (venv / "config" / "inceptum", venv / "inceptum"):
            if candidate.exists():
                return candidate.absolute()

    return (_user_config_root() / "inceptum").absolute()


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _load_layer(stem: Path) -> dict:
    """
    Load a config layer from stem.{yaml,yml,json}. Returns {} if none exist or file is empty.
    """
    candidates = [stem.with_suffix(".yaml"), stem.with_suffix(".yml"), stem.with_suffix(".json")]
    for p in candidates:
        if p.exists():
            try:
                text = _read_text(p)
                if text is None:
                    return {}
                if p.suffix in {".yaml", ".yml"}:
                    import yaml  # lazy import
                    data = yaml.safe_load(text)
                else:
                    data = json.loads(text)
            except Exception:
                return {}
            return data if isinstance(data, dict) and data is not None else {}
    return {}


def _deep_merge(dst: dict, src: Mapping) -> dict:
    """
    Recursively merge src into dst. Dicts are merged, other types replace.
    """
    for k, v in src.items():
        if isinstance(v, Mapping) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)  # type: ignore[index]
        else:
            dst[k] = v
    return dst


def _apply_environment_block(data: dict, env: str) -> dict:
    """
    If the data has an ENVIRONMENT mapping, merge data with ENVIRONMENT[env].
    Remove the ENVIRONMENT key from the final result.
    """
    env_block = data.get("ENVIRONMENT")
    if isinstance(env_block, Mapping):
        overrides = env_block.get(env)
        if isinstance(overrides, Mapping):
            _deep_merge(data, overrides)
        data.pop("ENVIRONMENT", None)
    return data


def _get_in(mapping: Mapping, keys: list[str]) -> Any:
    """
    Walk a nested mapping by a list of keys.
    """
    current: Any = mapping
    for k in keys:
        if not isinstance(current, Mapping) or k not in current:
            raise KeyError(k)
        current = current[k]
    return current


def _load_extras_list(base_dir: Path) -> list[str]:
    """
    Read extra stems from one of:
      base_dir/extras.yaml | extras.yml | extras.json

    Allowed formats:
      - A list of strings (each string is a stem, placeholders allowed)
      - An object with key "extras": list[str]
    """
    candidates = [base_dir / "extras.yaml", base_dir / "extras.yml", base_dir / "extras.json"]
    for p in candidates:
        if not p.exists():
            continue
        text = _read_text(p)
        if text is None:
            continue
        try:
            if p.suffix in {".yaml", ".yml"}:
                import yaml  # lazy import
                data = yaml.safe_load(text)
            else:
                data = json.loads(text)
        except Exception:
            return []
        if isinstance(data, list):
            return [x for x in data if isinstance(x, str)]
        if isinstance(data, dict):
            extras = data.get("extras")
            if isinstance(extras, list):
                return [x for x in extras if isinstance(x, str)]
        return []
    return []


def _extra_stems(base_dir: Path, name: str, env_name: str, host: str) -> list[Path]:
    """
    Compute extra stems based on the extras file.
    Each entry is a base name that needs the service name added, unless the entry includes {name}.
    Placeholders {name}, {env}, {host} are supported.
    Relative paths are resolved relative to base_dir. ~ and environment variables are expanded.
    """
    stems: list[Path] = []
    for entry in _load_extras_list(base_dir):
        had_name = "{name}" in entry
        formatted = (
            entry.replace("{name}", name)
            .replace("{env}", env_name)
            .replace("{host}", host)
        )
        path = Path(os.path.expandvars(os.path.expanduser(formatted)))
        if not path.is_absolute():
            path = base_dir / path
        stem = path if had_name else path / name
        stems.append(stem)
    return stems


def config(*args: str, default: Any = None, env: Optional[str] = None, meta: bool = True) -> Any:
    """
    Load configuration values.

    Usage:
      - config("service") -> merged dict from relevant layers
      - config("service.key.subkey") or config("service", "key", "subkey")
      - config("service.key", default=42)
      - config("service", env="development")
      - Pseudo-keys if meta is True (default):
          config("host") -> hostname
          config("env")  -> effective environment
          config("dir")  -> absolute base config directory
        Pass meta=False to treat these as real config group names.

    Sources and precedence within the base directory:
      extras (if any)  ->  any/<name>  ->  <hostname>/<name>  ->  <env>/<name>

    Optional ENVIRONMENT overrides inside any layer are applied if present.
    """
    # Flatten dotted segments
    parts = [p for arg in args for p in arg.split(".")]
    if not parts:
        raise ValueError("config() requires at least one key, e.g. 'service' or 'service.key'")

    base_dir = _base_dir_from_env()
    env_name = env or os.getenv('INCEPTUM_ENV', 'run')
    host = socket.gethostname()

    # Pseudo-keys with match syntax
    if meta and len(parts) == 1 and parts[0] in {"host", "env", "dir"}:
        match parts[0]:
            case "host":
                return host
            case "env":
                return env_name
            case "dir":
                return str(base_dir)

    name = parts[0]
    cache_key = (str(base_dir), env_name, host, name)

    cached = _CACHE.get(cache_key)
    if cached is None:
        merged: dict = {}

        # 1) extras - lowest precedence
        for stem in _extra_stems(base_dir, name, env_name, host):
            layer = _load_layer(stem)
            if layer:
                _apply_environment_block(layer, env_name)
                _deep_merge(merged, layer)

        # 2) built-in layers
        stems = [
            base_dir / "any" / name,
            base_dir / host / name,
            base_dir / env_name / name,
        ]
        for stem in stems:
            layer = _load_layer(stem)
            if layer:
                _apply_environment_block(layer, env_name)
                _deep_merge(merged, layer)

        cached = merged
        _CACHE[cache_key] = cached

    if len(parts) == 1:
        return cached if cached else default

    try:
        return _get_in(cached, parts[1:])
    except KeyError:
        return default
