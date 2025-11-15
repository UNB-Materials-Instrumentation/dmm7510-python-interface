# measure_resistance_once.py

from dmm_scpi import dmm_connection, query
from utils import configure_2wire_resistance, read_resistance_once


def main() -> None:
    with dmm_connection() as sock:
        identity = query(sock, "*IDN?")
        print("Connected to:", identity)

        configure_2wire_resistance(sock)

        resistance = read_resistance_once(sock)
        print(f"Measured resistance: {resistance:.6f} ohm")


if __name__ == "__main__":
    main()
