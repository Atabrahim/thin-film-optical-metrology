"""Analytical limits and independent tmm 0.2.0 reference checks."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from tmm import coh_tmm

from thinfilm.optics import multilayer


def test_single_interface_fresnel_and_normal_polarization():
    result = multilayer([400, 550, 800], [1, 1.5], [])
    assert_allclose(result.R, 0.04, atol=1e-14)
    assert_allclose(result.T_s, 0.96, atol=1e-14)
    assert_allclose(result.r_p, -result.r_s, atol=1e-14)
    assert_allclose(result.A, 0, atol=1e-14)


def test_zero_thickness_equivalence():
    wavelength = np.linspace(400, 800, 51)
    base = multilayer(wavelength, [1, 1.7, 3.8 + 0.04j], [123], 63)
    extra = multilayer(wavelength, [1, 2.4 + 0.5j, 1.7, 3.8 + 0.04j], [0, 123], 63)
    assert_allclose(extra.r_s, base.r_s, atol=1e-14)
    assert_allclose(extra.r_p, base.r_p, atol=1e-14)
    assert_allclose(extra.T_p, base.T_p, atol=1e-14)


def test_quarter_wave_antireflection():
    result = multilayer([600], [1, np.sqrt(1.5), 1.5], [600 / (4 * np.sqrt(1.5))])
    assert result.R[0] < 1e-28
    assert_allclose(result.T_s, 1, atol=1e-14)
    with pytest.raises(ValueError, match="undefined"):
        result.ellipsometry()


def test_lossless_energy_balance_and_passive_absorption():
    wavelength = np.linspace(400, 900, 121)
    for angle in (0, 45, 80):
        result = multilayer(wavelength, [1, 2.1, 1.46, 1.52], [87, 260], angle)
        assert_allclose(result.R_s + result.T_s, 1, atol=2e-14)
        assert_allclose(result.R_p + result.T_p, 1, atol=2e-14)
        lossy = multilayer(wavelength, [1, 2.1 + 0.3j, 1.46, 3.6 + 0.05j], [87, 260], angle)
        assert np.all(lossy.A >= 0)
        assert np.all(lossy.A <= 1)


def test_total_internal_reflection_and_brewster_limit():
    result = multilayer([500, 700], [1.5, 1], [], 60)
    assert_allclose(result.R, 1, atol=1e-14)
    assert_allclose(result.T_p, 0, atol=1e-14)
    brewster = multilayer([550], [1, 1.5], [], np.rad2deg(np.arctan(1.5)))
    assert brewster.R_p[0] < 1e-28


def test_opaque_film_remains_finite():
    result = multilayer([400, 800], [1, 2 + 3j, 1.5], [1e6], 55)
    interface = multilayer([400, 800], [1, 2 + 3j], [], 55)
    assert_allclose(result.R, interface.R, atol=1e-14)
    assert_allclose(result.T_s, 0, atol=1e-300)
    assert np.all(np.isfinite(result.A))


def test_random_stacks_against_independent_transfer_matrix():
    rng = np.random.default_rng(2026)
    for _ in range(30):
        count = int(rng.integers(0, 5))
        indices = [1] + list(
            rng.uniform(1.2, 4, count + 1) + 1j * rng.uniform(0, 0.4, count + 1)
        )
        thickness = rng.uniform(1, 400, count)
        wavelength = float(rng.uniform(400, 900))
        angle = float(rng.uniform(0, 80))
        actual = multilayer([wavelength], indices, thickness, angle)
        for pol in ("s", "p"):
            expected = coh_tmm(
                pol, indices, [np.inf, *thickness, np.inf], np.deg2rad(angle), wavelength
            )
            for name in ("r", "t", "R", "T"):
                assert_allclose(
                    getattr(actual, f"{name}_{pol}"), expected[name], atol=2e-12, rtol=2e-12
                )


@pytest.mark.parametrize(
    "wavelength,indices,thickness,angle",
    [
        ([], [1, 1.5], [], 0),
        ([0], [1, 1.5], [], 0),
        ([500], [1, 2, 1.5], [-1], 0),
        ([500], [1, 2], [100], 0),
        ([500], [1, 2 - 0.1j], [], 0),
        ([500], [1 + 0.1j, 2], [], 0),
        ([500], [1, 2], [], 90),
        ([500], [1, [1.5, 1.6]], [], 0),
    ],
)
def test_invalid_physical_inputs(wavelength, indices, thickness, angle):
    with pytest.raises(ValueError):
        multilayer(wavelength, indices, thickness, angle)
