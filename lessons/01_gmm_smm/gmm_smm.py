"""Unit 01: estimate one parameter from one moment, directly (GMM) and by simulation (SMM).

Each of 100 sectors has five firms. A firm's log sales are (eta - 1) * sigma *
epsilon plus a term common to its sector, with epsilon standard normal. The
moment is the within-sector variance of log sales, averaged over sectors; the
common term drops out. The observed data are one sample drawn with sigma = 1.
The script prints the numbers on the unit 01 page and saves two tables.

Run from the repository root (it needs NumPy and takes about a second):
    python lessons/01_gmm_smm/gmm_smm.py
or, for the copy downloaded from the unit 01 page, from the folder that holds it:
    python gmm_smm.py
The tables go to outputs/gmm_smm in the folder you run it from.
"""
import csv
import math
from pathlib import Path

import numpy as np

FIRMS, SECTORS, ETA, TRUE_SIGMA = 5, 100, 5.75, 1.0
GRID = np.linspace(0.75, 1.25, 51)  # candidate sigmas for the objective curves
OUTPUT = Path("outputs/gmm_smm")


def normals(seed, shape):
    return np.random.Generator(np.random.PCG64(seed)).standard_normal(shape)


def statistic(draws, sigma):
    """Within-sector variance of log sales (ddof=1), averaged over sectors; firms on the last axis."""
    return np.var((ETA - 1) * sigma * np.asarray(draws), axis=-1, ddof=1).mean(axis=-1)


def draw_variance(draws):
    """The same statistic for the draws alone: the simulated moment is (eta-1)^2 sigma^2 times this."""
    return np.var(draws, axis=-1, ddof=1).mean(axis=-1)


def smm_estimate(observed, variance):
    # Solves (eta - 1)^2 sigma^2 * variance = observed for sigma.
    return math.sqrt(observed / variance) / (ETA - 1)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # 1. The data moment, from one observed sample.
    observed = float(statistic(normals(1, (SECTORS, FIRMS)), TRUE_SIGMA))
    print(f"Observed moment: {observed:.4f}")

    # 2. GMM: the model's moment has a formula, (eta - 1)^2 sigma^2, so set it equal to the data.
    gmm = math.sqrt(observed) / (ETA - 1)
    print(f"GMM estimate of sigma: {gmm:.4f}")

    # 3. SMM: average the moment over S simulated data sets. The same draws serve every
    #    candidate sigma (common random numbers), and S = 1, 10, 100 use the first draws of 1000.
    print("SMM estimates of sigma:\n     S   stream A (seed 2)   stream B (seed 3)")
    variances = {seed: draw_variance(normals(seed, (1000, SECTORS, FIRMS))) for seed in (2, 3)}
    for S in (1, 10, 100, 1000):
        a, b = (smm_estimate(observed, float(variances[seed][:S].mean())) for seed in (2, 3))
        print(f"  {S:>4}   {a:17.4f}   {b:17.4f}")

    # 4. Repeat everything with 1000 new observed samples to see how much the estimates vary.
    rows = []
    for seed in range(101, 1101):
        sample = float(statistic(normals(seed, (SECTORS, FIRMS)), TRUE_SIGMA))
        # A separate stream for simulation, so it never reuses an observed sample's seed.
        simulated = draw_variance(normals(np.random.SeedSequence([seed, 20000]), (10, SECTORS, FIRMS)))
        rows.append({"data_seed": seed, "gmm": math.sqrt(sample) / (ETA - 1),
                     "smm_S1": smm_estimate(sample, float(simulated[0])),
                     "smm_S10": smm_estimate(sample, float(simulated.mean()))})
    base = TRUE_SIGMA / math.sqrt(2 * SECTORS * (FIRMS - 1))  # large-sample sd of the GMM estimate
    print("Over 1000 samples:    mean      sd   large-sample sd")
    for key, label, S in (("gmm", "GMM", None), ("smm_S1", "SMM, S = 1", 1), ("smm_S10", "SMM, S = 10", 10)):
        values = np.array([row[key] for row in rows])
        approximation = base if S is None else base * math.sqrt(1 + 1 / S)
        print(f"  {label:<13} {values.mean():8.4f} {values.std(ddof=1):8.4f} {approximation:12.4f}")

    # 5. Two ways to draw the random numbers for SMM with S = 1. Same draws at every
    #    candidate: the objective is smooth. Fresh draws at every candidate: it jumps.
    direct = (ETA - 1) ** 2 * GRID ** 2
    same = (direct * float(variances[2][:1].mean()) - observed) ** 2
    stream = np.random.Generator(np.random.PCG64(np.random.SeedSequence([2, 30000])))
    fresh = np.array([(float(statistic(stream.standard_normal((SECTORS, FIRMS)), s)) - observed) ** 2 for s in GRID])
    for name, curve in (("same draws", same), ("fresh draws", fresh)):
        dips = int(np.sum((curve[1:-1] < curve[:-2]) & (curve[1:-1] < curve[2:])))
        print(f"SMM objective, {name}: lowest at sigma = {GRID[np.argmin(curve)]:.2f}; "
              f"{dips} local minim{'um' if dips == 1 else 'a'} on the 51-point grid")

    with (OUTPUT / "objectives.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sigma", "gmm_objective", "smm_same_draws", "smm_fresh_draws"])
        writer.writerows(zip(GRID.tolist(), ((direct - observed) ** 2).tolist(), same.tolist(), fresh.tolist()))
    with (OUTPUT / "repeated_estimates.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved objectives.csv and repeated_estimates.csv to {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
