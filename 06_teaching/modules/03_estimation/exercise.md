# 03 Estimation: exercises

Start with one year on the page: steps 1–4 under "Which point fits?" follow
candidate 2 of 2000 from its Sobol coordinates to its loss, and the answer is
folded under step 4. Repeat it for a second year and note which inputs change.
The exercises below then build the same records in Python.

## Build and run the estimation pipeline

These seven exercises build the estimation in Python. Plan the run time before
you start. One economy for 2000 takes about 4.5 seconds on one core. An
economy for 1980, with 52 potential firms per market, takes about seven times as
long. A test with the first 64 points for 2000 takes about five minutes on one
core; `lessons/03_estimation/search_year.py` in the download runs it and checks
every economy against the [candidate table](assets/search_results.csv). All
22,528 points take about 60 core-hours, most of them in the 1980s: about eight
hours on a computer with eight cores, running eight shards side by side
(exercise 5).

1. **Find the independent work.** Draw the eight calculation layers: years,
   candidates, periods, exit rounds, markets, share iterations, firms and the
   aggregate-output equation. Identify which items depend on earlier results.
   Explain why whole candidate economies can be distributed across workers,
   while period 2 inherits the fixed cost from period 1. Distinguish vectorizing
   markets inside an economy from assigning economies to workers.

   <details>
   <summary>Check your result</summary>

   Years, and candidates within a year, are independent: each candidate economy is
   solved on its own, so whole economies can go to different workers. The rest
   depends on earlier results: period 2 uses the fixed labor φ chosen in period 1;
   each exit round starts from the set the previous round left; each share
   iteration starts from the previous shares; the output equation needs the
   shares of its round. The share fixed point of one market does not depend on
   other markets, so the market loop can be vectorized inside one economy. Output,
   the wage and the exit cutoff combine all markets, so markets are not separate
   jobs.

   </details>

2. **Freeze the candidates.** Generate the course's 512-point, three-dimensional
   Sobol design with `standard_sobol_points()` in `07_python/qmp/estimation.py`.
   SciPy's default Sobol generator lists the points in a different order and
   builds the third coordinate differently, so its points would not match the
   saved candidates. Map the design into each year's supplied σ, N and ζ box.
   Save all 22,528 rows before solving: `row_id`, `year`, `sobol_index`,
   `sigma`, `N`, `M` and `zeta`. Keep N continuous and set M = floor(N).
   Explain why saving the design makes resuming and comparing implementations
   easier.

   <details>
   <summary>Check your result</summary>

   22,528 rows, 512 for each of the 44 years. For 2000 the first row is row
   10241, Sobol index 0. Sobol index 1 is the centre of the box, u = 0.5 for all
   three parameters: row 10242, candidate 2 on the page. `make_points` in
   `07_python/qmp/estimation.py` writes the same rows.

   </details>

3. **Solve and checkpoint.** Write a Python worker that reads its assigned
   rows and uses the single-economy solver. Save a completed record with its
   row ID to a temporary file, then atomically rename it. On restart, validate
   an existing record before skipping it. Preserve failed records and their
   diagnostics; never replace them with zeros.

   <details>
   <summary>Check your result</summary>

   Stop a run partway and start it again: it should skip only the records that
   validate, keep the failed ones with their diagnostics, and end with the same
   records as a run that was never stopped.

   </details>

4. **Merge and select.** Require exactly one valid result for each expected
   row. Compute the three fixed-weight squared gaps and select the smallest
   loss for each year, resolving ties by row ID. Reproduce the page's one-year
   comparison from the saved records and verify its three contributions
   and total. A lower total may combine an improvement in one moment with a
   larger gap in another; use your two rows to show the trade-off.

   <details>
   <summary>Check your result</summary>

   The winner for 2000 is row 10463, Sobol index 222, with loss 0.0159091, as on
   the page. Candidate 2 and the winner show no trade-off: all three contributions
   fall. Candidate 58, the best of the first 64 points, does show one: its markup
   contribution, 0.000632, is smaller than the winner's, 0.00570, but its
   reallocation and SGA contributions, 0.0111 and 0.0143, are larger.

   </details>

5. **Run the shards side by side.** Split the rows into as many shards as your
   computer has cores, so that no two shards share a row, and start one solver
   process per shard with one numerical-library thread each. Keep each shard's
   log. Run the merge only after every shard has stopped, and still check
   inside the merge that every record is present.
   `lessons/03_estimation/full_search.py` in the download does all of this.

   <details>
   <summary>Check your result</summary>

   A complete run writes `outputs/annual_run/annual_estimates.csv` with the same
   44 winners as the page's
   [annual parameters](assets/annual_parameters.csv): the same row IDs,
   parameters and moments. A run with `--limit 2` marks its choice as provisional.

   </details>

6. **Measure scaling.** For the same fixed 256 rows, measure elapsed time with
   1, 2, 4, 8 and 16 workers. Plot measured speed-up T(1)/T(W) and efficiency
   T(1)/(W × T(W)). Report the machine and what the clock includes. Identify overhead,
   memory pressure and load imbalance. [Unit 04](../04_parallel/index.html#parallel)
   shows the recorded times for these 256 rows, and
   `lessons/04_parallel/scaling.py` in its download runs the same experiment.
   Compare your own measurements with them, not with an ideal linear speed-up.

   <details>
   <summary>Check your result</summary>

   The recorded run on dedicated cores took 1,154, 570, 288, 147 and 81 seconds
   with 1, 2, 4, 8 and 16 workers: speed-ups of 2.02, 4.01, 7.83 and 14.26, and
   efficiencies of 1.01, 1.00, 0.98 and 0.89. Your times will differ; the shape,
   close to linear up to 8 workers and lower at 16, is what to compare.

   </details>

7. **Review the full result.** Inspect all 44 annual winners, their fitted
   moments and their distance from each box edge. List estimates within 10%
   of an edge. In the early 1980s, distinguish an N candidate close to the
   upper limit from an actual sampled value of 60. Finally open the fresh-draw
   check: which moment moves most with new draws, in which years, and why?

   <details>
   <summary>Check your result</summary>

   Within 10% of an edge of the box: N in 1980–1985 and 1987, all near the upper
   limit of 60; σ in 2018, near its upper limit; ζ in 1991, near its upper limit.
   In 1980–1987 the estimated N lies between 57.0 and 59.9. No candidate equals 60:
   the largest Sobol coordinate is 511/512, so the highest candidate N in 1980 is
   about 59.97. The fresh-draw check keeps each winner's σ, N and ζ and changes
   only the draws, so it measures how the fit depends on them; it estimates
   nothing. Reallocation moves most, in the 11 years with ζ ≥ 1 (1986–1995 and
   2002): there φ is ζ times the largest break-even value, and the largest of
   many draws changes more than the value ζ picks when ζ < 1. Across the three
   draws φ changes by up to 3.6% in those years and by at most 0.4% in the
   others; the reallocation error is 2.0 pp in those years and 0.33 pp in the
   others (0.12 and 0.25 pp with the search's draws).

   </details>

The [method note](method.md) defines the moments, objective, draw convention,
selection rule and scope of the saved results. The [candidate table](assets/search_results.csv)
contains all evaluated points, and `lessons/03_estimation/search_year.py`
compares them with your own solves.
