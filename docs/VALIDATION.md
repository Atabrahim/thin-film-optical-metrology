# Validation and release evidence

Verification of numerical implementation is separate from validation of a physical
model against an independently characterized sample. This project does the former
extensively and supplies a conditional measured-data reanalysis; it does not claim
calibrated absolute thickness accuracy.

| Component | Independent check / failure case |
| --- | --- |
| Optical core | Fresnel, zero thickness, quarter-wave, conservation, TIR/Brewster, opaque films |
| Complex amplitudes / power | 30 seeded random stacks against independent tmm 0.2.0, tolerance 2e-12 |
| Dispersion | Cauchy unit conversion against micrometre formulation; published table endpoints |
| Import | Pinned file hash, exact row preservation, bad headers/angles/axis/nonfinite data |
| One-thickness inference | Independent Airy intensity observations and central-derivative Fisher variance |
| Two-thickness inference | Independent tmm synthetic ellipsometry; known truth and wrapped phases |
| Failure diagnostics | Identical-index layer degeneracy; active bounds; multiple interference orders |
| Design | Analytical quarter-wave optimum; wavelength and thickness-grid convergence |
| Tolerances | Seed reproducibility, zero variance, nonnegative conditioning |
| Case workflow | Phase conversion, reported correlation, known-noise recovery and refinement gates |
| Interactive demo | Streamlit AppTest changes spectral window and angle without exceptions |

Important defects found and resolved during development:

1. Numerically differentiated identical-index layers acquired spurious information.
   Central differences plus a conservative SVD-rank threshold now suppress covariance.
2. Measured source Delta had the opposite convention. It is converted explicitly,
   preserving the raw values; the independently verified optical core was unchanged.
3. An initial spectral grid missed the desired integration tolerance. Refinement
   resolved it; physical parameters and acceptance tolerance were not adjusted.

## Final execution evidence — 27 September 2026

- Complete automated suite: **38 passed, 0 failed, 0 skipped** in development and
  from a clean wheel installation (Python 3.12). This includes all scientific gates above.
- Ruff lint and formatting checks pass for source, tests and examples.
- Source distribution and wheel built successfully; the wheel was built from the sdist.
  A fresh environment installed the wheel and its declared extras; `pip check` reports
  no broken requirements. Imports resolve to that environment's site-packages.
- The exact README Python example, installed CLI, module CLI and representative full
  workflow pass. A fresh public clone followed the README's noneditable source install
  and both documented analysis commands successfully.
- Clean-wheel reproduction matches all seven CSV tables, the JSON report and all four
  PNG figures byte-for-byte in the tested environment. No scientific outputs changed
  in the final CI/documentation patch. Cross-platform equality is assessed numerically.
- Streamlit AppTest exercises both measurement windows and oblique incidence. A headless
  server bound explicitly to loopback returns HTTP 200 `ok`; the README uses that binding.
- All four scientific figures visually inspected: correct units, labels, phase-wrap
  handling, refined-minimum markers, residual signs, captions and physical interpretation.
- Local documentation links verified. Scientific source/provenance links were inspected.
- Actual GitHub Actions run [36317654740](https://github.com/Atabrahim/thin-film-optical-metrology/actions/runs/36317654740)
  succeeded for Python 3.11, 3.12 and 3.13 at `8e84e40`. It builds/installs the wheel,
  runs the full suite, checks Ruff and executes the complete plotting CLI. Deprecated
  Node actions were updated to v7 and the runner pinned to Ubuntu 24.04; updated CI passed.
  Final release publication additionally requires success on the release commit.

No unresolved implementation defect was found in the final audit. Remaining limitations
are scientific scope boundaries, including fixed optical constants, correlated measured
residuals and assumed process distributions. These are not hidden by the passing tests.
