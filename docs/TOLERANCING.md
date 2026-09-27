# Coating design and tolerance propagation

The objective is uniform-per-nanometre average reflectance:

\[
\bar R(d)=\frac{1}{\lambda_b-\lambda_a}\int_{\lambda_a}^{\lambda_b}R(\lambda,d)\,d\lambda.
\]

R is a dimensionless power fraction, d and wavelength are in nm. This weighting is
explicitly chosen for a synthetic design study; it is not an illumination spectrum,
detector response or photovoltaic-current objective. The band is sampled and integrated
by the composite trapezoidal rule. Thickness candidates cover a bounded grid; every
grid-resolved local minimum is refined and compared with the two endpoints. This is
not an unconditional global-optimum claim. Grid and wavelength refinement are checked.

Tolerance propagation draws d from a normal parent distribution with declared mean
and standard deviation in nm, conditioned on d >= 0. Negative draws are resampled
and counted. For appreciable truncation the resulting mean/std differ from the parent.
The seed and sample count are recorded. The reported 2.5/50/97.5 percentiles describe
the assumed performance distribution; they are not confidence intervals for measured
manufacturing yield. Material properties and illumination angle remain fixed.

Tests recover the analytical quarter-wave optimum for a real-index ideal coating in
a narrow band, check spectral integration and design-grid convergence, verify deterministic
sampling, and exercise zero variance and substantial truncation. A 101-point broad-band
grid produced a 4.37e-6 reflectance difference from refinement and failed the initial
2e-6 target. Refining the baseline to 201 points resolves that discretization error;
the workflow uses 241 points and records its own refinement comparison.
