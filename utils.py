from dmm_scpi import write, query


def configure_2wire_resistance(sock, nplc: float = 10.0) -> None:
    """
    Configure the DMM7510 for a basic 2-wire resistance measurement.
    """
    # Reset to default state
    write(sock, "*RST")

    # Select 2-wire resistance function
    write(sock, ':SENS:FUNC "RES"')

    # Use auto-range to start
    write(sock, ":SENS:RES:RANG:AUTO ON")

    # Set integration time (Number of Power Line Cycles).
    # 'NPLC' is a SCPI keyword, not a typo.
    write(sock, f":SENS:RES:NPLC {nplc}")

    # Enable autozero to reduce offset drift
    write(sock, ":SENS:RES:AZER ON")

    # Clear status system
    write(sock, "*CLS")


def read_resistance_once(sock) -> float:
    """
    Trigger a single resistance measurement and return value in ohms.
    """
    response = query(sock, ":READ?")
    first_field = response.split(",")[0]
    return float(first_field)
