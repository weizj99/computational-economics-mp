# Course to source

Use this map to move from a lesson's question to the calculation that answers
it. Website locations below are relative to the website folder, `06_teaching/`.
The same mapping is available in [course_map.json](../course_map.json); the
"Code on GitHub" line at the end of each lesson on the website is written from
it.

## Foundations and the economy

| Lesson and website location | Read in the source | What to do |
| --- | --- | --- |
| 00 · Shares and markups — `prerequisites/ab08.html#competition` | [ab08.py](../lessons/00_prerequisites/ab08.py): `elasticities`, `solve_sector`, `self_test` | Follow shares → elasticity → markup → price → implied shares. Compare Cournot and Bertrand in the small fixed-firm example. |
| 00 · Entry incentives — `prerequisites/berry92.html#entry` | [berry92.py](../lessons/00_prerequisites/berry92.py): `operating_profit`, `deviation_gains`, `pure_equilibria`, `ranked_equilibrium` | Check an incumbent's exit incentive and an outsider's entry incentive. Compare all operating sets with the ranked selection. |
| 01 · GMM and SMM — `modules/01_gmm_smm/index.html#moment-walkthrough` | [gmm_smm.py](../lessons/01_gmm_smm/gmm_smm.py): `statistic`, `draw_variance`, `smm_estimate`, `main`; [exercise](../lessons/01_gmm_smm/exercise.md) | Trace five firms into a sector variance, sectors into one data-set moment, and simulated data sets into SMM. Compare the estimates, repetition experiment and random-number policies. |
| 02.1 · Entry and exit — `modules/02_one_economy/index.html#entry-process` | [equilibrium.py](../07_python/qmp/equilibrium.py): `_solve_period`, `solve_economy` | Follow the active mask, profit test, proposed deletions and stopping rule. Check which state is returned before the next deletion. |
| 02.2 · Cournot and equilibrium — `modules/02_one_economy/index.html#mechanism` | [equilibrium.py](../07_python/qmp/equilibrium.py): `solve_shares`, `_prices`, `_solve_output`, `_solve_period` | Read the pricing fixed point conditional on operating firms, then trace aggregate output, wages and profits. These calculations repeat inside the exit procedure. |
| 02.3 · Parameters to moments — `modules/02_one_economy/index.html#moment-calculation` | [parameters_to_moments.py](../lessons/02_one_economy/parameters_to_moments.py): `page_draws`, `calculate`, `main`; [draws.py](../07_python/qmp/draws.py): `generate_draws`, `build_productivity`; [qmp entry](../07_python/qmp/__init__.py): `simulate`; [moments.py](../07_python/qmp/moments.py): `compute_moments` | Follow the parameter vector and common draws into two-period firm arrays. Reconstruct employment reallocation, sales weights and the two weighted moments. Solve the page's economy with the script and compare its numbers with the page. |
| 03 · Estimation — `modules/03_estimation/index.html#parameter-mapping` | [search_year.py](../lessons/03_estimation/search_year.py): `solve_candidate`, `compare`, `main`; [full_search.py](../lessons/03_estimation/full_search.py): `main`; [estimation.py](../07_python/qmp/estimation.py): `read_inputs`, `standard_sobol_points`, `make_points`, `prepare`, `solve`, `rank_records`, `select` | Map the Sobol coordinates into each search box, solve candidates, check their status, form the weighted loss and select the winner. Run one year with the script and compare it with the saved candidates. |
| 05 · Untargeted moment — `modules/05_untargeted/index.html#linking` | [decompose_markup.py](../lessons/05_untargeted/decompose_markup.py): `solve_year`, `decompose`, `levels`; [untargeted.py](../07_python/qmp/untargeted.py): `markup_decomposition`, `centred_moving_average` | Solve each year again at its unit 03 estimate with the same draws, link firms by slot across adjacent years, split the change in the sales-weighted markup into within-firm change, reallocation and net entry, and compare the cumulated parts with the data. |

The two prerequisite programs are standalone illustrations, not full empirical
AB08 or Berry replications. Lesson 01 uses the exact within-sector variance
reduction for its monopolistic-competition exercise; it does not call the
Cournot economy. Lessons 02, 03 and 05 use the main `qmp` model. Its sequential exit
procedure does not test profitable re-entry.

## Eight computing lessons

All website locations in this table begin with `modules/04_parallel/index.html`.
Lessons 04, 05 and 07 are optional: their code uses GPU kernels written in Triton.

| Lesson and fragment | Read in the source | What to inspect |
| --- | --- | --- |
| Parallel workers · `#parallel-start` | [scaling.py](../lessons/04_parallel/scaling.py): `start_worker`, `solve_case`, `trial`; [estimation.py](../07_python/qmp/estimation.py): `solve`, `select`; [full_search.py](../lessons/03_estimation/full_search.py): `main` | A serial shard owns rows selected by `row_id`. `full_search.py` runs the shards side by side; collection checks the combined records. `scaling.py` solves the page's 256 timed economies in a pool of worker processes and times it. |
| Vectorization · `#process-vectorization` | [equilibrium.py](../07_python/qmp/equilibrium.py): `solve_shares` and its nested `update`; [loop_vs_vectorized.py](../lessons/04_parallel/loop_vs_vectorized.py): `by_market`, `main` | Normalize over firms with `weight.sum(axis=0)`. Follow the `working` mask that freezes converged markets. Array syntax alone does not start worker processes. Time one call per market against one call for all markets, for several M. |
| GPU batches · `#process-gpu_batch` | [run_points_current.py](../03_gpu/run_points_current.py): `groups`, `solve_rows`; [qmp_torch_current.py](../03_gpu/qmp_torch_current.py): `solve_batch_current` | Group compatible firm counts, choose the batch from the cell budget, and restore requested row order after solving. Each economy retains its own stopping state. |
| Kernel fusion (optional) · `#process-kernel_fusion` | [qmp_torch_current.py](../03_gpu/qmp_torch_current.py): `_share_step`; [qmp_torch_share_fused.py](../03_gpu/qmp_torch_share_fused.py): `share_step_fused`, `_share_step_kernel` | Compare one ordinary share update with its fused kernel, including firm reductions. The film's scale-and-add example illustrates the idea; the real kernel does more. |
| Resident loops (optional) · `#process-resident_loop` | [qmp_torch_precision.py](../03_gpu/qmp_torch_precision.py): `solve_shares_mixed`; [qmp_torch_share_resident.py](../03_gpu/qmp_torch_share_resident.py): `solve_shares_resident_mixed`, `resident_updates`, `_resident_kernel`, `resident_backend` | Find which FP64 correction state stays on the device. Follow the per-market stops and the final independent `_share_residual` check in [qmp_torch_current.py](../03_gpu/qmp_torch_current.py). |
| Profiling · `#workflow-profiling` | [qmp_torch_current.py](../03_gpu/qmp_torch_current.py): `solve_batch_current`, `_period`, `solve_shares_current` | Identify the call and nested stages to instrument. The page's profiler snippet is pseudocode; this package does not include a profiler command or the original trace-collection harness. |
| Mixed precision (optional) · `#workflow-mixed_precision` | [qmp_torch_precision.py](../03_gpu/qmp_torch_precision.py): `_fp32_predict`, `solve_shares_mixed`, `precision_backend`; [qmp_torch_current.py](../03_gpu/qmp_torch_current.py): `_share_residual` | Follow the FP32 predictor, usable-predictor mask, remaining iteration budget, FP64 correction and final check. Prices, roots, exit and moments retain FP64. |
| Fair comparison · `#workflow-fair_comparison` | [run_points_current.py](../03_gpu/run_points_current.py): `solve_rows`; [estimation.py](../07_python/qmp/estimation.py): `diagnostic_quality`, `validate_record` | Inspect ordered results, synchronization and acceptance checks. Define the workload and timer boundary before comparing runs; the per-batch timer is not the website's end-to-end multi-worker benchmark. |
| Output equation (extra exercise) · `#optimization`, Root structure | [output_root.py](../lessons/04_parallel/output_root.py): `Dual`, `newton`, `bisection`, `main`; [equilibrium.py](../07_python/qmp/equilibrium.py): `_solve_output` | Solve each output equation with Newton's method, by hand and with automatic differentiation, and with bisection. Compare iterations and roots with qmp's Brent root, and start Newton's method on the wrong side of the hump. |

## Run and scope

- For lesson 00, run either standalone script; `--self-test` adds its existing
  checks. These examples need NumPy.
- For lesson 01, run `python lessons/01_gmm_smm/gmm_smm.py`. It draws its own
  fixed-seed inputs, prints the numbers on the page and saves two tables to
  `outputs/gmm_smm`. It needs NumPy only and takes a few seconds.
- For lesson 02, `python lessons/02_one_economy/parameters_to_moments.py`
  solves the page's baseline economy again in about ten seconds and compares
  each number the page shows with its saved value; `--case` picks another of
  the page's 17 economies. `python run.py cpu` solves an economy with
  parameters of your choice.
- For lesson 03, `python lessons/03_estimation/search_year.py --year 2000 --points 64`
  solves the first 64 candidates for 2000, reports the lowest loss and compares
  every economy with the saved candidate table, in about five minutes on one
  core. The full search, `python lessons/03_estimation/full_search.py --workers 8`,
  runs the `prepare`, `solve` and `select` commands of `python -m qmp.estimation`
  with one solver process per shard; it takes about eight hours on eight cores.
- For lesson 05, `python lessons/05_untargeted/decompose_markup.py --workers 4 --figure`
  solves the 44 annual economies again, about 18 core-minutes, and writes the
  decomposition and its figure to `outputs/untargeted`.
- For lesson 04, `python lessons/04_parallel/scaling.py` times the 256 economies
  with 1, 2, 4, … workers, and `python lessons/04_parallel/check_gpu.py` checks
  the GPU code against the CPU solver. `loop_vs_vectorized.py` (lesson 02, about
  30 seconds) and `output_root.py` (the extra exercise, about ten seconds) in
  the same folder need NumPy and SciPy only. Use `run.py gpu` for the FP64 batch runner. Read
  [GPU.md](GPU.md) before you switch on the fused, mixed or resident solver;
  importing a module alone changes nothing. The separate `08_gpu/qmp_gpu`
  package is a single-economy reference.

This map points to the code behind each lesson; it does not rebuild the website
or rerun the benchmarks. The programs that ran the profiler and the multi-GPU
and 64-core CPU benchmarks, and their raw timing logs, are not in this
repository. A timing on your own computer is a new measurement, separate from
the saved ones.
