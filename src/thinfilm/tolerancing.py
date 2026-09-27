"""Single-coating design and propagation of explicitly assumed thickness variation."""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import trapezoid
from scipy.optimize import minimize_scalar

from .optics import multilayer


def band_average(wavelength_nm, reflectance):
    """Uniform-per-nm spectral average of dimensionless reflectance by trapezoidal rule."""
    wavelength = np.asarray(wavelength_nm, dtype=float)
    values = np.asarray(reflectance, dtype=float)
    if (
        wavelength.ndim != 1
        or len(wavelength) < 2
        or values.shape != wavelength.shape
        or np.any(~np.isfinite(wavelength))
        or np.any(np.diff(wavelength) <= 0)
        or np.any(wavelength <= 0)
        or np.any(~np.isfinite(values))
    ):
        raise ValueError("Supply matching finite spectra on an increasing positive nm axis.")
    return float(trapezoid(values, wavelength) / (wavelength[-1] - wavelength[0]))


@dataclass(frozen=True)
class DesignResult:
    thickness_nm: float
    mean_reflectance: float
    grid_nm: np.ndarray
    grid_objective: np.ndarray


def design_single_layer(wavelength_nm, indices, bounds_nm, *, angle_deg=0.0, grid_size=301):
    """Search grid-resolved minima plus endpoints; refine every bracketed local minimum.

    Not a proof of global optimality: compare grid sizes and spectral quadrature
    to verify resolution. Only one finite coating is accepted.
    """
    bounds = np.asarray(bounds_nm, dtype=float)
    if (
        bounds.shape != (2,)
        or np.any(~np.isfinite(bounds))
        or not 0 <= bounds[0] < bounds[1]
        or len(indices) != 3
    ):
        raise ValueError(
            "One film and finite increasing nonnegative thickness bounds required."
        )
    if not isinstance(grid_size, int) or grid_size < 5:
        raise ValueError("grid_size must be an integer >= 5.")

    def objective(thickness_nm):
        return band_average(
            wavelength_nm, multilayer(wavelength_nm, indices, [thickness_nm], angle_deg).R
        )

    grid = np.linspace(*bounds, grid_size)
    scores = np.array([objective(value) for value in grid])
    candidates = [(grid[0], scores[0]), (grid[-1], scores[-1])]
    for i in range(1, grid_size - 1):
        if scores[i] <= scores[i - 1] and scores[i] <= scores[i + 1]:
            result = minimize_scalar(
                objective,
                bounds=(grid[i - 1], grid[i + 1]),
                method="bounded",
                options={"xatol": 1e-9},
            )
            if not result.success:
                raise RuntimeError("Thickness refinement failed.")
            candidates.append((float(result.x), float(result.fun)))
    thickness, mean = min(candidates, key=lambda pair: pair[1])
    return DesignResult(thickness, mean, grid, scores)


def tolerance_samples(
    wavelength_nm, indices, mean_nm, sigma_nm, *, samples=2000, seed=2026, angle_deg=0.0
):
    """Propagate a normal distribution conditioned on nonnegative thickness.

    Returns thicknesses, band-average R, and the rejected-negative count. The
    requested mean/std describe the untruncated parent; they are not measured
    process parameters. No performance threshold or experimental yield is inferred.
    """
    if (
        not np.all(np.isfinite([mean_nm, sigma_nm]))
        or mean_nm < 0
        or sigma_nm < 0
        or not isinstance(samples, int)
        or samples < 2
        or len(indices) != 3
    ):
        raise ValueError("One film, nonnegative finite mean/std, and >=2 samples required.")
    rng = np.random.default_rng(seed)
    thickness = rng.normal(mean_nm, sigma_nm, samples)
    rejected = 0
    for _ in range(100):
        mask = thickness < 0
        if not np.any(mask):
            break
        rejected += int(np.sum(mask))
        thickness[mask] = rng.normal(mean_nm, sigma_nm, np.sum(mask))
    else:
        raise RuntimeError("Truncated-normal sampling failed to produce positive thicknesses.")
    values = np.array(
        [
            band_average(
                wavelength_nm, multilayer(wavelength_nm, indices, [value], angle_deg).R
            )
            for value in thickness
        ]
    )
    return thickness, values, rejected
