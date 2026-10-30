# Full-economy CPU/GPU comparison

- **Work:** the same eight saved candidates, each with 10,000 markets and two
  periods. Nothing is estimated.
- **Precision:** float64, with the same share damping and stopping rules, the
  upper positive output root, separate labor accounting and the sequential exit
  rule.
- **Checks:** 17 fixed economies, including the teaching baseline and the old and
  new parameters of four years. Each compares the three moments, φ, the
  operating sets, every exit round and the full firm arrays. The result counts
  only if every case passes.
- **Clock:** three warmed repetitions, alternating CPU and GPU. The random inputs
  exist before the clock starts. The clock covers building productivity,
  uploading it, both periods, the moments and returning all output to the host.
  It excludes imports, initialization, warm-up, the checks and file writes.
- **Resources:** the process runs on one logical CPU with one numerical-library
  thread, against one GPU on the same machine. That CPU core was not reserved
  for it alone. The speed-up shown is for this workload.

## What stays on the host?

- Both versions receive inputs built the same way.
- Firm and market arrays, prices, shares, labor, profits, the sorting that sets
  the fixed cost, and exit run on the GPU.
- The scalar step that picks φ from the sorted values, and the Brent solver for
  the upper output root, run on the CPU, as in the CPU solver.
- A full GPU economy never falls back to the CPU.

## Reading the result

- Times are medians of three runs on this machine.
- The runs are warm, with Python's garbage collection on as usual; start-up is
  not timed.
- The 17 check cases compare full arrays and exit histories. The 48 timed runs
  check the moments, φ, firm counts, loss and each round's checks again, but not
  the full arrays.
- The share-block experiment and the 256-economy CPU worker experiment time
  different work, so their speed-ups cannot be multiplied.
- The JSON download has the raw errors and residuals; the table on the page
  leaves out the small residuals.
- The sequential exit rule does not test whether a firm that left could profit
  from coming back, so agreement between CPU and GPU does not show that the
  operating sets are Nash equilibria.
