# Parallel computing and acceleration: sources and method notes

The page changes one part of the implementation at a time. Its diagrams show which steps depend on which; the measured times are in GPU measurements.

## What changes?

| Item | Starting layout | Current Python implementation |
|---|---|---|
| Market shares | `for market in markets: solve_shares(market)` | NumPy uses an **M × J** array, with each market in its own column. |
| Aggregate output | Calls `fsolve` from an initial guess | The CPU code brackets the root and uses Brent's method. The GPU code uses bracketed Newton steps and bisection. |
| GPU batching | One economy at a time | Stack compatible economies as **B × M × J**, with the same numerical checks. |
| Fusion | Writes intermediate arrays between operations | A fused share update combines compatible operations inside one kernel. |
| Resident iteration | The host launches and checks each correction step | A correction loop on the GPU keeps each market's own stopping point, with fewer handoffs to the host. |

The [current source package](assets/computational-economics-04.zip) contains the CPU solver
at `model/qmp/equilibrium.py`, the GPU batch engine at `gpu/batched/qmp_torch.py`,
and its current adapter at `gpu/batched/qmp_torch_current.py`. The package also
contains the optional fusion, mixed-precision and resident modules, a common
runner and usage instructions, the single-economy GPU reference in `gpu/single_economy/qmp_gpu`,
and the scripts in `lessons/04_parallel` that time the CPU workers and check the GPU code.

## Arrays run on CPUs too

- **M × J:** one economy; one column per market.
- Normalize over firms **within** each column; each market has its own share solution.
- NumPy runs array operations as compiled loops on the CPU; array code alone does not start more workers.
- Larger arrays move more data through memory, so more vectorization is not always faster.
- **B × M × J:** add independent economies to a GPU batch.

See [NumPy’s explanation of vectorized operations and memory costs](https://numpy.org/doc/stable/user/basics.broadcasting.html).

## Why Brent here?

- The inner aggregate condition has one unknown: output **Y**.
- Its structure lets us bracket the upper positive root, the one the model selects.
- Solving in **log Y** keeps output positive.
- Brent's method combines interpolation with bisection inside the bracket.
- It suits this equation with one unknown; `fsolve` is built for systems of equations.
- The GPU code does not call SciPy's Brent routine; its batched method selects the same root and runs the same checks.

Compare [Brent’s requirements](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html) with [SciPy fsolve’s nonlinear-system interface](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html). Both solve for output inside one economy; the estimation of σ, N and ζ is in unit 03.

## Read the measured times

- The table: **256 fixed economies**, both periods, three moments and diagnostics; three warmed runs of each configuration.
- 64 CPU cores and 1, 2 or 4 GPUs, on the same machine.
- FP32 predicts shares only; the FP64 correction and all the original final checks still apply.
- Prices, roots, fixed costs, exit and moments remain FP64.
- All-FP32 economies were not measured.
- The earlier single-thread and share-block results are in Earlier experiments; they time different work.

[How the times were measured](multigpu_comparison.md).
