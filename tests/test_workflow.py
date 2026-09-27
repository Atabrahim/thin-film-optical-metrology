"""Integration gates: provenance, phase convention, inference and archived results."""

import json
from pathlib import Path

import numpy as np
import pytest

from thinfilm.workflow import run_workflow

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def completed_study(tmp_path_factory):
    directory = tmp_path_factory.mktemp("study")
    report = run_workflow(
        ROOT / "examples/case_study.json", output_dir=directory, figures=False
    )
    return directory, report


def test_measured_case_preserves_source_phase_and_exposes_model_limits(completed_study):
    directory, report = completed_study
    data = np.genfromtxt(directory / "measured_fit.csv", delimiter=",", names=True)
    np.testing.assert_allclose(data["delta_api_deg"], -data["delta_raw_deg"])
    assert report["measured"]["used_rows"] == 926
    assert report["measured"]["excluded_rows"] == 301
    fit = report["measured"]["two_thickness"]
    assert "correlated_residuals" in fit["flags"]
    assert fit["correlation"][0][1] < -0.9
    # Regression/reproducibility ranges, NOT independent certified thickness validation.
    np.testing.assert_allclose(fit["thickness_nm"], [24.977934, 276.052478], atol=0.002)
    assert max(fit["rmse"]) < 1


def test_synthetic_and_design_report_pass_scientific_gates(completed_study):
    _, report = completed_study
    synthetic = report["synthetic"]
    assert "competing_minima" in synthetic["narrow"]["flags"]
    assert "competing_minima" not in synthetic["broad"]["flags"]
    error = abs(synthetic["broad"]["thickness_nm"][0] - synthetic["truth_nm"])
    assert error < 3 * synthetic["broad"]["local_standard_errors_nm"][0]
    pair = synthetic["two_layer"]
    errors = abs(np.array(pair["thickness_nm"]) - synthetic["two_layer_truth_nm"])
    assert np.all(errors < 3 * np.array(pair["local_standard_errors_nm"]))
    design = report["tolerance"]
    assert design["mean_R"] < design["bare_mean_R"]
    assert design["refinement_difference_mean_R"] < 2e-6
    assert abs(design["optimum_nm"] - design["fine_grid_optimum_nm"]) < 0.002
    assert design["rejected_negative_draws"] == 0


def test_report_serialization_and_invalid_config(completed_study, tmp_path):
    directory, report = completed_study
    assert json.loads((directory / "report.json").read_text()) == report
    invalid = tmp_path / "bad.json"
    invalid.write_text('{"schema_version":2}')
    with pytest.raises(ValueError, match="schema"):
        run_workflow(invalid)


def test_interactive_demo_executes_and_changes_measurement_window():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(ROOT / "examples/app.py"), default_timeout=20).run()
    assert not app.exception
    app.radio[0].set_value("Spectrum: 420–780 nm").run()
    app.slider[1].set_value(55.0).run()
    assert not app.exception
