"""Independent units, interpolation and import checks for the pinned inputs."""

from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from thinfilm.data import read_spectraray
from thinfilm.materials import cauchy_index, read_rii_table, tabulated_index

ROOT = Path(__file__).resolve().parents[1]


def test_cauchy_units_against_micrometre_formulation():
    wavelength_um = np.array([0.4, 0.5, 0.8])
    expected = 1.5 + 0.01 / wavelength_um**2 + 0.0002 / wavelength_um**4
    np.testing.assert_allclose(cauchy_index(wavelength_um * 1000, 1.5, 1e4, 2e8), expected)


def test_reference_units_endpoints_and_interpolation():
    table = read_rii_table(ROOT / "data/reference/Si_Aspnes.yml")
    np.testing.assert_allclose(table[-1], [826.6, 3.673, 0.005])
    query = np.array([774.9, (774.9 + 826.6) / 2, 826.6])
    expected = np.array([3.714 + 0.008j, 3.6935 + 0.0065j, 3.673 + 0.005j])
    np.testing.assert_allclose(tabulated_index(query, *table.T), expected)
    with pytest.raises(ValueError, match="outside"):
        tabulated_index([850], *table.T)


def test_import_preserves_measurements_and_reports_window_selection():
    path = ROOT / "data/raw/TiO2_400cycles.txt"
    assert sha256(path.read_bytes()).hexdigest() == (
        "fd0ef2b7ad72c77a5ad87ead9e697897f54b3d3a1154b0b12e0de21e668ce702"
    )
    raw = np.loadtxt(path, skiprows=1)
    data = read_spectraray(path)
    selected = raw[(raw[:, 0] >= 400) & (raw[:, 0] <= 800)]
    np.testing.assert_array_equal(
        np.column_stack([data.wavelength_nm, data.psi_deg, data.delta_deg]), selected
    )
    assert data.angle_deg == 70.06
    assert data.original_rows == len(raw) == 1227
    assert data.excluded_outside_window == len(raw) - len(selected)


@pytest.mark.parametrize(
    "body",
    [
        "; WAVELENGTH 70 71\n400 20 350\n500 21 2\n600 20 3\n",
        "; WAVELENGTH 70 70\n400 20 350\n400 21 2\n600 20 3\n",
        "; WAVELENGTH 70 70\n400 20 350\n500 nan 2\n600 20 3\n",
    ],
)
def test_invalid_measurements_are_rejected_without_repair(tmp_path, body):
    path = tmp_path / "invalid.txt"
    path.write_text(body)
    with pytest.raises(ValueError):
        read_spectraray(path)


def test_invalid_material_inputs():
    with pytest.raises(ValueError):
        cauchy_index([0], 1.5)
    with pytest.raises(ValueError):
        tabulated_index([500], [400, 600], [1.5, 1.6], [0, -0.1])
    with pytest.raises(ValueError):
        tabulated_index([500], [600, 400], [1.5, 1.6], [0, 0])
