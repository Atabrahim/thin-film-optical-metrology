"""Thickness recovery from independent Airy and tmm observations, plus failure cases."""

import numpy as np
import pytest
from tmm import coh_tmm

from thinfilm.inference import fit_thickness, phase_difference_deg, thickness_scan


def airy(wavelength_nm, thickness_nm, n=1.8, substrate=1.5):
    """Independent normal-incidence single-film intensity formula (real indices)."""
    r01 = (1 - n) / (1 + n)
    r12 = (n - substrate) / (n + substrate)
    cosine = np.cos(4 * np.pi * n * thickness_nm / wavelength_nm)
    return (r01**2 + r12**2 + 2 * r01 * r12 * cosine) / (
        1 + (r01 * r12) ** 2 + 2 * r01 * r12 * cosine
    )


def test_single_thickness_and_covariance_against_independent_derivative():
    wavelength = np.linspace(420, 780, 90)
    truth = 137.0
    sigma = 0.002
    measured = airy(wavelength, truth)
    fit = fit_thickness(
        wavelength,
        [1, 1.8, 1.5],
        [100],
        [0],
        [[20, 250]],
        measured,
        sigma=sigma,
        absolute_sigma=True,
    )
    assert abs(fit.thickness_nm[0] - truth) < 1e-6
    derivative = (airy(wavelength, truth + 0.001) - airy(wavelength, truth - 0.001)) / 0.002
    expected_variance = 1 / np.sum((derivative / sigma) ** 2)
    np.testing.assert_allclose(fit.covariance_nm2[0, 0], expected_variance, rtol=2e-5)
    doubled = fit_thickness(
        wavelength,
        [1, 1.8, 1.5],
        [100],
        [0],
        [[20, 250]],
        measured,
        sigma=2 * sigma,
        absolute_sigma=True,
    )
    np.testing.assert_allclose(
        doubled.standard_errors_nm, 2 * fit.standard_errors_nm, rtol=2e-5
    )


def test_two_thickness_ellipsometry_recovery_from_tmm():
    wavelength = np.linspace(420, 790, 65)
    indices = [1, 2.25, 1.46, 3.8 + 0.025j]
    truth = [27.0, 276.0]
    ratio = []
    for value in wavelength:
        args = (indices, [np.inf, *truth, np.inf], np.deg2rad(70.06), value)
        ratio.append(coh_tmm("p", *args)["r"] / coh_tmm("s", *args)["r"])
    ratio = np.array(ratio)
    measured = np.column_stack(
        [np.rad2deg(np.arctan(abs(ratio))), np.rad2deg(np.angle(ratio)) % 360]
    )
    fit = fit_thickness(
        wavelength,
        indices,
        [20, 250],
        [0, 1],
        [[5, 60], [220, 340]],
        measured,
        kind="ellipsometry",
        angle_deg=70.06,
        sigma=0.05,
        absolute_sigma=True,
        starts_per_axis=3,
    )
    np.testing.assert_allclose(fit.thickness_nm, truth, atol=1e-6)
    assert fit.objective < 1e-12
    assert np.all(np.linalg.eigvalsh(fit.covariance_nm2) > 0)
    assert fit.correlation.shape == (2, 2)


def test_noise_recovery_is_statistical_not_optimizer_precision():
    wavelength = np.linspace(420, 780, 90)
    sigma = 0.002
    measured = airy(wavelength, 137) + np.random.default_rng(42).normal(0, sigma, 90)
    fit = fit_thickness(
        wavelength,
        [1, 1.8, 1.5],
        [100],
        [0],
        [[20, 250]],
        measured,
        sigma=sigma,
        absolute_sigma=True,
    )
    assert abs(fit.thickness_nm[0] - 137) < 3 * fit.standard_errors_nm[0]
    assert 0.5 < fit.objective / fit.degrees_of_freedom < 1.5


def test_identical_adjacent_films_are_not_separately_identifiable():
    wavelength = np.linspace(420, 780, 50)
    fit = fit_thickness(
        wavelength,
        [1, 1.8, 1.8, 1.5],
        [50, 80],
        [0, 1],
        [[10, 150], [10, 150]],
        airy(wavelength, 137),
        sigma=0.002,
        absolute_sigma=True,
        starts_per_axis=3,
    )
    assert "rank_deficient" in fit.flags
    assert fit.covariance_nm2 is None
    assert abs(sum(fit.thickness_nm) - 137) < 1e-5


def test_active_bound_suppresses_unconstrained_standard_errors():
    wavelength = np.linspace(420, 780, 40)
    fit = fit_thickness(
        wavelength,
        [1, 1.8, 1.5],
        [120],
        [0],
        [[100, 130]],
        airy(wavelength, 137),
        starts_per_axis=3,
    )
    assert "active_bound" in fit.flags
    assert fit.standard_errors_nm is None


def test_single_colour_has_competing_interference_orders():
    wavelength = np.full(8, 600.0)
    measured = airy(wavelength, 137)
    fit = fit_thickness(
        wavelength,
        [1, 1.8, 1.5],
        [100],
        [0],
        [[20, 700]],
        measured,
        sigma=0.002,
        absolute_sigma=True,
        starts_per_axis=15,
    )
    assert "competing_minima" in fit.flags
    assert sum(cost < 1e-9 for _, cost in fit.candidates) >= 3
    scores = thickness_scan(
        wavelength, [1, 1.8, 1.5], [100], 0, [137, 137 + 600 / (2 * 1.8)], measured
    )
    np.testing.assert_allclose(scores, 0, atol=1e-25)


def test_phase_wrapping_and_invalid_uncertainty():
    np.testing.assert_allclose(phase_difference_deg([1, 359, -179], [359, 1, 179]), [2, -2, 2])
    with pytest.raises(ValueError, match="sigma"):
        fit_thickness([500, 600], [1, 1.8, 1.5], [100], [0], [[20, 200]], [0.1, 0.2], sigma=0)
