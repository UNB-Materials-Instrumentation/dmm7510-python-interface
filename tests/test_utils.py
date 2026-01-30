from dmm7510.reading import read_resistance_average, configure_2wire_resistance


class FakeInstrument:
    def __init__(self, responses):
        self._responses = responses
        self.commands = []

    def write(self, cmd):
        self.commands.append(cmd)

    def query(self, cmd):
        self.commands.append(cmd)
        return self._responses.pop(0)


def test_read_resistance_average_mean():
    inst = FakeInstrument(["1.0,0,0", "3.0,0,0"])
    result = read_resistance_average(inst, count=2, delay_s=0, aggregate="mean")
    assert result == 2.0


def test_read_resistance_average_median():
    inst = FakeInstrument(["1.0,0,0", "10.0,0,0", "3.0,0,0"])
    result = read_resistance_average(inst, count=3, delay_s=0, aggregate="median")
    assert result == 3.0


def test_configure_sends_expected_commands():
    inst = FakeInstrument([])
    configure_2wire_resistance(inst, nplc=5.0)
    assert ":SENS:FUNC \"RES\"" in inst.commands
    assert any(cmd.startswith(":SENS:RES:NPLC") for cmd in inst.commands)
