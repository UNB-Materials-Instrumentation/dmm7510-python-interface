"""
Measurement primitives: configure instrument and capture resistance readings.
"""

import time
from statistics import mean, median
from typing import Iterable, Literal

from dmm7510.instrument import write, query


def configure_2wire_resistance(inst, nplc: float = 10.0) -> None:
    """
    Configure the DMM7510 for a basic 2-wire resistance measurement.
    """
    if nplc <= 0:
        raise ValueError("nplc must be > 0")
    write(inst, "*RST")
    write(inst, ':SENS:FUNC \"RES\"')
    write(inst, ":SENS:RES:RANG:AUTO ON")
    write(inst, f":SENS:RES:NPLC {nplc}")
    write(inst, ":SENS:RES:AZER ON")
    write(inst, "*CLS")


def read_resistance_once(inst) -> float:
    """
    Take a single 2-wire resistance measurement and return value in ohms.

    :MEAS:RES? performs a configure + trigger + read in one command,
    which is simpler and more robust than using :READ? directly.
    """
    response = query(inst, ":MEAS:RES?")
    first_field = response.split(",")[0]
    return float(first_field)


def _aggregate(values: Iterable[float], method: Literal["mean", "median"] = "mean") -> float:
    vals = list(values)
    if not vals:
        raise ValueError("No readings to aggregate")
    if method == "median":
        return median(vals)
    return mean(vals)


def read_resistance_average(
    inst,
    count: int = 5,
    delay_s: float = 0.2,
    aggregate: Literal["mean", "median"] = "mean",
) -> float:
    """
    Take multiple resistance measurements and return the aggregated value (ohms).

    :param inst: Open DMM instrument handle
    :param count: Number of readings to aggregate
    :param delay_s: Delay between readings, in seconds
    :param aggregate: 'mean' or 'median' to reduce noise
    """
    if count <= 0:
        raise ValueError("count must be >= 1")
    if delay_s < 0:
        raise ValueError("delay_s cannot be negative")

    readings = []

    for i in range(count):
        r = read_resistance_once(inst)
        readings.append(r)
        if i < count - 1:
            time.sleep(delay_s)

    return _aggregate(readings, aggregate)
