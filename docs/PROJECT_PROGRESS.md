# Project progress — Thin-Film Optical Metrology and Tolerance Design

## Original objective

Project 5 of the five-project portfolio: infer coating thickness from optical measurements,
test whether the measurements identify that thickness, and evaluate coating performance
under explicitly assumed manufacturing tolerances. Recovered from
Semiconductor_Portfolio_Plan.md (18 September 2026), which identifies this as the flagship.
The original proposed repository name is thin-film-optical-metrology.

## Frozen V1 scope

- Coherent monochromatic plane-wave propagation through smooth, isotropic, homogeneous,
  passive planar films between semi-infinite ambient and substrate. Non-absorbing ambient.
- s/p reflection and transmission, R/T/A energy accounting, and ellipsometric Psi/Delta.
  Wavelength and thickness use nm; incidence and ellipsometric angles use degrees.
- One unknown thickness, then a bounded two-layer thickness case with fixed optical constants.
  Multistart least squares; residuals; local covariance/correlations and rank/bound warnings;
  profile-objective scans to expose competing solutions. Noise assumptions remain explicit.
- One experimental reanalysis: the original roadmap's pyElli ALD TiO2 / SiO2 / Si example.
  Inspect source, units, licence and conditions before including data. Fixed dispersion/
  substrate assumptions are not independent thickness measurements; no certified truth claimed.
- Synthetic inference with disclosed noise/seed, including ambiguity and a comparison showing
  how additional spectral information changes identifiability.
- One antireflection design/tolerance study: an explicit optical objective, bounded thickness
  optimization and seeded Monte Carlo using assumed (not measured) thickness variation.
- Reusable API, configuration-driven CLI, reproducible figures/reports, focused interactive
  demonstration, tests, scientific documentation, package, CI, clean-install checks and release.

Future work (not release gates): anisotropy, roughness, incoherent layers, arbitrary optical-
constant fitting, spatial maps, instrument calibration, experimental manufacturing tolerances,
and industrial process qualification.

## Architecture

| Component | Intended responsibility |
| --- | --- |
| optics | Fresnel amplitudes and coherent multilayer forward model |
| materials | Explicit dispersion/reference-table inputs and bounded interpolation |
| inference | Bounded thickness extraction, residuals and identifiability diagnostics |
| data | Auditable measured-data import and provenance |
| tolerancing | Optical design objective and seeded tolerance propagation |
| workflow / cli | Config validation and reproducible reports |
| plotting / app | Scientific static figures and focused optional interactive demo |
| tests / docs / examples | Independent checks, scientific reasoning and reproduction |

No code from existing solvers will be copied into the optical core. Reference solvers may
be development-only comparisons, with their own licences retained.

## Milestones

| Milestone | Status | Evidence |
| --- | --- | --- |
| Recover original roadmap and inspect Projects 1–4 | VERIFIED, PUBLISHED | Saved plan read; published repository documentation inspected. |
| Create repository and freeze scope | VERIFIED | Repository created under Atabrahim; initial README commit 1a273834fedb8c7afee0e2a215b99bd72211e30f. |
| Publish scaffold and progress record | VERIFIED, PUBLISHED | Remote scaffold files match local files at 9a2d97a; package import, sdist/wheel build and Ruff pass. |
| Verify experimental data and reference inputs | VERIFIED, PUBLISHED | Pinned source files, licence, hashes and conditions in data/PROVENANCE.md; strict import and bounded interpolation tested; aea9d40. |
| Optical core and independent validation | VERIFIED, PUBLISHED | 15 tests pass, including 30 randomized stack comparisons with independent tmm 0.2.0; remote f8f0e75 verified. |
| Thickness inference and uncertainty | VERIFIED, PUBLISHED | Analytical Airy and independent tmm recovery, Fisher covariance, ambiguity and rank/bound checks pass; aea9d40. |
| Measured case, synthetic ambiguity and tolerance study | VERIFIED, PUBLISHED | Complete reproducible reports and sensitivity results in results/; scientific gates pass. |
| CLI, figures, interactive demo and documentation | VERIFIED, PUBLISHED | CLI reproduces all outputs; four figures inspected; Streamlit AppTest and loopback server pass. |
| Full QA, clean wheel installation and CI | VERIFIED, PUBLISHED | 38/38 tests; Ruff; wheel/sdist; clean API/CLI; fresh-clone README workflow; CI 3.11/3.12/3.13 succeeds at 8e84e40. |
| Final release content and portfolio review | COMPLETE, VERIFIED, PUBLISHED | v0.1.0 published at d542c5c; release assets downloaded and hash-verified; learning/portfolio review in LEARNING.md. |

## Scientific validation plan

Single-interface Fresnel limit; zero-thickness equivalence; normal-incidence polarization
consistency; quarter-wave antireflection; lossless energy balance; passive absorption;
total internal reflection; agreement with an independent established solver; synthetic
one/two-thickness recovery; phase-wrap residual handling; rank/bound diagnostics; fixed-seed
reproducibility; documented model-mismatch and measurement-information studies.

Analytical, numerical, synthetic, measured and reference-property results remain separate.

## Test status

Final full suite: **38 passed, 0 failed, 0 skipped**, repeated successfully from a clean
wheel installation on 27 September 2026. Ruff lint and formatting pass. Optical checks cover
Fresnel/zero-thickness/quarter-wave limits, energy balance, passive absorption,
total internal reflection, Brewster incidence, opaque films and invalid inputs.
Thirty random stacks agree with tmm 0.2.0 for complex r/t and power R/T at
2e-12 absolute/relative tolerances. These verify calculations, not measured accuracy.

## Known scientific limitations

- Experimental data lack an independent certified thickness in the recovered example.
- Measurement noise/calibration and material-parameter uncertainty must not be invented.
- pyElli raw data retain the source repository GPL-3.0 licence and attribution separately
  from original MIT-licensed implementation; see data/PROVENANCE.md.
- Published optical constants are reference model inputs, not validation measurements
  on this particular sample.
- AI-assisted implementation; personal competence requires reviewing and reproducing it.

## Completion status / recovery action

**Project 5 V1 is complete according to the frozen scientific/software scope.**
No further feature development is required. Final documentation and release metadata are
the only publication steps associated with this record. No unresolved implementation bug
is known. Packaging, independent validation, reproducibility and full testing are verified.

Release publication is complete. Tag `v0.1.0` resolves to
`d542c5ca4a40bf635de4ff7c2c32f52b8335ffc3`. The public release and both attached
package assets were verified on 28 September 2026 (Europe/Berlin).
No remaining V1 task or known release-blocking defect remains.

## Latest verified GitHub checkpoint

Release: https://github.com/Atabrahim/thin-film-optical-metrology/releases/tag/v0.1.0

Release commit: `d542c5ca4a40bf635de4ff7c2c32f52b8335ffc3`.
Actual CI run https://github.com/Atabrahim/thin-film-optical-metrology/actions/runs/36318005630
succeeded on Python 3.11, 3.12 and 3.13. Local release source matches the tagged tree.
Both public asset downloads match the previously tested local builds byte-for-byte:

- Wheel (24,418 bytes): SHA256 `d874609bf8ad4949fae0bed9a6d394a7f11590202157e5a99e651804eef3aaf1`.
- Source distribution (885,236 bytes): SHA256 `4bfb3d16328d7e454e9e07d0120d11b0fb89824cf7182151195eea0cbd837c68`.

This post-release documentation receipt records publication; it does not change the
release tag, implementation, data, results or package assets. Do not restart development.

### Resolved findings and final QA record

- Single-layer band-average design and seeded truncated-normal tolerance propagation implemented.
- Initial 101-point spectral quadrature missed the 2e-6 reflectance convergence target;
  201-point baseline versus 801-point refinement is used instead. No physical parameters tuned.
- Measured-case integration uncovered a phase-sign mismatch, not a forward-solver error:
  [pyElli defines rho = tan(Psi) exp(-i Delta)](https://pyelli.readthedocs.io/en/latest/_modules/elli/result.html),
  whereas this package reports +arg(rp/rs). The workflow now converts measured Delta explicitly,
  preserves raw values and plots predictions in the source convention. The core was unchanged.
- Five tolerance/design tests passed; four workflow/demo tests passed. CLI generates all
  reports and four inspected figures. Measured result 24.978/276.052 nm, correlation -0.951;
  structured residuals prevent calibrated-uncertainty claims. Synthetic narrow window
  has multiple minima; broad window rejects alternatives found by multistart.
- All seven CSV tables, JSON report and four figures reproduce byte-identically from the
  clean wheel. A separate fresh-clone source installation verifies README CLI commands.
- The interrupted session removed disposable environment executables, but source code,
  input data, reports and figures survived intact. A new clean environment reproduced
  results and passed all 38 tests; no scientific implementation was rebuilt.
- Final CI maintenance updated Node-based actions to v7 and fixed the Ubuntu 24.04 runner.
  Updated CI passes; there are no science/output changes in that patch.
- Package builds, public API example, installed CLI, module CLI, optional demo, dependency
  consistency and local documentation links verified. Scientific audit covered sign,
  polarization, flux normalization, phase conversion, bounds, degeneracy and uncertainty.
