"""Thickness inference with explicit observation errors and ambiguity diagnostics."""

from dataclasses import dataclass
from itertools import product

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import chi2

from .optics import multilayer


def phase_difference_deg(model_deg, observed_deg):
    """Shortest signed model-minus-observation phase difference in [-180,180)."""
    return (np.asarray(model_deg) - np.asarray(observed_deg) + 180) % 360 - 180


def observable(wavelength_nm, indices, thickness_nm, angle_deg, kind):
    """Return unpolarized reflectance or columns Psi/Delta in degrees."""
    spectrum = multilayer(wavelength_nm, indices, thickness_nm, angle_deg)
    if kind == "reflectance":
        return spectrum.R
    if kind == "ellipsometry":
        return np.column_stack(spectrum.ellipsometry())
    raise ValueError("kind must be reflectance or ellipsometry.")


@dataclass(frozen=True)
class FitResult:
    """Conditional inference result; covariance is not a model-accuracy claim."""

    thickness_nm: np.ndarray
    variable_layers: tuple
    predicted: np.ndarray
    residual: np.ndarray
    objective: float
    degrees_of_freedom: int
    covariance_nm2: np.ndarray | None
    correlation: np.ndarray | None
    flags: tuple
    candidates: tuple
    absolute_sigma: bool
    jacobian_condition: float

    @property
    def standard_errors_nm(self):
        return None if self.covariance_nm2 is None else np.sqrt(np.diag(self.covariance_nm2))


def fit_thickness(
    wavelength_nm,
    indices,
    thickness_nm,
    variable_layers,
    bounds_nm,
    observed,
    *,
    angle_deg=0.0,
    kind="reflectance",
    sigma=1.0,
    absolute_sigma=False,
    starts_per_axis=5,
):
    """Fit one or two film thicknesses, holding optical constants fixed.

    Residuals are model minus observation, with wrapped Delta for ellipsometry.
    sigma is in reflectance-fraction units or degrees and must be positive.
    If absolute_sigma=True, supplied sigma is treated as known independent
    Gaussian observation error. Otherwise it specifies relative weights and
    covariance is rescaled by residual sum of squares / degrees of freedom.
    A deterministic Cartesian grid of starts searches for local minima; it
    does not guarantee a global solution. Active bounds/rank failure suppress
    misleading local standard errors. Other model uncertainties are excluded.
    """
    thickness = np.array(thickness_nm, dtype=float, copy=True)
    variables = tuple(variable_layers)
    if (
        len(variables) not in (1, 2)
        or len(set(variables)) != len(variables)
        or any(
            not isinstance(i, (int, np.integer)) or not 0 <= i < len(thickness)
            for i in variables
        )
    ):
        raise ValueError("Select one or two distinct valid finite-layer indices.")
    bounds = np.asarray(bounds_nm, dtype=float)
    if (
        bounds.shape != (len(variables), 2)
        or np.any(~np.isfinite(bounds))
        or np.any(bounds[:, 0] < 0)
        or np.any(bounds[:, 1] <= bounds[:, 0])
    ):
        raise ValueError(
            "bounds_nm must contain a finite nonnegative [lower,upper] per variable."
        )
    if not isinstance(starts_per_axis, int) or not 2 <= starts_per_axis <= 20:
        raise ValueError("starts_per_axis must be an integer from 2 through 20.")
    initial_prediction = observable(wavelength_nm, indices, thickness, angle_deg, kind)
    measured = np.asarray(observed, dtype=float)
    if measured.shape != initial_prediction.shape or np.any(~np.isfinite(measured)):
        raise ValueError("Observed values must be finite and match the model output shape.")
    if kind == "ellipsometry" and np.any((measured[:, 0] < 0) | (measured[:, 0] > 90)):
        raise ValueError("Measured Psi must lie in [0,90] degrees.")
    try:
        uncertainty = np.broadcast_to(np.asarray(sigma, dtype=float), measured.shape)
    except ValueError as exc:
        raise ValueError("sigma must be scalar or broadcast to the observations.") from exc
    if np.any(~np.isfinite(uncertainty)) or np.any(uncertainty <= 0):
        raise ValueError("sigma must be finite and positive.")
    dof = measured.size - len(variables)
    if dof <= 0:
        raise ValueError("More observations than fitted parameters are required.")

    def predict(parameters):
        trial = thickness.copy()
        trial[list(variables)] = parameters
        return observable(wavelength_nm, indices, trial, angle_deg, kind)

    def residual(parameters):
        difference = predict(parameters) - measured
        if kind == "ellipsometry":
            difference[:, 1] = phase_difference_deg(difference[:, 1], 0)
        return (difference / uncertainty).ravel()

    lower, upper = bounds.T
    starts = product(*[np.linspace(lo, hi, starts_per_axis + 2)[1:-1] for lo, hi in bounds])
    solutions = []
    for start in starts:
        solution = least_squares(
            residual,
            start,
            bounds=(lower, upper),
            jac="3-point",
            x_scale="jac",
            ftol=1e-11,
            xtol=1e-11,
            gtol=1e-11,
            max_nfev=800,
        )
        if solution.success and np.all(np.isfinite(solution.fun)):
            solutions.append(solution)
    if not solutions:
        raise RuntimeError("No multistart fit converged; inspect bounds and optical model.")
    solutions.sort(key=lambda s: float(s.fun @ s.fun))
    best = solutions[0]
    objective = float(best.fun @ best.fun)
    candidates = []
    for solution in solutions:
        if not any(
            np.allclose(solution.x, item[0], atol=1e-3, rtol=1e-5) for item in candidates
        ):
            candidates.append((solution.x.copy(), float(solution.fun @ solution.fun)))
    flags = []
    if kind == "reflectance" and np.any((measured < 0) | (measured > 1)):
        flags.append("observations_outside_physical_range")
    if len(solutions) < starts_per_axis ** len(variables):
        flags.append("some_starts_failed")
    if np.any(np.minimum(best.x - lower, upper - best.x) < 1e-5 * (upper - lower)):
        flags.append("active_bound")
    _, singular, vt = np.linalg.svd(best.jac, full_matrices=False)
    condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else np.inf
    # Conservative numerical rank: finite-difference noise must not manufacture
    # information about physically indistinguishable layers.
    if singular[-1] <= singular[0] * 1e-7 or singular[0] == 0:
        flags.append("rank_deficient")
    covariance = correlation = None
    if "active_bound" not in flags and "rank_deficient" not in flags:
        scale = 1.0 if absolute_sigma else objective / dof
        covariance = (vt.T / singular**2) @ vt * scale
        errors = np.sqrt(np.diag(covariance))
        if np.all(errors > 0):
            correlation = covariance / np.outer(errors, errors)
    allowance = (
        chi2.ppf(0.95, len(variables)) if absolute_sigma else max(objective * 0.05, 1e-12)
    )
    if any(cost <= objective + allowance for _, cost in candidates[1:]):
        flags.append("competing_minima")
    fitted = thickness.copy()
    fitted[list(variables)] = best.x
    raw_residual = best.fun.reshape(measured.shape) * uncertainty
    channels = raw_residual.reshape(len(raw_residual), -1)
    for channel in channels.T:
        if len(channel) > 4 and np.std(channel) > 1e-12:
            if abs(np.corrcoef(channel[:-1], channel[1:])[0, 1]) > 0.3:
                flags.append("correlated_residuals")
                break
    return FitResult(
        fitted,
        variables,
        predict(best.x),
        raw_residual,
        objective,
        dof,
        covariance,
        correlation,
        tuple(flags),
        tuple(candidates),
        bool(absolute_sigma),
        condition,
    )


def thickness_scan(
    wavelength_nm,
    indices,
    thickness_nm,
    layer,
    grid_nm,
    observed,
    *,
    angle_deg=0.0,
    kind="reflectance",
    sigma=1.0,
):
    """Conditional objective scan with all other parameters fixed.

    Not a nuisance-profile confidence interval for a multi-parameter fit.
    Used to expose interference orders and ambiguity in the one-thickness case.
    """
    grid = np.asarray(grid_nm, dtype=float)
    if grid.ndim != 1 or not grid.size or np.any(~np.isfinite(grid)) or np.any(grid < 0):
        raise ValueError("grid_nm must be a finite nonnegative vector.")
    if not isinstance(layer, (int, np.integer)) or not 0 <= layer < len(thickness_nm):
        raise ValueError("Invalid layer index.")
    measured = np.asarray(observed, dtype=float)
    prediction = observable(wavelength_nm, indices, thickness_nm, angle_deg, kind)
    if measured.shape != prediction.shape or np.any(~np.isfinite(measured)):
        raise ValueError("Observed values must be finite and match model output shape.")
    uncertainty = np.broadcast_to(np.asarray(sigma, dtype=float), measured.shape)
    if np.any(~np.isfinite(uncertainty)) or np.any(uncertainty <= 0):
        raise ValueError("sigma must be finite and positive.")
    scores = []
    for value in grid:
        trial = np.array(thickness_nm, dtype=float, copy=True)
        trial[layer] = value
        difference = observable(wavelength_nm, indices, trial, angle_deg, kind) - measured
        if kind == "ellipsometry":
            difference[:, 1] = phase_difference_deg(difference[:, 1], 0)
        scores.append(float(np.sum((difference / uncertainty) ** 2)))
    return np.asarray(scores)
