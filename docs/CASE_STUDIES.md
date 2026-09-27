# Case-study interpretation

Run `thinfilm examples/case_study.json --output outputs/reproduced` from the checkout.
All generated numeric tables and a JSON report are archived in `results/`. Input hashes,
package versions and random seeds are part of the report. No network download is needed.

## Measured reanalysis

Air / TiO2 / SiO2 / semi-infinite Si, 70.06°, 400–800 nm. A strict importer retains
all 926 rows inside that explicit window and reports 301 excluded rows. Raw data are
unchanged. pyElli's `Delta = -arg(r_p/r_s)` is converted to our API convention before
fitting and converted back for plots. A missing conversion originally caused >90°
phase residuals and active-bound fits; primary-source convention inspection resolved
the discrepancy without altering the optical solver or tuning material parameters.

The one-thickness case fixes oxide thickness at 276.36 nm and fits TiO2 to 24.806 nm.
The two-thickness case fits 24.978 nm TiO2 / 276.052 nm SiO2 with fixed indices and
equal degree weights for Psi and Delta. Its RMSE is 0.261° / 0.588°. These values are
reproducibility results, **not independent certified thickness validation**.

Local residual-scaled iid standard errors are 0.015/0.026 nm, correlation −0.951.
Strong residual structure violates a literal iid precision interpretation. Reference
Si may differ from this sample; film dispersion and angle are not known exactly;
the source itself fitted TiO2 dispersion to these spectra. The source's reported
24.8446 nm also used 70° and a different fitted-parameter/residual formulation.
Agreement should not be forced.

One-thickness refits, holding observations unchanged, show approximately:

| Assumption change | TiO2 thickness change |
| --- | ---: |
| Angle −0.1° / +0.1° | −0.067 / +0.067 nm |
| TiO2 Cauchy n0 −0.01 / +0.01 | +0.147 / −0.145 nm |
| Fixed oxide −1 / +1 nm | +0.561 / −0.555 nm |

These are illustrative sensitivities, not calibrated uncertainty distributions. They
are not combined in quadrature with the local errors. See `measured_sensitivity.csv`.

## Synthetic inference and ambiguity

Air / n=1.8 film / n=1.5 substrate, thickness 137 nm, normal incidence. Each experiment
has 90 observations with the same seeded Gaussian noise realization, sigma(R)=0.002.
Only the wavelength window differs: 599–601 nm versus 420–780 nm. Bounds are 20–700 nm;
15 deterministic starts are used. Every distinct converged minimum is saved.

The narrow window supports alternatives near 29.786, 136.880 and 303.548 nm within
the known-noise one-parameter 95% chi-square increment. The broad window's fit is
136.785 ± 0.153 nm (local one-sigma); the alternatives found by multistart have much
larger residual cost. This is evidence within the tested model and bounds, not a
proof of global identifiability for arbitrary materials.

The narrow case actually has a slightly *smaller local* standard error than the broad
case. Thus local precision and global ambiguity are different questions. Plot lines
sample a uniform conditional scan; markers show refined local minima that a coarse
scan might miss. No nuisance parameter varies in this single-thickness scan.

A second synthetic example fits both thicknesses (truth 27/276 nm), using 65 Psi/Delta
pairs at 70.06° and known independent 0.05° noise, seed 2027. It recovers approximately
26.983/276.024 nm; both deviations are within three local standard errors. Known-truth
recovery under the assumed model does not test the model's applicability to a real sample.

## Antireflection design and process assumptions

One transparent TiO2-like Cauchy film on reference Aspnes Si, normal incidence,
450–750 nm. Uniform-per-nm average R is minimized over 20–180 nm. A 301-point design
grid plus local refinement gives 58.352 nm. The nominal mean R is 6.288% compared
with bare-reference Si at 36.146%. A 961-point spectral / 601-point thickness refinement
changes mean R by 1.342e-6 and thickness by 0.000107 nm.

Two thousand samples use assumed normal thickness variation, sigma=2 nm, seed 2028.
No negative draws required rejection in this case. Mean-R percentiles (2.5/50/97.5)
are approximately 6.288/6.330/6.789%. Near an optimum, first-order thickness sensitivity
vanishes but second-order variation produces a skewed performance distribution. Monte
Carlo captures this; a linear uncertainty approximation alone would be misleading.

This is a hypothetical design using reference/fitted material constants. It is not a
fabricated coating, measured process distribution, process capability index or yield claim.

## Output columns

`measured_fit.csv` preserves wavelength in nm, raw Psi/Delta in degrees, converted API
Delta, two-thickness predictions, and model-minus-measurement residuals (wrapped phase).
`synthetic_*.csv` contains noiseless truth, generated observations, fits and residuals in
reflectance fractions. `ambiguity_scan.csv` records dimensionless objective increments.
`design_spectra.csv` includes R fractions and central sensitivity dR/dd in nm⁻¹ (0.1 nm
step). `tolerance_samples.csv` contains assumed thickness in nm and band-average R.

Source data retain their original licences. See [provenance](../data/PROVENANCE.md).
