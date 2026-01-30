"""
Continuous measurement loop with CSV logging and optional dry-run.
"""

import csv
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from dmm7510.config import load_config
from dmm7510.instrument import dmm_connection, query
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
    interval_s: float = typer.Option(1.0, help="Seconds between displayed readings"),
    count: int = typer.Option(20, help="Samples to average per reading"),
    delay_s: float = typer.Option(0.1, help="Delay between samples (s)"),
    nplc: float = typer.Option(10.0, help="Integration time (NPLC)"),
    out_csv: Optional[Path] = typer.Option(None, help="Write readings to CSV file"),
    visa_resource: Optional[str] = typer.Option(None, "--visa-resource", help="Override VISA resource"),
    log_file: Optional[Path] = typer.Option(None, "--log-file", help="Optional log file path"),
    dry_run: bool = typer.Option(False, help="Skip instrument I/O for demonstration"),
    length_m: Optional[float] = typer.Option(None, help="Probe spacing / sample length in meters"),
    area_m2: Optional[float] = typer.Option(None, help="Cross-sectional area in square meters"),
) -> None:
    _setup_logging(log_file)
    cfg = load_config(override_visa=visa_resource)

    if interval_s <= 0:
        raise typer.BadParameter("interval_s must be > 0")

    geometry = None
    if length_m and area_m2:
        geometry = Geometry(length_m=length_m, area_m2=area_m2)
    elif length_m or area_m2:
        raise typer.BadParameter("Both length_m and area_m2 must be provided to compute conductivity")

    if dry_run:
        typer.echo("Dry run: would start loop with current settings.")
        return

    csv_writer = None
    csv_file = None
    if out_csv:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        csv_file = out_csv.open("w", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        headers = ["timestamp_iso", "resistance_ohm"]
        if geometry:
            headers.append("conductivity_s_per_m")
        csv_writer.writerow(headers)

    with dmm_connection(cfg) as inst:
        identity = query(inst, "*IDN?")
        typer.echo(f"Connected to: {identity}")

        configure_2wire_resistance(inst, nplc=nplc)

        typer.echo("Starting resistance measurements. Press Ctrl+C to stop.\n")

        try:
            while True:
                resistance = read_resistance_average(inst, count=count, delay_s=delay_s)
                sigma = conductivity_s_per_m(resistance, geometry)
                timestamp = datetime.now().isoformat(timespec="seconds")
                line = f"{timestamp}  R = {resistance:.6f} ohm"
                if sigma is not None:
                    line += f"  σ = {sigma:.6f} S/m"
                typer.echo(line)
                if csv_writer:
                    row = [timestamp, resistance]
                    if sigma is not None:
                        row.append(sigma)
                    csv_writer.writerow(row)
                time.sleep(interval_s)
        except KeyboardInterrupt:
            typer.echo("\nStopped by user.")
        finally:
            if csv_file:
                csv_file.close()


if __name__ == "__main__":
    app()
