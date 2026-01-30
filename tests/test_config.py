import os
from dmm7510.config import load_config


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("VISA_RESOURCE", "USB::SIM::INSTR")
    monkeypatch.setenv("DMM_TIMEOUT_MS", "5000")
    cfg = load_config()
    assert cfg.visa_resource == "USB::SIM::INSTR"
    assert cfg.timeout_ms == 5000


def test_cli_override_wins(monkeypatch):
    monkeypatch.setenv("VISA_RESOURCE", "ENV")
    cfg = load_config(override_visa="CLI")
    assert cfg.visa_resource == "CLI"
