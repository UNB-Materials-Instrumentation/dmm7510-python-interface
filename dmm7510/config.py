"""
Configuration loader for the DMM7510 interface.

Supports:
- .env file (python-dotenv) for local overrides
- environment variables (take precedence)
- safe defaults that still allow auto-discovery
"""

from dataclasses import dataclass
from typing import Optional
import os

from dotenv import load_dotenv

# Load .env if present; env vars still win
load_dotenv()


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(key, default)
    return val if val not in {"", None} else default


@dataclass(frozen=True)
class AppConfig:
    visa_resource: Optional[str]
    timeout_ms: int = 10_000
    max_retries: int = 3
    retry_delay_s: float = 0.5
    nplc_default: float = 10.0
    sample_delay_default: float = 0.1
    sample_count_default: int = 10


def load_config(override_visa: Optional[str] = None) -> AppConfig:
    visa = override_visa or _env("VISA_RESOURCE")
    # None/"" means auto-select first instrument
    timeout_ms = int(_env("DMM_TIMEOUT_MS", "10000"))
    max_retries = max(1, int(_env("DMM_MAX_RETRIES", "3")))
    retry_delay_s = float(_env("DMM_RETRY_DELAY_S", "0.5"))
    nplc_default = float(_env("DMM_NPLC_DEFAULT", "10.0"))
    sample_delay_default = float(_env("DMM_SAMPLE_DELAY", "0.1"))
    sample_count_default = int(_env("DMM_SAMPLE_COUNT", "10"))

    if timeout_ms <= 0:
        raise ValueError("DMM_TIMEOUT_MS must be positive")
    if retry_delay_s < 0:
        raise ValueError("DMM_RETRY_DELAY_S cannot be negative")
    if sample_count_default <= 0:
        raise ValueError("DMM_SAMPLE_COUNT must be >= 1")
    if nplc_default <= 0:
        raise ValueError("DMM_NPLC_DEFAULT must be > 0")

    return AppConfig(
        visa_resource=visa,
        timeout_ms=timeout_ms,
        max_retries=max_retries,
        retry_delay_s=retry_delay_s,
        nplc_default=nplc_default,
        sample_delay_default=sample_delay_default,
        sample_count_default=sample_count_default,
    )
