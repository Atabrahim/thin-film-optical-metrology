"""Frozen V1 case studies. Inputs and assumptions are explicit and outputs reproducible."""

import csv
import hashlib
import json
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

import numpy as np

from .data import read_spectraray
from .inference import fit_thickness, observable, thickness_scan
from .materials import cauchy_index, read_rii_table, tabulated_index
from .optics import multilayer
from .tolerancing import band_average, design_single_layer, tolerance_samples


def _plain(value):
    if isinstance(value, np.ndarray):
        return _plain(value.tolist())
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def _fit_report(fit):
    return _plain(
        {
            key: value
            for key, value in asdict(fit).items()
            if key not in ("predicted", "residual")
        }
        | {
            "local_standard_errors_nm": fit.standard_errors_nm,
            "rmse": np.sqrt(np.mean(fit.residual**2, axis=0)),
        }
    )


def _csv(path, columns, values):
    np.savetxt(
        path,
        np.asarray(values),
        delimiter=",",
        header=",".join(columns),
        comments="",
        fmt="%.12g",
    )


def _titania(wavelength_nm, a_offset=0):
    # Original example's empirical coefficients converted to this API's nm units.
    return cauchy_index(wavelength_nm, 2.22973557 + a_offset, 46168.934, 1.89779575e9)


def measured_case(measurement_path, silicon_table, output):
    """Conditional reanalysis; dispersion and covariance are not thickness truth."""
    data = read_spectraray(measurement_path)
    wavelength = data.wavelength_nm
    indices = [
        1,
        _titania(wavelength),
        cauchy_index(wavelength, 1.452, 3600),
        tabulated_index(wavelength, *silicon_table.T),
    ]
    # pyElli's dataset uses rho=tan(Psi)*exp(-i Delta); our API returns +arg(rho).
    # Preserve the raw Delta column and report this explicit convention conversion.
    observations = np.column_stack([data.psi_deg, -data.delta_deg])

    def fit(
        variable_layers, bounds, *, angle=data.angle_deg, stack=None, thickness=(25, 276.36)
    ):
        return fit_thickness(
            wavelength,
            indices if stack is None else stack,
            thickness,
            variable_layers,
            bounds,
            observations,
            angle_deg=angle,
            kind="ellipsometry",
            starts_per_axis=4,
        )

    one = fit([0], [[5, 60]])
    two = fit([0, 1], [[5, 60], [240, 310]])
    sensitivity = []
    for label, angle, offset, oxide in [
        ("baseline", 70.06, 0, 276.36),
        ("source_example_angle", 70, 0, 276.36),
        ("angle_minus_0.1deg", 69.96, 0, 276.36),
        ("angle_plus_0.1deg", 70.16, 0, 276.36),
        ("TiO2_n0_minus_0.01", 70.06, -0.01, 276.36),
        ("TiO2_n0_plus_0.01", 70.06, 0.01, 276.36),
        ("oxide_minus_1nm", 70.06, 0, 275.36),
        ("oxide_plus_1nm", 70.06, 0, 277.36),
    ]:
        stack = [indices[0], _titania(wavelength, offset), *indices[2:]]
        result = fit([0], [[5, 60]], angle=angle, stack=stack, thickness=(25, oxide))
        sensitivity.append(
            {
                "scenario": label,
                "angle_deg": angle,
                "TiO2_n0_offset": offset,
                "oxide_nm": oxide,
                "TiO2_nm": result.thickness_nm[0],
                "objective_deg2": result.objective,
            }
        )
    with (output / "measured_sensitivity.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(sensitivity[0]))
        writer.writeheader()
        writer.writerows(sensitivity)
    _csv(
        output / "measured_fit.csv",
        [
            "wavelength_nm",
            "psi_measured_deg",
            "delta_raw_deg",
            "delta_api_deg",
            "psi_fit_deg",
            "delta_fit_source_deg",
            "psi_residual_deg",
            "delta_residual_source_deg",
        ],
        np.column_stack(
            [
                wavelength,
                data.psi_deg,
                data.delta_deg,
                -data.delta_deg,
                two.predicted[:, 0],
                (-two.predicted[:, 1]) % 360,
                two.residual[:, 0],
                -two.residual[:, 1],
            ]
        ),
    )
    return {
        "category": "measured data; fitted quantities conditional on fixed dispersion",
        "original_rows": data.original_rows,
        "used_rows": len(wavelength),
        "excluded_rows": data.excluded_outside_window,
        "angle_deg": data.angle_deg,
        "delta_conversion": "delta_api_deg = -delta_raw_deg; modulo 360 equivalence",
        "noise_assumption": "equal degree weights; residual-scaled iid covariance",
        "one_thickness": _fit_report(one),
        "two_thickness": _fit_report(two),
        "sensitivity": sensitivity,
        "warning": "Residual correlation invalidates a literal iid precision claim. "
        "TiO2 dispersion was fitted to the same data by the source. No independent truth.",
    }


def synthetic_case(output, seed):
    """Equal-size narrow/broad experiments; known truth and declared Gaussian noise."""
    indices, truth_nm, sigma = [1, 1.8, 1.5], 137.0, 0.002
    grid = np.linspace(20, 700, 1601)
    noise = np.random.default_rng(seed).normal(0, sigma, 90)
    results, scores = {}, []
    for name, endpoints in [("narrow", (599, 601)), ("broad", (420, 780))]:
        wavelength = np.linspace(*endpoints, 90)
        clean = observable(wavelength, indices, [truth_nm], 0, "reflectance")
        measured = clean + noise  # Same noise realization isolates spectral-window effect.
        fit = fit_thickness(
            wavelength,
            indices,
            [100],
            [0],
            [[20, 700]],
            measured,
            sigma=sigma,
            absolute_sigma=True,
            starts_per_axis=15,
        )
        score = thickness_scan(wavelength, indices, [100], 0, grid, measured, sigma=sigma)
        scores.append(score - fit.objective)
        _csv(
            output / f"synthetic_{name}.csv",
            ["wavelength_nm", "noiseless_R", "observed_R", "fitted_R", "residual_R"],
            np.column_stack([wavelength, clean, measured, fit.predicted, fit.residual]),
        )
        results[name] = _fit_report(fit)
    _csv(
        output / "ambiguity_scan.csv",
        ["thickness_nm", "narrow_delta_chi2", "broad_delta_chi2"],
        np.column_stack([grid, *scores]),
    )

    wavelength = np.linspace(420, 790, 65)
    stack = [1, 2.25, 1.46, 3.8 + 0.025j]
    true_pair = [27, 276]
    paired = observable(wavelength, stack, true_pair, 70.06, "ellipsometry")
    paired += np.random.default_rng(seed + 1).normal(0, 0.05, paired.shape)
    two = fit_thickness(
        wavelength,
        stack,
        [20, 250],
        [0, 1],
        [[5, 60], [220, 340]],
        paired,
        kind="ellipsometry",
        angle_deg=70.06,
        sigma=0.05,
        absolute_sigma=True,
        starts_per_axis=4,
    )
    results.update(
        {
            "category": "synthetic observations, no experimental measurements",
            "seed": seed,
            "truth_nm": truth_nm,
            "sigma_R": sigma,
            "two_layer_truth_nm": true_pair,
            "two_layer_sigma_deg": 0.05,
            "two_layer": _fit_report(two),
        }
    )
    return results


def tolerance_case(silicon_table, output, samples, seed):
    """TiO2-like transparent Cauchy coating on reference Si; normal-incidence objective."""
    wavelength = np.linspace(450, 750, 241)
    stack = [1, _titania(wavelength), tabulated_index(wavelength, *silicon_table.T)]
    optimum = design_single_layer(wavelength, stack, [20, 180])
    fine_wavelength = np.linspace(450, 750, 961)
    fine_stack = [
        1,
        _titania(fine_wavelength),
        tabulated_index(fine_wavelength, *silicon_table.T),
    ]
    fine = design_single_layer(fine_wavelength, fine_stack, [20, 180], grid_size=601)
    thickness, performance, rejected = tolerance_samples(
        wavelength, stack, optimum.thickness_nm, 2, samples=samples, seed=seed
    )
    bare = multilayer(wavelength, [1, stack[-1]], []).R
    design = multilayer(wavelength, stack, [optimum.thickness_nm])
    oblique = multilayer(wavelength, stack, [optimum.thickness_nm], 55)
    minus = multilayer(wavelength, stack, [optimum.thickness_nm - 0.1]).R
    plus = multilayer(wavelength, stack, [optimum.thickness_nm + 0.1]).R
    _csv(
        output / "design_spectra.csv",
        [
            "wavelength_nm",
            "bare_R",
            "design_R",
            "design_R_s_55deg",
            "design_R_p_55deg",
            "dR_dd_per_nm",
        ],
        np.column_stack(
            [wavelength, bare, design.R, oblique.R_s, oblique.R_p, (plus - minus) / 0.2]
        ),
    )
    _csv(
        output / "tolerance_samples.csv",
        ["thickness_nm", "mean_R"],
        np.column_stack([thickness, performance]),
    )
    return {
        "category": "numerical design and assumed process variation; not measured yield",
        "band_nm": [450, 750],
        "weighting": "uniform per nm",
        "angle_deg": 0,
        "bounds_nm": [20, 180],
        "optimum_nm": optimum.thickness_nm,
        "mean_R": optimum.mean_reflectance,
        "bare_mean_R": band_average(wavelength, bare),
        "fine_grid_optimum_nm": fine.thickness_nm,
        "refinement_difference_mean_R": abs(fine.mean_reflectance - optimum.mean_reflectance),
        "assumed_parent_sigma_nm": 2,
        "samples": samples,
        "seed": seed,
        "rejected_negative_draws": rejected,
        "R_percentiles_2p5_50_97p5": np.percentile(performance, [2.5, 50, 97.5]).tolist(),
        "percentile_meaning": "assumed performance distribution, not measurement CI",
    }


def run_workflow(config_path, *, output_dir=None, figures=True):
    """Run the frozen study; paths resolve relative to the configuration file."""
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text())
    expected = {
        "schema_version",
        "seed",
        "measurement_file",
        "silicon_file",
        "output_dir",
        "monte_carlo_samples",
    }
    if set(config) != expected or config["schema_version"] != 1:
        raise ValueError("Configuration must match the documented V1 schema exactly.")
    for key in ("seed", "monte_carlo_samples"):
        if type(config[key]) is not int:
            raise ValueError(f"{key} must be an integer.")
    if config["seed"] < 0 or not 100 <= config["monte_carlo_samples"] <= 100000:
        raise ValueError("Require nonnegative seed and 100..100000 Monte Carlo samples.")
    measurement = (config_path.parent / config["measurement_file"]).resolve()
    silicon = (config_path.parent / config["silicon_file"]).resolve()
    table = read_rii_table(silicon)
    read_spectraray(measurement)  # Validate inputs before creating output files.
    output = (
        Path(output_dir).resolve()
        if output_dir
        else (config_path.parent / config["output_dir"]).resolve()
    )
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "config": config,
        "software": {
            name: version(name) for name in ("thin-film-optical-metrology", "numpy", "scipy")
        },
        "input_sha256": {
            "measurement": hashlib.sha256(measurement.read_bytes()).hexdigest(),
            "silicon": hashlib.sha256(silicon.read_bytes()).hexdigest(),
        },
    }
    report["measured"] = measured_case(measurement, table, output)
    report["synthetic"] = synthetic_case(output, config["seed"])
    report["tolerance"] = tolerance_case(
        table, output, config["monte_carlo_samples"], config["seed"] + 2
    )
    report = _plain(report)
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    if figures:
        from .plotting import make_figures

        make_figures(output, report)
    return report
