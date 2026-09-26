"""Coherent isotropic multilayer optics, using a stable amplitude recursion.

Convention: exp(-i omega t), passive index n + i k with k >= 0, forward
exp(+i k_z z). The p polarization follows the Fresnel electric-field convention
of Byrnes (2016), so r_p = -r_s at normal incidence. All lengths use nm.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class OpticalResult:
    """Complex field amplitudes and dimensionless power fractions."""

    wavelength_nm: NDArray[np.float64]
    r_s: NDArray[np.complex128]
    r_p: NDArray[np.complex128]
    t_s: NDArray[np.complex128]
    t_p: NDArray[np.complex128]
    R_s: NDArray[np.float64]
    R_p: NDArray[np.float64]
    T_s: NDArray[np.float64]
    T_p: NDArray[np.float64]

    @property
    def R(self):
        """Unpolarized reflected fraction, equal s/p incident powers."""
        return (self.R_s + self.R_p) / 2

    @property
    def A(self):
        """Absorption in finite films; excludes absorption inside the substrate."""
        return 1 - self.R - (self.T_s + self.T_p) / 2

    def ellipsometry(self):
        """Return Psi in [0,90] and Delta in (-180,180] degrees, rho = r_p/r_s.

        Delta is undefined when either reflected polarization vanishes. Do not
        silently assign a phase to an unobservable quantity.
        """
        if np.any(np.abs(self.r_s) < 1e-14) or np.any(np.abs(self.r_p) < 1e-14):
            raise ValueError("Ellipsometric phase is undefined at zero reflection.")
        rho = self.r_p / self.r_s
        return np.rad2deg(np.arctan(np.abs(rho))), np.rad2deg(np.angle(rho))


def multilayer(
    wavelength_nm: ArrayLike,
    indices: list | tuple,
    thickness_nm: ArrayLike,
    angle_deg: float = 0.0,
) -> OpticalResult:
    """Solve one planar stack at a real ambient angle and many wavelengths.

    ``indices`` contains ambient, film(s), substrate; entries can be complex
    scalars or one index per wavelength. ``thickness_nm`` contains only finite
    film thicknesses. Ambient and substrate are semi-infinite. Indices must
    have positive real part and nonnegative imaginary part. Ambient is real.
    No roughness, anisotropy, gain, incoherence, or backside reflection.

    The recursion sums internal reflections without exponentially growing
    propagation factors. T is power entering the substrate, even if absorbing.
    Exact internal critical incidence (k_z = 0) is excluded as a singular limit.
    """
    wavelength = np.asarray(wavelength_nm, dtype=float)
    thickness = np.asarray(thickness_nm, dtype=float)
    if wavelength.ndim != 1 or not wavelength.size:
        raise ValueError("wavelength_nm must be a nonempty one-dimensional array.")
    if np.any(~np.isfinite(wavelength)) or np.any(wavelength <= 0):
        raise ValueError("Wavelengths must be finite and positive, in nm.")
    if thickness.ndim != 1 or np.any(~np.isfinite(thickness)) or np.any(thickness < 0):
        raise ValueError("Film thicknesses must be finite, nonnegative and one-dimensional.")
    if len(indices) != thickness.size + 2:
        raise ValueError("Supply ambient, each finite film, and substrate indices.")
    if not np.isfinite(angle_deg) or not 0 <= angle_deg < 90:
        raise ValueError("Ambient angle_deg must satisfy 0 <= angle_deg < 90.")
    try:
        index = np.stack(
            [np.broadcast_to(np.asarray(n, dtype=complex), wavelength.shape) for n in indices]
        )
    except ValueError as exc:
        raise ValueError("Each index must be scalar or match wavelength_nm.") from exc
    if np.any(~np.isfinite(index)) or np.any(index.real <= 0) or np.any(index.imag < 0):
        raise ValueError("Indices must be finite, passive n + i k with n > 0 and k >= 0.")
    if np.any(index[0].imag != 0):
        raise ValueError("The ambient must be non-absorbing.")

    tangential_index = index[0].real * np.sin(np.deg2rad(angle_deg))
    normal_index = np.sqrt(index**2 - tangential_index**2 + 0j)
    # For passive positive-real indices the principal root decays into the stack.
    if np.any(np.abs(normal_index) < 1e-12):
        raise ValueError("Exact critical incidence is excluded; use a nearby angle.")
    amplitudes = []
    for polarization in ("s", "p"):
        left, right = normal_index[:-1], normal_index[1:]
        if polarization == "s":
            denominator = left + right
            interface_r = (left - right) / denominator
            interface_t = 2 * left / denominator
        else:
            left_weight = index[1:] ** 2 * left
            right_weight = index[:-1] ** 2 * right
            denominator = left_weight + right_weight
            interface_r = (left_weight - right_weight) / denominator
            interface_t = 2 * index[:-1] * index[1:] * left / denominator
        reflection, transmission = interface_r[-1].copy(), interface_t[-1].copy()
        for layer in range(thickness.size - 1, -1, -1):
            phase = np.exp(2j * np.pi * normal_index[layer + 1] * thickness[layer] / wavelength)
            denominator = 1 + interface_r[layer] * reflection * phase**2
            transmission = interface_t[layer] * transmission * phase / denominator
            reflection = (interface_r[layer] + reflection * phase**2) / denominator
        amplitudes.extend((reflection, transmission))
    r_s, t_s, r_p, t_p = amplitudes
    incident_flux = normal_index[0].real
    s_flux = normal_index[-1].real / incident_flux
    p_flux = np.real(index[-1] * np.conj(normal_index[-1] / index[-1])) / incident_flux
    return OpticalResult(
        wavelength.copy(),
        r_s,
        r_p,
        t_s,
        t_p,
        np.abs(r_s) ** 2,
        np.abs(r_p) ** 2,
        np.abs(t_s) ** 2 * s_flux,
        np.abs(t_p) ** 2 * p_flux,
    )
