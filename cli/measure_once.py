"""
CLI entrypoint for single-run measurement.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import typer

from dmm7510.config import load_config
from dmm7510.instrument import dmm_connection, get_idn
from dmm7510.reading import configure_2wire_resistance, read_resistance_average
from dmm7510.measurement import Geometry, conductivity_s_per_m

app = typer.Typer(add_completion=False)
log = logging.getLogger(__name__)


def _setup_logging(log_path: Optional[Path]) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logging.getLogger().addHandler(fh)


@app.command()
def main(
    count: int = typer.Option(50, help="Number of samples to average"),
    delay_s: float = typer.Option(0.05, help="Delay between samples (s)"),
    nplc: float = typer.Option(10.0, help="Integration time (NPLC)"),
    visa_resource: Optional[str] = typer.Option(None, "--visa-resource", help="Override VISA resource"),
    log_file: Optional[Path] = typer.Option(None, "--log-file", help="Optional log file path"),
    dry_run: bool = typer.Option(False, help="Skip instrument I/O for demonstration"),
    length_m: Optional[float] = typer.Option(None, help="Probe spacing / sample length in meters"),
    area_m2: Optional[float] = typer.Option(None, help="Cross-sectional area in square meters"),
) -> None:
    _setup_logging(log_file)
    cfg = load_config(override_visa=visa_resource)

    geometry = None
    if length_m and area_m2:
        geometry = Geometry(length_m=length_m, area_m2=area_m2)
    elif length_m or area_m2:
        raise typer.BadParameter("Both length_m and area_m2 must be provided to compute conductivity")

    if dry_run:
        typer.echo("Dry run: would perform measurement with current settings.")
        typer.echo(json.dumps(cfg.__dict__, indent=2))
        return

    with dmm_connection(cfg) as inst:
        try:
            inst.clear()
        except Exception:
            log.debug("Instrument clear not supported; continuing.")

        idn_reply = get_idn(cfg)
        typer.echo(f"Connected to instrument: {idn_reply}")

        configure_2wire_resistance(inst, nplc=nplc)

        resistance_ohm = read_resistance_average(
            inst,
            count=count,
            delay_s=delay_s,
        )
        typer.echo(f"Measured resistance: {resistance_ohm:.6f} ohm")
        sigma = conductivity_s_per_m(resistance_ohm, geometry)
        if sigma is not None:
            typer.echo(f"Conductivity: {sigma:.6f} S/m")


if __name__ == "__main__":
    app()
