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

## Current execution evidence

- Optical milestone: 15 passed in the earlier published checkpoint.
- New material/import/inference: 14 passed.
- Tolerance/design: 5 passed.
- Workflow/demo integration: 4 passed.
- End-to-end numeric and figure workflows executed successfully.
- Four scientific figures visually inspected for labels, units, wraps, residuals,
  numerical trends and data/model distinction.
- Final combined tests, clean wheel/sdist installation and GitHub CI are still pending.

The progress record records the latest verified checkpoint; release status must not be
inferred solely from this validation design table.
