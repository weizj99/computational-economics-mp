# 02 One economy: exercises

The three lessons on the [unit page](index.html) each end with their task and a
folded answer: the exit rounds of 02.1, the two equilibrium conditions of 02.2
and the moment calculation of 02.3. This sheet follows the same economy into
the Python code.

## Follow the calculation in Python

Download and unpack the [Python source](assets/computational-economics-02.zip). The file
paths below are the same in the package and in the course repository. First run
`python lessons/02_one_economy/parameters_to_moments.py`: it solves the
baseline economy of 02.3 in about ten seconds and compares each number with the
page. Then map each economic item to a function and an array, and
record its shape. Firm outcomes have shape `(M, 10000, 2)`; an intermediate
within-period firm array has shape `(M, 10000)`.

| Economic item | Source to inspect | What to identify |
|---|---|---|
| Demand and sector/final-good prices | `07_python/qmp/equilibrium.py`, `_prices` | Relative prices, market demand and normalization `P=1` |
| Technology and input demand | `ModelConfig` and `_solve_period` | γ, αCOGS, capital share and production labor |
| Cournot prices/shares | `solve_shares` | Elasticity, markup and share stopping test |
| Overhead and profits | `_solve_period` | `fixed_labor`, SGA and `profits` |
| Labor market | `_solve_output` and `_solve_period` | Output root, wage and labor residual |
| Within-period exit | `_solve_period` | Profit cutoff, proposed deletion and pre-deletion stop |
| ζ → φ | `_solve_period` | The rank branch and maximum branch; φ then stays fixed across rounds and periods |
| Two-period productivity | `07_python/qmp/draws.py`, `build_productivity` | Fixed shocks, persistence and the two productivity arrays |
| Three moments | `07_python/qmp/moments.py`, `compute_moments` | Employment mask, first-period sales weights and three returned values |

Sort the parameters into three groups: the fixed technology and labor-supply
settings with `(θ, η)`, the candidate `(σ, N, ζ)`, and the numerical tolerances
and limits. Explain why ζ picks the fixed cost φ instead of being a cost
itself.

In `compute_moments`, check the three definitions. Employment counts production
and fixed labor in both periods, so entry and exit enter reallocation. The
markup and the SGA cost share use period-1 operating firms with economy-wide
sales weights, and the SGA moment averages each firm's ratio of SGA to total
cost, which differs from total SGA divided by total cost. Unit 03 compares
these moments with data defined the same way.

Profiling and vectorization come in [unit 04](../04_parallel/index.html).
