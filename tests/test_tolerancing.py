import numpy as np
import pytest

from thinfilm.tolerancing import band_average, design_single_layer, tolerance_samples


def test_quadrature_constant_and_linear_spectra_on_irregular_grid():
    wavelength = np.array([400, 420, 550, 700, 800])
    assert band_average(wavelength, np.full(5, 0.2)) == pytest.approx(0.2)
    assert band_average(wavelength, wavelength / 1000) == pytest.approx(0.6)


def test_design_recovers_analytical_quarterwave_in_narrow_band():
    wavelength = np.linspace(599.99, 600.01, 15)
    film_index = np.sqrt(1.5)
    result = design_single_layer(wavelength, [1, film_index, 1.5], [50, 200])
    assert result.thickness_nm == pytest.approx(600 / (4 * film_index), abs=1e-5)
    assert result.mean_reflectance < 1e-10


def test_design_grid_and_spectral_convergence():
    coarse = design_single_layer(
        np.linspace(450, 750, 201), [1, 2.2, 3.8 + 0.02j], [20, 180], grid_size=151
    )
    fine = design_single_layer(
        np.linspace(450, 750, 801), [1, 2.2, 3.8 + 0.02j], [20, 180], grid_size=601
    )
    assert abs(coarse.thickness_nm - fine.thickness_nm) < 0.001
    assert abs(coarse.mean_reflectance - fine.mean_reflectance) < 2e-6


def test_tolerance_reproducibility_zero_variance_and_truncation():
    wavelength = np.linspace(450, 750, 31)
    args = (wavelength, [1, 2.2, 3.8 + 0.02j], 65, 2)
    first = tolerance_samples(*args, samples=50, seed=12)
    second = tolerance_samples(*args, samples=50, seed=12)
    np.testing.assert_array_equal(first[0], second[0])
    np.testing.assert_array_equal(first[1], second[1])
    fixed = tolerance_samples(wavelength, args[1], 65, 0, samples=10)
    np.testing.assert_array_equal(fixed[0], np.full(10, 65))
    assert np.ptp(fixed[1]) == 0
    truncated = tolerance_samples(wavelength, args[1], 0, 2, samples=100)
    assert np.all(truncated[0] >= 0)
    assert truncated[2] > 0


def test_invalid_tolerance_and_band_inputs():
    with pytest.raises(ValueError):
        band_average([500, 400], [0.1, 0.2])
    with pytest.raises(ValueError):
        tolerance_samples([400, 500], [1, 2, 3], 50, -1)
