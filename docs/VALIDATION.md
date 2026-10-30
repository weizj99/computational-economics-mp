# What has been checked

The website shows saved results. These checks connect them to the current code.

## Tests

`python run.py test` runs 41 tests in a few seconds. They cover the market
shares, the root of the output equation, the economy and its moments, the
Sobol design and the loss, the estimation's checkpoints, and the markup
decomposition.

## Scripts that reproduce the saved results

| Script | Compared with | Result on 2026-10-29 |
| --- | --- | --- |
| `lessons/01_gmm_smm/gmm_smm.py` | the 13 numbers on the unit 01 page | identical |
| `lessons/02_one_economy/parameters_to_moments.py` | the numbers saved for the unit 02 page | identical for all 17 saved economies: every displayed line, and the three moments at full precision |
| `lessons/03_estimation/search_year.py` | unit 03's saved candidates | identical for the first 64 candidates of 2000 and four of 1985 |
| `lessons/04_parallel/scaling.py` | unit 03's saved values for the 256 timed economies | identical, with four workers |
| `lessons/05_untargeted/decompose_markup.py` | unit 03's saved moments at the 44 estimates | identical; the saved table was reproduced byte for byte |

Two scripts of unit 04 check a method against the model's own one rather than
against saved results:

| Script | Compared with | Result on 2026-10-30 |
| --- | --- | --- |
| `lessons/04_parallel/loop_vs_vectorized.py` | `solve_shares` called once per market against one call for all markets | the same iterations in every market, shares and markups within 4.4 × 10⁻¹⁶, for M from 5 to 80 and 500 to 5,000 markets |
| `lessons/04_parallel/output_root.py` | qmp's Brent root of each output equation | Newton's method within 3.3 × 10⁻¹⁶ in log output and bisection within 2.1 × 10⁻¹⁵, for all 29 equations of unit 02's baseline economy; five other economies gave the same |

The scripts for units 02–05 make the comparison themselves and print the
largest difference. Unit 02's page rebuilt job creation, job destruction and
firm sales from other saved totals, so at full precision these differ from the
script's values in the last digit (at most 1.1 × 10⁻¹⁵ relative). Exact
agreement needs one linear-algebra thread per process, and these scripts set
it. With more threads, the two sales-weighted moments can change in the last
one or two digits (about 10⁻¹⁵).

## GPU code

`lessons/04_parallel/check_gpu.py` compares the GPU code with the CPU solver:
the single-economy GPU version on 17 economies, the batched engine on 8, and
the market-share step. On 2026-10-30 it passed in full on an NVIDIA RTX 4500
Ada (PyTorch 2.11.0 with CUDA 12.8, Triton 3.6.0): the three moments differed
from the CPU solver's by at most 1.6 × 10⁻¹⁵, and every economy had the same
operating firms. The full run took two minutes. A run with the tensors on the
CPU (`tools/check_gpu_on_cpu.py`) also passed; it tests the Python logic
without a GPU.

## Not rerun

- The full annual search of unit 03: 22,528 economies, about 60 core-hours.
  The scripts above rerun parts of it.
- The GPU timings on unit 04, which are saved measurements.
