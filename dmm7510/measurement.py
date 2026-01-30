"""
Measurement domain helpers: geometry metadata and conductivity calculations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Geometry:
    """
    Sample geometry needed for conductivity:
    - length_m: distance between probes (meters)
    - area_m2: cross-sectional area (square meters)
    """

    length_m: float
    area_m2: float

    def __post_init__(self):
        if self.length_m <= 0:
            raise ValueError("length_m must be positive")
        if self.area_m2 <= 0:
            raise ValueError("area_m2 must be positive")


def conductivity_s_per_m(resistance_ohm: float, geometry: Optional[Geometry]) -> Optional[float]:
    """
    Compute electrical conductivity σ (S/m) from resistance and geometry.
    σ = L / (R * A)
    Returns None when geometry is missing.
    """
    if geometry is None:
        return None
    if resistance_ohm <= 0:
        raise ValueError("resistance_ohm must be positive to compute conductivity")
    return geometry.length_m / (resistance_ohm * geometry.area_m2)
