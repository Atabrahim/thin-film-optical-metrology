# Optical model and conventions

V1 treats coherent plane waves in smooth, homogeneous, isotropic, passive films.
Each finite film lies between a semi-infinite ambient and substrate. There is no
backside reflection, diffuse scattering, anisotropy or incoherent averaging.

Use time dependence exp(-i omega t), complex refractive index N = n + i k
(dimensionless, n > 0, k >= 0) and forward propagation exp(+i k_z z). The ambient
index N0 is real. Vacuum wavelength lambda and film thickness d are in nm;
incidence theta0 is in degrees in the API. The conserved tangential wavevector
gives q_j = sqrt(N_j^2 - N0^2 sin(theta0)^2). Choose the passive forward branch
with nonnegative imaginary part. The layer phase is beta_j = 2 pi q_j d_j / lambda.
Exact critical incidence q_j = 0 is a singular excluded limit; nearby angles work.

Electric-field Fresnel amplitudes from medium i to j are

    r_s = (q_i - q_j) / (q_i + q_j)
    t_s = 2 q_i / (q_i + q_j)
    r_p = (N_j^2 q_i - N_i^2 q_j) / (N_j^2 q_i + N_i^2 q_j)
    t_p = 2 N_i N_j q_i / (N_j^2 q_i + N_i^2 q_j).

The p-polarization basis gives r_p = -r_s at normal incidence. It must be kept
consistent when reporting ellipsometry. Boundary conditions are continuity of
tangential electric/magnetic fields and no incoming wave from the substrate.

Starting with the last interface, combine a front interface r_i,t_i and the
remaining stack r_b,t_b through a film with P = exp(i beta):

    r = (r_i + r_b P^2) / (1 + r_i r_b P^2)
    t = t_i t_b P / (1 + r_i r_b P^2).

This is the multiple-reflection sum, algebraically equivalent to the coherent
transfer-matrix solution. For passive media |P| <= 1; no growing exponentials
are formed, so opaque films do not overflow.

R = |r|^2 is reflected power fraction. T_s = |t_s|^2 Re(q_sub)/q_0 and
T_p = |t_p|^2 Re(N_sub conj(q_sub/N_sub))/q_0. T is power entering the substrate,
not power emerging from a finite wafer. A = 1-R-T is absorption in finite films.
No clipping hides energy-balance errors. Unpolarized R averages equal s/p powers.

The ellipsometric ratio rho = r_p/r_s = tan(Psi) exp(i Delta). Psi and Delta are
reported in degrees; Delta is periodic. At zero reflected amplitude its phase
is undefined, and the API raises an error instead of inventing a phase.

## Verification versus experiment

Independent tmm 0.2.0 comparisons test the implementation under matching models.
Analytical Fresnel, quarter-wave, zero-thickness and energy limits provide
separate checks. Neither establishes the accuracy of real sample optical constants.
Synthetic observations and measured spectra are labelled separately throughout.

## References

- S. J. Byrnes, *Multilayer optical calculations* (2016, revised 2020),
  https://arxiv.org/abs/1603.02720. Equations and polarization/flux conventions.
- https://github.com/sbyrnes321/tmm — independent development-only comparator.
- https://pyelli.readthedocs.io/en/latest/auto_examples/plot_02_TiO2_multilayer.html
  — source of the measured reanalysis; not certified thickness truth.
