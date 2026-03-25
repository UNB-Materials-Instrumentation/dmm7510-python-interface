# test_identity.py

from dmm7510.instrument import get_idn


def main() -> None:
    try:
        idn = get_idn()
        print("DMM7510 identity string:")
        print(idn)
    except Exception as exc:
        print("Failed to communicate with DMM7510.")
        print("Error:", repr(exc))


if __name__ == "__main__":
    main()
