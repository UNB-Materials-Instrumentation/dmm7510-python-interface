import pyvisa


def main() -> None:
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print("Found resources:", resources)

    if resources:
        dmm = rm.open_resource(resources[0])
        dmm.read_termination = "\n"
        dmm.write_termination = "\n"

        idn = dmm.query("*IDN?")
        print("Instrument ID:", idn)
    else:
        print("No VISA instruments found.")


if __name__ == "__main__":
    main()
