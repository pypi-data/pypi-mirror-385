import json
import os
from pathlib import Path
import socket

import pytest

from inceptum import config


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_pseudo_keys_and_escape(monkeypatch, tmp_path):
    # Point INCEPTUM at a temp directory
    base = tmp_path / "cfgroot"
    monkeypatch.setenv("INCEPTUM", str(base))

    # No files needed to check pseudo-keys
    assert config("dir") == str(base.resolve())
    assert isinstance(config("host"), str)
    assert config("env") == "run"

    # Collision escape: a real group called "env"
    write_json(base / "any" / "env.json", {"value": 123})
    # meta=True returns pseudo-key
    assert config("env") == "run"
    # meta=False returns actual config
    assert config("env", meta=False) == {"value": 123}
    assert config("env.value", meta=False) == 123


def test_layer_precedence_and_environment_block(monkeypatch, tmp_path):
    base = tmp_path / "cfg"
    monkeypatch.setenv("INCEPTUM", str(base))
    # Fake hostname for deterministic behavior
    monkeypatch.setattr(socket, "gethostname", lambda: "h1")

    # any layer
    write_json(base / "any" / "svc.json", {"a": 1, "b": {"x": 1}, "ENVIRONMENT": {"dev": {"a": 2}}})
    # host layer
    write_json(base / "h1" / "svc.json", {"b": {"x": 10, "y": 20}})
    # env layer
    write_json(base / "dev" / "svc.json", {"b": {"y": 200, "z": 300}})

    cfg_dev = config("svc", env="dev")
    assert cfg_dev == {"a": 2, "b": {"x": 10, "y": 200, "z": 300}}

    # ENVIRONMENT block must be removed
    assert "ENVIRONMENT" not in cfg_dev

    # Different env should give different result - also tests cache keying
    cfg_prod = config("svc", env="run")
    assert cfg_prod == {"a": 1, "b": {"x": 10, "y": 20}}


def test_nested_lookup_and_default(monkeypatch, tmp_path):
    base = tmp_path / "root"
    monkeypatch.setenv("INCEPTUM", str(base))
    write_json(base / "any" / "svc.json", {"a": {"b": {"c": 7}}})

    assert config("svc.a.b.c") == 7
    assert config("svc.a.b.d", default="missing") == "missing"
    assert config("missing_service", default={"x": 1}) == {"x": 1}


def test_venv_override(monkeypatch, tmp_path):
    # No INCEPTUM set
    monkeypatch.delenv("INCEPTUM", raising=False)

    # Simulate a venv with a config override
    venv = tmp_path / "venv"
    (venv / "config" / "inceptum").mkdir(parents=True)
    monkeypatch.setenv("VIRTUAL_ENV", str(venv))

    write_json(venv / "config" / "inceptum" / "any" / "svc.json", {"k": 1})

    # Should resolve config under the venv
    assert config("dir") == str((venv / "config" / "inceptum").resolve())
    assert config("svc") == {"k": 1}


def test_venv_fallback_dir(monkeypatch, tmp_path):
    # If <venv>/config/inceptum does not exist but <venv>/inceptum does, use it
    monkeypatch.delenv("INCEPTUM", raising=False)
    venv = tmp_path / "venv2"
    (venv / "inceptum").mkdir(parents=True)
    monkeypatch.setenv("VIRTUAL_ENV", str(venv))

    write_json(venv / "inceptum" / "any" / "svc.json", {"k": 2})

    assert config("dir") == str((venv / "inceptum").resolve())
    assert config("svc") == {"k": 2}


def test_extras_lowest_precedence_and_placeholders(monkeypatch, tmp_path):
    base = tmp_path / "cfgx"
    defaults = tmp_path / "defaults"
    host = "hX"
    env = "dev"

    monkeypatch.setenv("INCEPTUM", str(base))
    monkeypatch.setattr(socket, "gethostname", lambda: host)

    # Extras file: a list, mixing dir stems and a stem with {name}
    (base).mkdir(parents=True, exist_ok=True)
    (defaults).mkdir(parents=True, exist_ok=True)
    extras = [
        str(defaults),                           # relative to base_dir? we give absolute here
        "{env}-common/services",                 # relative, will be base_dir/<env>-common/services/<name>.*
        "/missing/path/{name}",                  # missing should be ignored
    ]
    (base / "extras.json").write_text(json.dumps(extras), encoding="utf-8")

    # Defaults layer - will be overridden by later layers
    write_json(defaults / "svc.json", {"a": 1, "b": {"x": 1}, "from": "defaults"})

    # any and env layers
    write_json(base / "any" / "svc.json", {"b": {"x": 10}, "from": "any"})
    write_json(base / f"{env}-common" / "services" / "svc.json", {"b": {"y": 20}, "from": "extras-env-rel"})
    write_json(base / env / "svc.json", {"b": {"z": 30}, "from": "env"})

    cfg = config("svc", env=env)

    # Defaults present but overridden where appropriate
    assert cfg["a"] == 1                # only in defaults
    assert cfg["b"]["x"] == 10          # overridden by 'any'
    assert cfg["b"]["y"] == 20          # from extras relative env dir
    assert cfg["b"]["z"] == 30          # from env layer
    assert cfg["from"] == "env"         # highest among provided 'from' keys

