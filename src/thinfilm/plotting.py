"""Scientific figures generated only from the archived case-study reports/tables."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _table(directory, name):
    return np.genfromtxt(directory / name, delimiter=",", names=True)


def _save(figure, directory, name, caption):
    figure.text(0.02, 0.015, caption, fontsize=9, va="bottom")
    figure.tight_layout(rect=(0, 0.105, 1, 0.95))
    figure.savefig(directory / name, dpi=180, facecolor="white")
    plt.close(figure)


def make_figures(output_dir, report):
    """Generate four publication-style PNG figures with data categories in captions."""
    directory = Path(output_dir)
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "lines.linewidth": 1.5,
        }
    )
    data = _table(directory, "measured_fit.csv")
    figure, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    wavelength = data["wavelength_nm"]
    delta_fit = data["delta_fit_source_deg"].copy()
    delta_fit[1:][np.abs(np.diff(delta_fit)) > 180] = np.nan
    for ax, measured, prediction, label in [
        (axes[0, 0], data["psi_measured_deg"], data["psi_fit_deg"], r"$\Psi$ (deg)"),
        (axes[0, 1], data["delta_raw_deg"], delta_fit, r"$\Delta$, source convention (deg)"),
    ]:
        ax.scatter(
            wavelength, measured, s=5, color="#375a7f", alpha=0.5, label="Measured (926 points)"
        )
        ax.plot(wavelength, prediction, color="#dc661f", label="Two-thickness fit")
        ax.set_ylabel(label)
        ax.legend(fontsize=8)
    for ax, key, label in [
        (axes[1, 0], "psi_residual_deg", r"$\Psi$ residual (deg)"),
        (axes[1, 1], "delta_residual_source_deg", r"$\Delta$ residual (deg)"),
    ]:
        ax.plot(wavelength, data[key], color="#375a7f")
        ax.axhline(0, color="black", lw=0.8)
        ax.set(xlabel="Wavelength (nm)", ylabel=label)
    pair = report["measured"]["two_thickness"]["thickness_nm"]
    figure.suptitle(
        f"Measured ALD TiO₂ / SiO₂ / Si: conditional fit at 70.06°\n"
        f"d(TiO₂) = {pair[0]:.3f} nm; d(SiO₂) = {pair[1]:.3f} nm"
    )
    _save(
        figure,
        directory,
        "measured_fit.png",
        "Raw data: pyElli Sentech example; fixed Cauchy films and Aspnes Si reference.\n"
        "Residuals = fit − measurement (wrapped Δ). Structure limits uncertainty claims.\n"
        "Dispersion used the same spectra: conditional reanalysis, not thickness truth.",
    )

    scan = _table(directory, "ambiguity_scan.csv")
    broad = _table(directory, "synthetic_broad.csv")
    figure, axes = plt.subplots(1, 2, figsize=(11, 5.4))
    for key, label, color in [
        ("narrow_delta_chi2", "599–601 nm", "#dc661f"),
        ("broad_delta_chi2", "420–780 nm", "#375a7f"),
    ]:
        axes[0].semilogy(
            scan["thickness_nm"], np.maximum(scan[key], 0) + 1, label=label, color=color
        )
        case = report["synthetic"]["narrow" if key.startswith("narrow") else "broad"]
        axes[0].scatter(
            [item[0][0] for item in case["candidates"]],
            [1 + item[1] - case["objective"] for item in case["candidates"]],
            color=color,
            s=18,
            zorder=4,
        )
    axes[0].axvline(137, color="black", ls=":", label="Known truth: 137 nm")
    axes[0].set(
        xlabel="Trial film thickness (nm)",
        ylabel=r"$1 + Q(d) - Q_{min}$",
        title="Spectral information separates interference orders",
    )
    axes[0].legend(fontsize=8)
    axes[1].scatter(
        broad["wavelength_nm"],
        broad["observed_R"],
        s=12,
        label="Synthetic noisy observations",
        color="#375a7f",
    )
    axes[1].plot(
        broad["wavelength_nm"], broad["fitted_R"], color="#dc661f", label="Fitted model"
    )
    axes[1].set(
        xlabel="Wavelength (nm)",
        ylabel="Reflectance (fraction)",
        title="Broad-band thickness recovery",
    )
    axes[1].legend(fontsize=8)
    _save(
        figure,
        directory,
        "identifiability.png",
        "Synthetic air / n=1.8 film / n=1.5 substrate; 0° incidence; 90 points per window.\n"
        f"Same Gaussian noise, σ(R)=0.002, seed={report['synthetic']['seed']}; fixed indices.\n"
        "Lines: uniform scan; dots: refined minima. Local errors exclude separated solutions.",
    )

    spectra = _table(directory, "design_spectra.csv")
    samples = _table(directory, "tolerance_samples.csv")
    figure, axes = plt.subplots(1, 2, figsize=(11, 5.4))
    for key, label, style in [
        ("bare_R", "Bare Si, 0°", "--"),
        ("design_R", "Designed film, 0°", "-"),
        ("design_R_s_55deg", "Designed film, s at 55°", ":"),
        ("design_R_p_55deg", "Designed film, p at 55°", "-."),
    ]:
        axes[0].plot(spectra["wavelength_nm"], 100 * spectra[key], style, label=label)
    axes[0].set(
        xlabel="Wavelength (nm)", ylabel="Reflectance (%)", title="Reference-material AR design"
    )
    axes[0].legend(fontsize=8)
    axes[1].hist(100 * samples["mean_R"], bins=40, color="#375a7f", alpha=0.85)
    axes[1].axvline(
        100 * report["tolerance"]["mean_R"], color="#dc661f", label="Nominal optimum"
    )
    axes[1].set(
        xlabel="Band-average reflectance (%)",
        ylabel="Monte Carlo count",
        title="Assumed thickness variation at 0°",
    )
    axes[1].legend(fontsize=8)
    _save(
        figure,
        directory,
        "tolerance_design.png",
        "TiO₂-like Cauchy film on Aspnes Si; uniform-per-nm objective over 450–750 nm.\n"
        f"Nominal {report['tolerance']['optimum_nm']:.3f} nm; assumed normal σ(d)=2 nm; "
        f"{report['tolerance']['samples']} samples; seed={report['tolerance']['seed']}.\n"
        "Assumed process variation, not measured yield. Optical constants remain fixed.",
    )

    sensitivity = report["measured"]["sensitivity"]
    baseline = sensitivity[0]["TiO2_nm"]
    figure, ax = plt.subplots(figsize=(10, 5.8))
    ax.barh(
        [v["scenario"].replace("_", " ") for v in sensitivity[1:]],
        [v["TiO2_nm"] - baseline for v in sensitivity[1:]],
        color="#375a7f",
    )
    ax.axvline(0, color="black", lw=0.8)
    ax.set(
        xlabel="Change in fitted TiO₂ thickness (nm)",
        title="Sensitivity to fixed-model assumptions",
    )
    _save(
        figure,
        directory,
        "model_sensitivity.png",
        "Measured spectra unchanged; each row refits one thickness after the perturbation.\n"
        "Perturbations are exploratory assumptions, not calibrated uncertainty distributions.\n"
        "Oxide fixed here; the two-free-layer fit separately exposes strong correlation.",
    )
