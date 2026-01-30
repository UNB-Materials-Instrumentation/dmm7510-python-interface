# utils.py
import time
from statistics import mean
from dmm_scpi import write, query


def configure_2wire_resistance(inst, nplc: float = 10.0) -> None:
    """
    Configure the DMM7510 for a basic 2-wire resistance measurement.
    """
    write(inst, "*RST")
    write(inst, ':SENS:FUNC "RES"')
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
    # If you want to see the raw reply for debugging, uncomment:
    # print("RAW :MEAS:RES? response:", repr(response))
    first_field = response.split(",")[0]
    return float(first_field)

def read_resistance_average(
    inst,
    count: int = 5,
    delay_s: float = 0.2,
) -> float:
    """
    Take multiple resistance measurements and return the average (ohms).

    :param inst: Open DMM instrument handle
    :param count: Number of readings to average
    :param delay_s: Delay between readings, in seconds
    """
    readings = []

    for i in range(count):
        r = read_resistance_once(inst)
        readings.append(r)
        # Short pause between readings, except after the last one
        if i < count - 1:
            time.sleep(delay_s)

    return mean(readings)