# dmm_scpi.py

import socket
from contextlib import contextmanager
from typing import Generator

from config import DMM_IP, DMM_PORT


def _create_connection() -> socket.socket:
    """
    Create a TCP connection to the DMM7510 using the IP/port in config.py.
    Raises socket.error if connection fails.
    """
    return socket.create_connection((DMM_IP, DMM_PORT), timeout=5)


@contextmanager
def dmm_connection() -> Generator[socket.socket, None, None]:
    """
    Context manager that opens a connection to the DMM and closes it
    when done.

    Usage:
        with dmm_connection() as s:
            write(s, "*RST")
    """
    s = _create_connection()
    try:
        yield s
    finally:
        s.close()


def write(sock: socket.socket, cmd: str) -> None:
    """
    Send a SCPI command that does NOT expect a response.
    Automatically appends a newline.
    """
    msg = (cmd + "\n").encode("ascii")
    sock.sendall(msg)


def query(sock: socket.socket, cmd: str) -> str:
    """
    Send a SCPI query (command ending with '?') and return the reply as a string.
    """
    write(sock, cmd)
    data = sock.recv(4096)
    return data.decode("ascii").strip()


def get_idn() -> str:
    """
    Convenience function: open a short connection and return *IDN? reply.
    """
    with dmm_connection() as s:
        return query(s, "*IDN?")
