# dmm7510-python-interface
Work study- Instrument development to measure resistance for materials through Keithley dmmm7510

## Setup
1) Install deps (Python 3.11+): `pip install -e .[dev]`  
2) Optional: create `.env` with `VISA_RESOURCE=USB0::...::INSTR` and overrides like `DMM_TIMEOUT_MS`.  
3) Verify connectivity: `python test_identity.py`

## Commands
- Single run: `measure-once --count 50 --delay-s 0.05 --nplc 10`
- Continuous: `resistance-loop --count 20 --delay-s 0.1 --interval-s 1 --out-csv runs/run.csv`
- Dry run: add `--dry-run`. Override device: `--visa-resource <name>`.
- Conductivity: add geometry `--length-m <m> --area-m2 <m^2>` to print σ and include in CSV.

## Architecture
- Package: `dmm7510/` (config, instrument I/O, reading primitives, measurement domain).
- CLIs: `cli/` provides Typer apps wrapping the package.
- Tests: `tests/` use mocks/pyvisa-sim to validate logic; no hardware needed.
- Utilities/demos: `test_identity.py`, `test1.py`.

## Logging & data
- `--log-file` writes INFO logs; `resistance-loop` writes CSV when `--out-csv` is set.

## CI
GitHub Actions workflow runs pytest on push/PR (Python 3.11).
