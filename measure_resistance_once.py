# measure_resistance_once.py

from dmm_scpi import dmm_connection, query, get_idn
from utils import (
    configure_2wire_resistance,
    read_resistance_average,
)


def main() -> None:
    with dmm_connection() as inst:
        # Make sure any previous output is cleared
        try:
            inst.clear()  # PyVISA Instrument.clear()
        except Exception:
            # Not critical; continue even if clear is not supported
            pass

        # 1) Ask who we are talking to
        idn_reply = get_idn()
        print(f"Connected to instrument: {idn_reply}")

        # 2) Configure resistance mode
        configure_2wire_resistance(inst)

        # 3) Take a single resistance measurement
        resistance_ohm = read_resistance_average(
            inst,
            count=50,      # number of samples
            delay_s=0.05,  # pause between samples (seconds)
        )
        print(f"Measured resistance: {resistance_ohm:.6f} ohm")


if __name__ == "__main__":
    main()
