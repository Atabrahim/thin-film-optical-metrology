# Explaining this project accurately

Development and validation execution were AI-assisted. Review the implementation,
reproduce the examples and modify a small case before claiming personal mastery.
Do not imply that you fabricated the coating or collected the source ellipsometry.

## Thirty seconds

“My portfolio includes an AI-assisted Python project for thin-film optical metrology.
It models polarized multilayer spectra, fits one or two film thicknesses, and checks
whether those fits are unique. It includes a public ellipsometry reanalysis, synthetic
recovery tests and an antireflection tolerance study. Its main lesson is that a small
fit error does not automatically mean an accurate or unique physical measurement.”

## Two minutes

“Thin-film interference encodes thickness in reflected amplitude and phase. The project
uses a stable multiple-reflection recursion with complex passive refractive indices,
separate s and p polarization, and correct power normalization. Transmission refers to
power entering a semi-infinite substrate. The core was checked against analytical
limits and an independent transfer-matrix implementation.

“The inverse calculation varies one or two thicknesses with fixed optical constants.
It uses bounded multistart least squares, circular phase residuals, SVD covariance,
correlation and rank/bound diagnostics. A narrow-band synthetic example has several
interference-order solutions even though each has a small local standard error.
A broad spectrum rejects those alternatives within the tested bounds.

“The measured case uses a public ALD TiO2/SiO2/Si ellipsometry file. An explicit phase-
sign conversion matches its convention. Residual structure and strong thickness
correlation prevent a calibrated uncertainty claim. Refitting after assumed angle,
index or oxide changes separates model sensitivity from statistical covariance.

“Finally, a bounded antireflection design propagates an assumed thickness distribution
through the nonlinear forward model. It reports a simulated performance distribution,
not measured manufacturing yield. The package has automated tests, reproducible reports,
a CLI and CI. Implementation was AI-assisted; I am studying and reproducing the models
so I can explain and modify them independently.”

## Physics and mathematics to understand

| Concept | Meaning and engineering use | Example here |
| --- | --- | --- |
| Complex index | n controls phase; k controls attenuation, with a stated time convention | N=n+ik with exp(−iωt) |
| Optical thickness | Propagation phase depends on index, thickness, wavelength and angle | 2π q d / λ |
| Fresnel polarization | s and p field boundaries differ; amplitudes need flux normalization | Different R_s/R_p at 55° |
| Ellipsometry | Relative reflected amplitude/phase, not direct thickness | rho=r_p/r_s; convention conversion required |
| Identifiability | Whether distinct parameters can be distinguished by observations | Several narrow-band interference orders |
| Correlation | Thickness changes can compensate each other | Measured two-layer correlation −0.951 |
| Model discrepancy | Systematic mismatch beyond the declared noise model | Structured Psi/Delta residuals |
| Tolerance propagation | A process assumption maps into a performance distribution | Assumed 2 nm variation produces skewed mean R |

## Python and numerical design decisions

- `optics.py`: vectorize wavelengths; recurse through films. Decaying exponentials
  prevent absorbing-layer overflow. Dataclass fields separate amplitude from power.
- `materials.py`: explicit coefficient units and bounded interpolation prevent silent
  nm/µm conversion errors and unjustified extrapolation.
- `inference.py`: residual construction is separate from the optical model. Bounds
  encode the search domain; multiple starts probe basin dependence. SVD reveals nearly
  dependent Jacobian columns. Covariance is conditional, local and model-dependent.
- `tolerancing.py`: integration weights represent a scientific objective; grid refinement
  tests discretization. A seeded generator supports reproducible Monte Carlo.
- `workflow.py`: fixed case assumptions, source hashes and structured outputs make an
  analysis auditable. The CLI resolves configuration paths independently of working directory.
- Tests use independent formulas/implementations and intentional failures rather than
  only comparing a function with values it generated itself.

## Likely interview questions

1. Why can an absorbing-layer transfer matrix overflow, and why does this recursion avoid it?
2. Why is transmittance not simply |t|²? What does it mean for an absorbing substrate?
3. Why do r_p and r_s have opposite signs at normal incidence in this basis?
4. Why did the measured Delta require a sign conversion? How was that verified?
5. Can a precise optimizer return the wrong interference order?
6. Why can two adjacent equal-index films be identified only by their total thickness?
7. What assumptions underlie `(J.T @ J)^-1` as covariance?
8. Why should structured residuals change the interpretation of standard errors?
9. Is a conditional objective slice a nuisance-profile confidence interval?
10. Why is process performance skewed near an optimum even with symmetric thickness variation?
11. Which tests independently challenge the implementation, and which are only regressions?
12. What additional measurements would establish absolute thickness accuracy?

## Portfolio connection and honest application language

Projects 1–5 collectively cover equilibrium statistics, device electrostatics,
experimental Raman fitting, diffusion/process modelling and optical inverse metrology.
All use numerical validation and reusable Python; these shared practices are deliberate.
Project 5 adds complex wave optics, measurement identifiability, phase conventions and
the connection between inferred dimensions and optical design tolerances.

The portfolio signals scientific software, modelling, characterization-analysis and
R&D preparation relevant to thin-film, photonics and semiconductor metrology work.
It does not establish cleanroom experience, instrument operation, process qualification
or independent research authorship. No additional repository is needed to claim those skills.

CV wording: “AI-assisted scientific Python portfolio project: polarized multilayer
optics, bounded thickness inference with identifiability diagnostics, measured ellipsometry
reanalysis and Monte Carlo coating-tolerance studies, supported by independent numerical tests.”

LinkedIn description: “Thin-Film Optical Metrology and Tolerance Design connects polarized
optical modelling with thickness inference, uncertainty diagnostics and coating design.
The AI-assisted Python project includes public-data reanalysis, reproducible studies,
independent validation and automated software checks.”
