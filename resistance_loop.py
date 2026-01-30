# resistance_loop.py

import time
from datetime import datetime

from dmm_scpi import dmm_connection, query
from utils import configure_2wire_resistance, read_resistance_average


def main() -> None:
    with dmm_connection() as inst:
        identity = query(inst, "*IDN?")
        print("Connected to:", identity)

        configure_2wire_resistance(inst)

        print("Starting resistance measurements. Press Ctrl+C to stop.\n")

        try:
            while True:
                resistance = read_resistance_average(inst, count=20, delay_s=0.1)
                timestamp = datetime.now().isoformat(timespec="seconds")
                print(f"{timestamp}  R = {resistance:.6f} ohm")
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nStopped by user.")


if __name__ == "__main__":
    main()
