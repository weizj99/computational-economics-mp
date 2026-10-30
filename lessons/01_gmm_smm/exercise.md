# 01 Moment matching: exercises

Direct and simulated moments, programmed step by step in Python.

## The problem and how to check it

You observe firm log sales in one sample: I = 5 firms in each of J = 100
sectors. The substitution elasticity eta = 5.75 is known. Estimate the unknown
standard deviation of log productivity, sigma_A.

The experiment generates this observed sample with sigma_A = 1. That value is
a benchmark for evaluating the estimates; it is not an input to either
estimator. Both estimators receive the observed moment and the model settings.

Find the fixed observed variance, one continuous GMM estimate, and continuous
SMM estimates for S = 1, 10, 100 and 1000 under simulation seeds 2 and 3.
Explain the role of S, then work through the repetition and random-number
exercises below. Each exercise ends with a folded "Check your result", and
`python gmm_smm.py` prints the same numbers. Your route is:

`firm log sales -> observed variance -> model moment -> squared gap -> minimizing sigma_A`.

## The model and the statistic

Consider 100 sectors with five firms in each sector. Under monopolistic
competition, use eta = 5.75 and log productivity

`log A_ij = sigma_A * epsilon_ij`, where `epsilon_ij ~ N(0,1)` independently.

The other economy settings are theta = 1.2, P = 1,
phibar = 1, varphi = 0.25 and mu_A = 0. For this exercise, the pricing and demand
conditions imply

`log r_ij = (eta - 1) * sigma_A * epsilon_ij + c_j`,

where `c_j` is common to every firm in sector j. Define the data moment as the
average of the sectors' unbiased sample variances of log sales: subtract each
sector's mean, divide its sum of squared deviations by I-1, then average over J.

This within-sector transformation removes c_j exactly. It lets us study
estimation without solving for sector-common levels. It does not replace the
equilibrium calculation needed for the later Cournot economy.

For simulation s at a candidate sigma_A, define log sales minus the common
sector level as

`x_ijs = (eta - 1) * sigma_A * epsilon_ijs`.

Calculate the statistic in three steps:

1. In each sector j, calculate `xbar_js = (1/I) * sum_i x_ijs`. Then calculate
   `v_js = (1/(I-1)) * sum_i (x_ijs - xbar_js)^2`.
2. Average those J = 100 sector variances:
   `vhat_s(sigma_A) = (1/J) * sum_j v_js`.
3. For SMM, average across S whole data sets:
   `vtilde_S(sigma_A) = (1/S) * sum_s vhat_s(sigma_A)`.

Each data set contains 500 firms. S counts data sets, not firms or sectors.
The observed target vhat uses steps 1 and 2 on the separate fixed sample from
data seed 1. A single five-firm sector is only one contribution to that target.

The page traces these steps for any candidate; the exercises below program
them.

## 1. Build a data moment

Generate one observed sample using NumPy PCG64 seed 1 and true sigma_A = 1.
Calculate the within-sector statistic v_hat. Explain why the common term c_j
has no effect. Derive

`E[v_hat | sigma_A] = (eta - 1)^2 * sigma_A^2`.

Distinguish the expectation from the moment realized in this finite sample.

<details>
<summary>Check your result</summary>

The observed moment is v_hat = 19.9036. With eta = 5.75 and sigma_A = 1 the
expectation is `(eta - 1)^2 * sigma_A^2 = 4.75^2 = 22.5625`; this finite sample
gives a lower value, and another data seed would give another one. Subtracting
the sector mean removes c_j because every firm in sector j has the same c_j.

</details>

## 2. Estimate with the direct moment

Minimize `[v(sigma_A) - v_hat]^2` over positive sigma_A. Derive the continuous
solution and compare it with a numerical minimizer. Inspect how a coarse
display grid can give a different selected point from the continuous minimum.

Is the estimate required to equal 1 in this observed sample? Explain.

<details>
<summary>Check your result</summary>

Setting `(eta - 1)^2 * sigma_A^2 = v_hat` gives
`sigma_GMM = sqrt(v_hat) / (eta - 1) = sqrt(19.9036) / 4.75 = 0.9392`. On the
page's 51-point grid the closest point is 0.94. The estimate need not equal 1:
it matches this sample's moment, which contains sampling error.

</details>

## 3. Replace the formula with simulation

Use simulation seed 2, independently of the observed data. At each candidate
sigma_A, compute the average statistic from S = 1, 10, 100 and 1000 simulated
data sets. Hold the underlying standard-normal draws fixed across candidates;
use nested prefixes as S increases.

Minimize the squared distance between this simulated moment and the same
observed v_hat. Report all four estimates to four decimal places while keeping
full precision internally. Compare with the direct-moment estimate. Repeat
with simulation seed 3 to see another realization of simulation error.

Explain why larger S approaches the direct-moment estimate for this data set,
and why a particular sequence need not move monotonically closer at each step.

<details>
<summary>Check your result</summary>

| S | Seed 2 | Seed 3 |
| --- | --- | --- |
| 1 | 0.9173 | 0.9266 |
| 10 | 0.9347 | 0.9351 |
| 100 | 0.9415 | 0.9427 |
| 1000 | 0.9393 | 0.9388 |

Both sequences end near the GMM estimate 0.9392, but not monotonically: at
S = 100 both overshoot it. A larger S averages away simulation error in the
model moment, so the estimate approaches this data set's GMM estimate, not 1.

</details>

## 4. Repeat with new observed data

Generate 1000 observed samples using data seeds 101–1100. Give every observed
sample an independent simulation sequence, using
`SeedSequence([data_seed, 20000])`. For each sample, obtain GMM, SMM(S=1) and
SMM(S=10) estimates. Save all 1000 estimates for every method.

Compute their empirical standard deviations and compare with the approximations

`SD(sigma_GMM) ≈ sigma_A / sqrt(2*J*(I-1))`,

`SD(sigma_SMM) ≈ sqrt(1+1/S) * SD(sigma_GMM)`.

Explain which source of error remains when S becomes large. The formulas are
approximations, so the standard deviations of 1000 estimates need not match
them exactly.

<details>
<summary>Check your result</summary>

| Estimator | Mean | Empirical SD | Approximate SD |
| --- | --- | --- | --- |
| GMM | 0.9978 | 0.0355 | 0.0354 |
| SMM, S = 1 | 1.0002 | 0.0495 | 0.0500 |
| SMM, S = 10 | 0.9985 | 0.0368 | 0.0371 |

The approximation for GMM is `1 / sqrt(2 * 100 * 4) = 0.0354`; for SMM it is
sqrt(2) and sqrt(1.1) times that. As S grows, the sampling error of the
observed data remains.

</details>

## 5. Change the random-number policy

Return to the original observed sample and S = 1. Draw the objective across a
candidate grid first with fixed simulation draws, then with a fresh simulation
at every candidate. For the second policy, initialize a generator with
`SeedSequence([2, 30000])` once outside the objective evaluation loop. Each
evaluation consumes new draws by advancing that same stream; do not reset its
seed inside the objective. Verify that two consecutive evaluations at the same
sigma use different draws.

Compare the curves on the same vertical scale. Explain what common random
numbers achieve, and why a smooth curve is not proof of an accurate
estimate.

<details>
<summary>Check your result</summary>

With the same draws at every candidate, the S = 1 objective is smooth and has
one minimum on the 51-point grid, at sigma_A = 0.92. With fresh draws it has
16 local minima, the lowest at 0.95. Common random numbers make the comparison
between candidates reflect the change in sigma_A rather than new draws. The
smooth curve still carries the simulation error of its one fixed draw: its
minimum, 0.92, is not the GMM estimate 0.9392.

</details>

## 6. Connect to Cournot competition

Under Cournot competition, a firm's share changes its effective elasticity and
markup; its price then feeds back into shares. Explain why the direct variance
formula used above no longer describes that economy. Describe how solving and
simulating firm outcomes can supply moments for estimation. SMM is one of
several possible estimators.

<details>
<summary>Check your result</summary>

Under Cournot competition a firm's markup depends on its share, its share on
its price and its price on its markup, so log sales are no longer
`(eta - 1) * sigma_A * epsilon` plus a sector term, and the within-sector
variance has no closed form. A solver finds the shares, prices and output for
given parameters and draws; the simulated firms then give the moments, and SMM
compares them with the data, as units 02 and 03 do. Other estimators are
possible; this course uses simulated moments.

</details>

## Reproducibility

`gmm_smm.py` implements these calculations and prints the numbers on the page.
NumPy's PCG64 seeds reproduce them; the same seed numbers in another random
number generator give different draws.
