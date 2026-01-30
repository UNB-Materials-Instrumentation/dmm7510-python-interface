import math
import pytest

from dmm7510.measurement import Geometry, conductivity_s_per_m


def test_geometry_validation():
    with pytest.raises(ValueError):
        Geometry(length_m=0, area_m2=1)
    with pytest.raises(ValueError):
        Geometry(length_m=1, area_m2=0)


def test_conductivity_calculation():
    g = Geometry(length_m=0.02, area_m2=1e-6)  # 20 mm length, 1 mm^2 area
    sigma = conductivity_s_per_m(resistance_ohm=10.0, geometry=g)
    assert math.isclose(sigma, 2000.0, rel_tol=1e-6)


def test_conductivity_none_without_geometry():
    assert conductivity_s_per_m(10.0, None) is None
