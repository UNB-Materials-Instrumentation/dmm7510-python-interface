# dmm_scpi.py

from contextlib import contextmanager
from typing import Generator, Optional

import pyvisa

from config import VISA_RESOURCE


_rm: Optional[pyvisa.ResourceManager] = None


def _get_resource_manager() -> pyvisa.ResourceManager:
    """
    Lazily create and cache the global VISA ResourceManager.
    """
    global _rm
    if _rm is None:
        _rm = pyvisa.ResourceManager()
    return _rm


def _open_instrument():
    """
    Open the DMM7510 VISA resource.

    If VISA_RESOURCE is set in config.py, that resource name is used.
    Otherwise, the first available VISA resource is opened.
    """
    rm = _get_resource_manager()

    if VISA_RESOURCE:
        return rm.open_resource(VISA_RESOURCE)

    resources = rm.list_resources()
    if not resources:
        raise RuntimeError("No VISA instruments found. Is the DMM7510 connected and powered on?")

    # Use the first resource by default
    inst = rm.open_resource(resources[0])
    return inst


@contextmanager
def dmm_connection():
    inst = _open_instrument()

    # Configure line termination and timeout for SCPI over VISA
    inst.read_termination = "\n"
    inst.write_termination = "\n"
    inst.timeout = 10000  # 10 seconds, in milliseconds

    try:
        yield inst
    finally:
        inst.close()


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


def get_idn() -> str:
    """
    Convenience function: open a short connection and return *IDN? reply.
    """
    with dmm_connection() as inst:
        return query(inst, "*IDN?")
