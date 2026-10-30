# Measuring CPU parallelism

The CPU worker recordings of unit 04 solve the same 256 economies with 1, 2, 4,
8 and 16 workers. This note says what was timed and how to read the figures.

## The work

The batch is the first 256 Sobol candidates of the year-2000 search, indices
0–255, from the completed annual search. Every worker count solves exactly
these parameter vectors: one year's search box, not the 44-year estimation.

Each economy has 10,000 markets and two periods, the fixed cost chosen by ζ,
NumPy's PCG64 generator with seed 100 and the course's model settings. The
solver uses float64, a share tolerance of 1e-10 and an output-root tolerance of
1e-12. A candidate with M potential firms uses the draws generated for M firms.

## What the clock includes

The five worker counts ran one after another on one machine, each with a new
process pool. Each worker used one numerical-library thread and its own
physical core, checked from the CPU topology and the process affinity; two
hardware threads of one core count as one core.

The wall time runs from starting the pool to shutting it down: it includes
creating the draws, solving and writing the results. Waiting for the machine,
setting up the environment and preparing the inputs are outside it. There is
no warm-up, and a separate, untimed run checks correctness. Each new pool
starts with no cached draws and reuses no solved economy; the caches of the
operating system and the file system were not controlled.

A timing counts only if all 256 economies were solved and passed the original
round-level checks, matching the saved moments, φ, operating-firm count and
weighted loss within 1e-10.

## Reading the figures

For W workers and the measured time T(W):

```
speed-up   = T(1) / T(W)
efficiency = speed-up / W
worker core-time = W * T(W)
```

Worker core-time counts the worker cores over the timed run. It does not
measure processor use, energy or what the cluster charges: the same 16 physical
cores stayed reserved for the whole benchmark, including the runs with fewer
workers.

The timeline shows the recorded tasks, one lane per worker. Each worker count
has its own time scale, so compare speed with the times and the scaling plot.
The replay compresses the recorded time; its counters come from the recorded
events.

The scaling plot shows the measured points and a labelled ideal line. Each
worker count was timed once, so there are no confidence intervals. Other users
of the machine and its storage can make the times vary.

## Why the speed-up has limits

Candidate economies are independent of each other. Inside one economy, period
2 uses the fixed cost from period 1, and exit rounds and share iterations each
need the step before. Vectorizing the markets of an economy and spreading
economies over workers act at different levels. The markets of one economy
share the condition that clears the labor market and sets output, so they stay
one economy after vectorization.

Amdahl's law gives the intuition: serial work limits what more workers can
gain. Starting the pool, handling results, storage, communication and uneven
task lengths matter as well. Five single timings cannot pin down a serial
fraction or a best worker count in general.

The [timing table](assets/timings.csv) and the [Python source](assets/computational-economics-04.zip)
document the experiment; `lessons/04_parallel/scaling.py` in the download runs
it again.
