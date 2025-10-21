The analysis proceeds through a sequence of methodical steps designed to construct and validate a hierarchical Bayesian meta-model that jointly infers the intrinsic and remnant parameters of GW231123 from two distinct waveform model posteriors, while explicitly quantifying waveform systematics. The workflow is structured as follows:

1. **Data Ingestion and Preliminary Processing**

   - Load the posterior samples from both models, NRSur7dq4 and IMRPhenomXO4a, from the provided CSV files.
   - Verify data integrity by checking for missing values, outliers, and consistency in column names and units.
   - Harmonize the parameter sets by selecting common parameters available in both datasets: primary and secondary source-frame masses (`mass_1_source`, `mass_2_source`), spin magnitudes (`a_1`, `a_2`), spin tilts (`cos_tilt_1`, `cos_tilt_2`), effective spin parameters (`chi_eff`, `chi_p`), remnant properties (`final_mass_source`, `final_spin`), redshift, and orientation angles (`cos_theta_jn`, `phi_jl`).
   - For each parameter, compute summary statistics (mean, median, standard deviation, 5th and 95th percentiles) within each model’s posterior samples to characterize central tendency and spread.
   - Generate empirical covariance matrices for key parameter subsets within each model to reveal intrinsic correlations and degeneracies.

2. **Exploratory Data Analysis (EDA) and Statistical Characterization**

   - Quantify marginal posterior differences between the two waveform models using:
     - Kolmogorov–Smirnov (KS) tests on marginal distributions of each parameter.
     - Jensen-Shannon divergence to measure distributional similarity.
   - Examine joint distributions of strongly correlated parameters (e.g., mass ratio vs. spin parameters) within each model to identify degeneracy structures.
   - Evaluate the log-likelihood distributions per model to assess relative model fit quality and sample weights.
   - Tabulate key EDA results, including:
     - Parameter-wise KS test p-values.
     - Mean and 90% credible intervals per parameter per model.
     - Cross-model covariance comparisons for selected parameter pairs.
   - These statistics guide the specification of the hierarchical meta-model by highlighting parameters with significant inter-model discrepancies and correlated uncertainties.

3. **Hierarchical Bayesian Meta-Model Specification**

   - Model the true astrophysical parameters of GW231123 as latent variables \(\theta\), encompassing masses, spins, remnant properties, and orientation angles.
   - Treat the posterior samples from NRSur7dq4 and IMRPhenomXO4a as noisy observations of \(\theta\), each subject to model-dependent systematic shifts and statistical noise.
   - Introduce waveform systematics latent variables \(\delta_m\) and \(\delta_s\) representing additive biases or distortions in masses and spins, respectively, that differ between models.
   - Define likelihood functions for each model’s samples conditioned on \(\theta\) and systematics:
     \[
     p(\text{samples}_i | \theta, \delta_i) = \prod_{j} \mathcal{N}(\text{samples}_{i,j} | \theta + \delta_i, \Sigma_{i,j})
     \]
     where \(i\) indexes the waveform model (NRSur7dq4 or IMRPhenomXO4a), \(j\) indexes posterior samples, and \(\Sigma_{i,j}\) represents sample covariance (estimated from posterior scatter).
   - Specify prior distributions for \(\theta\) informed by astrophysical expectations and previous GW population studies (e.g., mass distributions consistent with high-mass binaries).
   - Assign hierarchical priors to systematics parameters \(\delta_i\) to allow shrinkage toward zero while permitting model-dependent deviations.
   - Incorporate covariance structures capturing known parameter correlations (e.g., mass ratio-spin degeneracies) within the likelihood covariance matrices or via Gaussian Process priors on \(\delta_i\).

4. **Posterior Inference via MCMC Sampling**

   - Implement the hierarchical model in a probabilistic programming framework (e.g., PyMC, Stan) capable of multi-CPU parallelization.
   - Use the posterior samples from each waveform model as input data points in the hierarchical likelihood, rather than raw gravitational-wave strain data, to reduce computational cost.
   - Initialize multiple Markov Chain Monte Carlo (MCMC) chains with dispersed starting values for \(\theta\) and \(\delta_i\).
   - Employ adaptive Hamiltonian Monte Carlo (HMC) or No-U-Turn Sampler (NUTS) algorithms to efficiently explore the high-dimensional posterior.
   - Leverage all 8 available CPUs by running parallel chains and parallelizing likelihood evaluations where possible.
   - Monitor convergence diagnostics (Gelman-Rubin \(\hat{R}\), effective sample size) and posterior trace plots to ensure robust sampling.
   - Save posterior samples for \(\theta\) and systematics parameters for downstream analysis.

5. **Model Agreement and Systematics Quantification**

   - From the inferred posterior distributions, compute the posterior predictive distributions for each waveform model by adding estimated systematics \(\delta_i\) to the latent true parameters \(\theta\).
   - Assess the magnitude and direction of waveform systematics by analyzing the posterior distributions of \(\delta_i\).
   - Perform posterior predictive checks comparing the original model samples to the hierarchical model predictions, quantifying residual discrepancies.
   - Compute Bayes factors or information criteria (WAIC/LOO) for models with and without systematics to quantify the necessity of systematics parameters.
   - Quantify uncertainty inflation due to waveform differences by comparing credible interval widths for \(\theta\) in the hierarchical model versus single-model posteriors.

6. **Astrophysical Parameter Consolidation and Reporting**

   - Generate consolidated posterior distributions for key astrophysical parameters (component masses, spins, remnant mass and spin, effective spin parameters) marginalized over waveform systematics.
   - Provide robust credible intervals that incorporate both statistical and systematic uncertainties.
   - Tabulate final parameter estimates with uncertainty budgets decomposed into statistical and waveform-model contributions.
   - Summarize intrinsic parameter correlations disentangled from model biases, emphasizing physically meaningful degeneracies such as spin-precession effects and mass ratio-spin correlations.
   - Archive all intermediate results, including covariance matrices, systematics posterior samples, and diagnostic statistics, with clear documentation for reproducibility.

7. **Plotting and Visualization Strategy**

   - Produce a limited set of composite figures (≤10) that jointly visualize:
     - Marginal posterior distributions per model and the hierarchical meta-model consolidated posterior.
     - Joint parameter correlations highlighting degeneracies and systematics shifts.
     - Posterior distributions of waveform systematics parameters \(\delta_i\).
     - Posterior predictive checks illustrating model fit quality.
   - Combine related plots (e.g., mass and spin parameters) to optimize figure utility and avoid redundancy.
   - Save all plots and processed data outputs with metadata indicating successful execution and reproducibility.

This structured methodology ensures a principled, statistically rigorous joint inference of GW231123 parameters that explicitly accounts for waveform model systematics, enabling robust astrophysical conclusions grounded in a unified hierarchical Bayesian framework.