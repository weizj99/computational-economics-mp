# Whole-economy GPU comparison

The same 256 saved economies; three warmed repetitions of each configuration.

| Configuration | Median seconds | Observed range |
|---|---:|---:|
| 1 GPU · FP64 | 23.105 | 23.104–23.111 |
| 2 GPU · FP64 | 12.387 | 12.334–12.469 |
| 4 GPU · FP64 | 7.120 | 7.078–7.181 |
| 1 GPU · FP32 share prediction + FP64 correction | 17.520 | 17.499–17.577 |
| 2 GPU · FP32 share prediction + FP64 correction | 9.349 | 9.328–9.351 |
| 4 GPU · FP32 share prediction + FP64 correction | 5.605 | 5.578–5.635 |
| CPU · 64 physical cores | 35.869 | 35.575–35.873 |

## Precision

- FP64: every stage of the economy uses double precision.
- Mixed: only the share prediction uses FP32; the FP64 correction passes the
  original final residual checks.
- Prices, the output roots, the fixed cost, exit and moments stay in FP64.
- All-FP32 economies were not measured.

## Timing

- One, two and four cards solve the same total workload, split into independent
  groups of candidates.
- The clock covers sending out and collecting the work, building productivity,
  transfers, the full solves, the diagnostics and the results returned to the
  host, including the transfers back from the GPU.
- It excludes imports, starting the workers, setting up the draws, compilation,
  warm-up and the extra messages of the detailed traces.
- The 64-core CPU run used the same machine, with one native library thread per
  worker.
- Other jobs may have used other parts of the machine. Doubling the cards does
  not halve the time.
- Every reported result passed the reference and residual checks and belongs to
  the candidate it was computed for.

Hardware: INTEL(R) XEON(R) GOLD 6530 / NVIDIA L40S.

[Raw timing values](assets/multigpu_benchmark.json).
