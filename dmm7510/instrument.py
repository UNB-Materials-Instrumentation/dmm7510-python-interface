"""
Thin wrapper around pyvisa for the DMM7510 with retries and sane defaults.
SCPI command strings are unchanged to avoid regressions.
"""

from contextlib import contextmanager
from typing import Optional
import time
import logging

import pyvisa

from dmm7510.config import AppConfig, load_config

log = logging.getLogger(__name__)

_rm: Optional[pyvisa.ResourceManager] = None


def _get_resource_manager() -> pyvisa.ResourceManager:
    """
    Lazily create and cache the global VISA ResourceManager.
    """
    global _rm
    if _rm is None:
        _rm = pyvisa.ResourceManager()
    return _rm


def _open_instrument(app_cfg: AppConfig):
    """
    Open the DMM7510 VISA resource.

    If visa_resource is set, that resource name is used.
    Otherwise, the first available VISA resource is opened.
    """
    rm = _get_resource_manager()

    if app_cfg.visa_resource:
        log.debug("Opening VISA resource %s", app_cfg.visa_resource)
        return rm.open_resource(app_cfg.visa_resource)

    resources = rm.list_resources()
    if not resources:
        raise RuntimeError("No VISA instruments found. Is the DMM7510 connected and powered on?")

    inst_name = resources[0]
    log.info("VISA_RESOURCE not set; using first available: %s", inst_name)
    return rm.open_resource(inst_name)


@contextmanager
def dmm_connection(app_cfg: Optional[AppConfig] = None):
    cfg = app_cfg or load_config()
    attempt = 0
    inst = None
    last_exc: Optional[Exception] = None

    while attempt < cfg.max_retries and inst is None:
        attempt += 1
        try:
            inst = _open_instrument(cfg)
            inst.read_termination = "\n"
            inst.write_termination = "\n"
            inst.timeout = cfg.timeout_ms
        except Exception as exc:  # pyvisa.VisaIOError or others
            last_exc = exc
            log.warning("Instrument open failed (attempt %s/%s): %s", attempt, cfg.max_retries, exc)
            time.sleep(cfg.retry_delay_s)

    if inst is None:
        raise RuntimeError(f"Failed to open instrument after {cfg.max_retries} attempts") from last_exc

    try:
        yield inst
    finally:
        try:
            inst.close()
        except Exception:
            log.exception("Error while closing instrument; continuing")


def write(inst, cmd: str) -> None:
    """
    Send a SCPI command that does NOT expect a response.
    """
    inst.write(cmd)


def query(inst, cmd: str) -> str:
    """
    Send a SCPI query (command ending with '?') and return the reply as a string.
    """
    return inst.query(cmd).strip()


def get_idn(cfg: Optional[AppConfig] = None) -> str:
    """
    Convenience function: open a short connection and return *IDN? reply.
    """
    with dmm_connection(cfg) as inst:
        return query(inst, "*IDN?")
