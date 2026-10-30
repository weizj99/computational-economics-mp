# How each candidate is scored

The text version of the unit's [method page](method.html). Back to
[the search](index.html).

## The design

For one year, start with three observed targets and the bounds of σ, N and ζ,
solve the 512 candidates fixed in advance, and choose the parameter vector with
the lowest weighted loss, with its moments and loss.

For each year t, candidate i and coordinate p in (σ, N, ζ),

```
x[t, i, p] = lo[t, p] + u[i, p] × (hi[t, p] − lo[t, p])
```

The page shows the bounds, the Sobol coordinates and the mapped values of the
selected candidate. N stays continuous; M = floor(N) is the number of potential
firms per market. The average number of operating firms is an outcome of the
equilibrium, after entry and exit.

| Setting | Value |
| --- | --- |
| Years | 1980–2023: 44 annual searches |
| Candidates | 512 points fixed in advance in each annual search box |
| Coordinates | Productivity dispersion σ, continuous N, fixed-cost control ζ |
| Design | The same three-dimensional Sobol design in every box |
| Corners | Lower corner included; upper corner excluded |
| Potential firms | M = floor(N) |
| Markets / periods | 10,000 / 2 |
| Random inputs | NumPy's PCG64, seed 100; shared by candidates with the same M |
| Numerics | float64; share tolerance 1e-10; output-root tolerance 1e-12 |
| Fixed cost | φ chosen by ζ |

The σ–N plot shows two of the three coordinates, so it is not a loss surface;
the readout gives each point's ζ.

ζ picks φ. In the first round of period 1, the solver sorts the firms'
break-even fixed-labor values. If ζ < 1, φ is the first value whose cumulative
share is strictly greater than ζ; if ζ ≥ 1, φ is ζ times the largest value. φ
then stays the same in later rounds and in period 2. φ is fixed labor in model
units (1e−6 is one millionth), an outcome of the solve rather than a searched
parameter. The code is `qmp/equilibrium.py::_solve_period`.

## Three moments, fixed weights

1. Employment reallocation.
2. Sales-weighted markup.
3. Sales-weighted SGA share of total costs.

```
loss = Σ weight[k] × (model_moment[k] − target_moment[k])²
weight[k] = 1 / full_sample_variance(target_moment[k])
```

- The weights use all 44 years, with sample variance (`ddof=1`).
- Rates enter the loss as fractions. The page shows them as percentages and the
  gaps in percentage points; the display does not change the weights.
- The thin data and model bars share one scale per year and moment, across all
  512 candidates.
- The brown bar is that moment's share of the selected candidate's total loss;
  the number beside it is the weighted contribution itself.
- The three contributions add up to the total loss, up to rounding.
- Under each contribution, the arithmetic shows its weight and signed gap in the
  loss's own units, with rates as fractions. Compare a candidate with the year's
  winner using the same targets and weights.

## Selecting and reading the result

- All 22,528 records must be valid.
- The selected points are checked against the annual winners table.
- Candidates are sorted by `(loss, row_id)`.
- **Best of 512** is the candidate with the lowest weighted loss.
- **Top 15** lists the 15 candidates with the lowest loss.
- The annual parameters and fitted moments are annual values, not smoothed.
- The search-box boundaries can limit a result.
- The early-1980s markup stays above its target.
- A solve that converges can still change with new random draws; see the
  optional fresh-draw check.

## Optional fresh-draw check

| Held fixed | Changed |
| --- | --- |
| The annual fitted σ, N and ζ | PCG64 seeds 300, 301, 302 |
| The rule: ζ picks φ from the draws | New draws, generated for each M as in the estimation, and the φ that ζ picks from them |

- The draws follow the estimation's convention for each M, not unit 02's
  18-firm draws.
- The figure shows the mean and the range of three draws. Each of the three
  errors (RMSE) pools the 44 years and the three draws.
- Years with the same M share draws for each seed, so the year–seed results are
  not independent.

## Reproduce or extend

- [Python download](assets/computational-economics-03.zip): solver, estimation driver,
  a one-year search that checks itself against the saved candidates
  (`lessons/03_estimation/search_year.py`), and a script that runs the full
  search on one computer (`lessons/03_estimation/full_search.py`).
- Choose the number of workers for your computer.
- Keep each worker's results with the inputs and settings that produced them.
- Merge only runs with the same inputs and settings, and report every failed
  candidate.
- [Exercises](exercise.md): checkpointing, parallel work, complete merging,
  box boundaries and measured scaling.
