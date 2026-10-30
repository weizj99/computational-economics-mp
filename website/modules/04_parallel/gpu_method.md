# Measuring the GPU share block

- **What is solved:** one market-share fixed point, with 14 potential firms and
  10,000 markets. Output, labor clearing and exit are not part of it.
- **Inputs:** NumPy's PCG64 generator with seed 100; the same float64
  productivity array goes into NumPy and PyTorch. There are two cases: every
  firm active, and a fixed mix of empty markets, monopolies and oligopolies.
- **Algorithm:** damping 0.35, share tolerance 1e-10, at most 1,000 iterations,
  each market stopping on its own, and the CPU solver's rule for the final
  markups.
- **Checks:** shares, markups, the residuals of the returned fixed points, zeros
  for inactive firms, share sums, the closed form for monopolies, and an error
  when the iteration cap is too low. The comparison with the closed forms allows
  for rounding. The [checks file](assets/gpu_share_check.json) has the raw
  diagnostics.
- **Hardware:** one core of an Intel Xeon Gold 6530 and one NVIDIA L40S, with one
  numerical-library thread. This experiment is separate from the CPU worker
  timings on the same page.
- **Timing:** the median of five solves after a warm-up. CPU inputs start in host
  memory. For "GPU · resident", inputs and outputs stay on the GPU; "GPU +
  transfers" also copies the input to the GPU and all returned arrays back. The
  GPU is synchronized before and after each solve.
- **What the clock includes:** PyTorch's array operations and the host's
  convergence checks. It excludes waiting for the machine, setup, imports,
  generating the inputs and the two warm-up calls before each set of five timed
  solves. Nothing is compiled, and everything is float64.
- **Reading the result:** these are short, repeated timings of one block on these
  inputs. They do not measure the speed-up of a whole economy or of the 44-year
  estimation.
- **Earlier GPU code:** the repository also has a full GPU solver, with its own
  earlier checks and different conventions for inputs and numerics. This
  experiment checks only the current share block.

[Python code](assets/computational-economics-04.zip)
(`lessons/04_parallel/gpu_share_check.py`) ·
[All timing repetitions and checks](assets/gpu_share_check.json)
