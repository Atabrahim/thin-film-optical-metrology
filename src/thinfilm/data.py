"""Strict import of the selected Sentech SpectraRay Psi/Delta text export."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class EllipsometryData:
    wavelength_nm: np.ndarray
    psi_deg: np.ndarray
    delta_deg: np.ndarray
    angle_deg: float
    original_rows: int
    excluded_outside_window: int


def read_spectraray(path, window_nm=(400.0, 800.0)):
    """Read nm/Psi/Delta columns and angle from the header; do not smooth or trim silently.

    Reject missing/nonfinite/unordered/invalid data. The explicit wavelength
    window limits use of reference optical constants and is reported in counts.
    Preserve measured Delta as supplied (0..360 degrees is valid).
    """
    with Path(path).open(encoding="utf-8") as stream:
        header = stream.readline().split()
    if len(header) != 4 or header[:2] != [";", "WAVELENGTH"]:
        raise ValueError("Unsupported SpectraRay header; expected wavelength and two angles.")
    angle_psi, angle_delta = map(float, header[2:])
    if not 0 < angle_psi < 90 or angle_psi != angle_delta:
        raise ValueError("Psi and Delta must have the same physical incidence angle.")
    table = np.loadtxt(path, skiprows=1, ndmin=2)
    if table.shape[1] != 3 or len(table) < 3 or np.any(~np.isfinite(table)):
        raise ValueError("Expected at least three finite wavelength/Psi/Delta rows.")
    if np.any(np.diff(table[:, 0]) <= 0) or np.any(table[:, 0] <= 0):
        raise ValueError("Wavelengths must be positive and strictly increasing.")
    if np.any((table[:, 1] < 0) | (table[:, 1] > 90)):
        raise ValueError("Psi must lie between 0 and 90 degrees.")
    window = np.asarray(window_nm, dtype=float)
    if window.shape != (2,) or np.any(~np.isfinite(window)) or not 0 < window[0] < window[1]:
        raise ValueError("window_nm must be two increasing positive endpoints.")
    mask = (table[:, 0] >= window[0]) & (table[:, 0] <= window[1])
    if np.count_nonzero(mask) < 3:
        raise ValueError("Too few measurements inside the requested window.")
    selected = table[mask]
    return EllipsometryData(*selected.T, angle_psi, len(table), int(np.sum(~mask)))
