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
| Publish scaffold and progress record | IN PROGRESS | Browser publication authorized on 26 September 2026 after the connector returned 403. |
| Verify experimental data and reference inputs | IN PROGRESS | Original pyElli candidate located; raw format inspected; complete provenance/licence audit pending. |
| Optical core and independent validation | NOT STARTED | No numerical implementation claimed. |
| Thickness inference and uncertainty | NOT STARTED | |
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

No Project 5 tests executed yet. No scientific results or release claims.

## Known limitations / open checks

- Experimental data lack an independent certified thickness in the recovered example.
- Measurement noise/calibration and material-parameter uncertainty must not be invented.
- pyElli repository has a GPL-3.0 licence; verify applicable dataset terms before redistribution.
- Published optical constants are reference model inputs, not validation measurements
  on this particular sample.
- AI-assisted implementation; personal competence requires reviewing and reproducing it.

## Remaining work / next action

Browser publication is explicitly authorized. Do not retry the connector write route, which
returned HTTP 403 Resource not accessible by integration. Publish this record and the minimal
Python scaffold, complete dataset provenance, then implement
and independently verify the optical forward model. Do not change Projects 1–4.

## Latest verified GitHub checkpoint

`1a273834fedb8c7afee0e2a215b99bd72211e30f` — initial README, verified on GitHub.
At preparation, the scaffold is local only. Verify the browser-created commit before advancing.
