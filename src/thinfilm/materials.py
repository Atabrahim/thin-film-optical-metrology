"""Transparent dispersion inputs; no extrapolation of tabulated references."""

from pathlib import Path

import numpy as np


def cauchy_index(wavelength_nm, a, b_nm2=0.0, c_nm4=0.0):
    """Lossless empirical n = a + b/lambda^2 + c/lambda^4; lambda in nm.

    Coefficients have units 1, nm^2, nm^4. A transparent-window approximation,
    not a model of absorption edges. Coefficients are supplied explicitly.
    """
    wavelength = np.asarray(wavelength_nm, dtype=float)
    if np.any(~np.isfinite(wavelength)) or np.any(wavelength <= 0):
        raise ValueError("Wavelength must be finite and positive.")
    if not np.all(np.isfinite([a, b_nm2, c_nm4])):
        raise ValueError("Cauchy coefficients must be finite.")
    index = a + b_nm2 / wavelength**2 + c_nm4 / wavelength**4
    if np.any(~np.isfinite(index)) or np.any(index <= 0):
        raise ValueError("Cauchy coefficients produce a nonfinite or nonpositive index.")
    return index


def tabulated_index(wavelength_nm, reference_nm, reference_n, reference_k):
    """Linearly interpolate n and k without extrapolating reference data."""
    wavelength, axis, n, k = [
        np.asarray(a, dtype=float)
        for a in (wavelength_nm, reference_nm, reference_n, reference_k)
    ]
    if axis.ndim != 1 or axis.size < 2 or n.shape != axis.shape or k.shape != axis.shape:
        raise ValueError("Reference wavelength/n/k must be matching one-dimensional arrays.")
    if (
        np.any(~np.isfinite(axis))
        or np.any(np.diff(axis) <= 0)
        or axis[0] <= 0
        or np.any(~np.isfinite(n))
        or np.any(~np.isfinite(k))
        or np.any(n <= 0)
        or np.any(k < 0)
    ):
        raise ValueError("Reference indices must be finite/passive with an increasing axis.")
    if (
        np.any(~np.isfinite(wavelength))
        or np.any(wavelength < axis[0])
        or np.any(wavelength > axis[-1])
    ):
        raise ValueError("Requested wavelengths lie outside the reference range.")
    return np.interp(wavelength, axis, n) + 1j * np.interp(wavelength, axis, k)


def read_rii_table(path):
    """Read the numeric block of the pinned single-block Aspnes nk YAML file.

    This intentionally narrow reader does not claim to parse arbitrary RII YAML.
    Converts the source wavelength in micrometres to nm.
    """
    text = Path(path).read_text(encoding="utf-8")
    if text.count("type: tabulated nk") != 1 or text.count("data: |") != 1:
        raise ValueError("Expected one tabulated nk block.")
    lines = text.split("data: |", 1)[1].splitlines()
    rows = [[float(value) for value in line.split()] for line in lines if line.strip()]
    table = np.asarray(rows)
    if table.ndim != 2 or table.shape[1] != 3:
        raise ValueError("Expected wavelength_um, n, k columns.")
    table[:, 0] *= 1000
    tabulated_index(table[:, 0], *table.T)
    return table
