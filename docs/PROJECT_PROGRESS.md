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
| Recover original roadmap and inspect Projects 1–4 | VERIFIED | Saved plan read; published repository documentation inspected. |
| Create repository and freeze scope | VERIFIED | Repository created under Atabrahim; initial README commit 1a273834fedb8c7afee0e2a215b99bd72211e30f. |
| Publish scaffold and progress record | VERIFIED, PUBLISHED | Remote scaffold files match local files at 9a2d97a; package import, sdist/wheel build and Ruff pass. |
| Verify experimental data and reference inputs | VERIFIED | Pinned source files, licence, hashes and conditions in data/PROVENANCE.md; strict import and bounded interpolation tested. Publication in progress. |
| Optical core and independent validation | VERIFIED, PUBLISHED | 15 tests pass, including 30 randomized stack comparisons with independent tmm 0.2.0; remote f8f0e75 verified. |
| Thickness inference and uncertainty | VERIFIED | Analytical Airy and independent tmm recovery, Fisher covariance, ambiguity and rank/bound checks pass. Publication in progress. |
| Measured case, synthetic ambiguity and tolerance study | NOT STARTED | |
| CLI, figures, interactive demo and documentation | NOT STARTED | |
| Full QA, clean wheel installation and CI | NOT STARTED | |
| Final release and portfolio review | NOT STARTED | |

## Scientific validation plan

Single-interface Fresnel limit; zero-thickness equivalence; normal-incidence polarization
consistency; quarter-wave antireflection; lossless energy balance; passive absorption;
total internal reflection; agreement with an independent established solver; synthetic
one/two-thickness recovery; phase-wrap residual handling; rank/bound diagnostics; fixed-seed
reproducibility; documented model-mismatch and measurement-information studies.

Analytical, numerical, synthetic, measured and reference-property results remain separate.

## Test status

Optical milestone: 15 passed, 0 failed, 0 skipped. New material/import/inference milestone:
14 passed, 0 failed, 0 skipped (27 September 2026). Ruff lint and formatting pass.
The unchanged optical tests have not yet been repeated in this milestone. Optical checks cover
Fresnel/zero-thickness/quarter-wave limits, energy balance, passive absorption,
total internal reflection, Brewster incidence, opaque films and invalid inputs.
Thirty random stacks agree with tmm 0.2.0 for complex r/t and power R/T at
2e-12 absolute/relative tolerances. These verify calculations, not measured accuracy.

## Known limitations / open checks

- Experimental data lack an independent certified thickness in the recovered example.
- Measurement noise/calibration and material-parameter uncertainty must not be invented.
- pyElli raw data retain the source repository GPL-3.0 licence and attribution separately
  from original MIT-licensed implementation; see data/PROVENANCE.md.
- Published optical constants are reference model inputs, not validation measurements
  on this particular sample.
- AI-assisted implementation; personal competence requires reviewing and reproducing it.

## Remaining work / next action

Browser publication is explicitly authorized. Do not retry the connector write route, which
returned HTTP 403 Resource not accessible by integration. Finish publishing the verified
dispersion/import/inference milestone, then implement measured/synthetic cases and tolerancing.
A falsification test exposed misleading covariance for identical-index layers; central
differences and conservative rank detection now correctly suppress it. Do not change Projects 1–4.

## Latest verified GitHub checkpoint

`f8f0e75c235acd909271117eb3acca3192f0bb2b` — optical modules, independent tests and model
documentation, verified against local files. The next checkpoint is the commit containing
this updated recovery record; its parent milestones are verified before publication.
