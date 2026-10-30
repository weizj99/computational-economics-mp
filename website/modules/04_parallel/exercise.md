# 04 Parallel computing and acceleration: exercises

Each of the eight lessons on the [unit page](index.html) ends with its task and
a folded answer. This sheet adds what needs your own computer: the programs of
this unit, what to keep in mind when you time a change, and an extra exercise
on the model's equation for output.

Download and unpack the [code](assets/computational-economics-04.zip). Paths
below are relative to the unpacked folder. `README.md` explains the setup and
`docs/GPU.md` the GPU programs.

## Programs in this unit

| Command | Lesson | Time | What it does |
| --- | --- | --- | --- |
| `python lessons/04_parallel/scaling.py --cases 16` | 01 | about 4 minutes on 4 cores | Times 16 of the 256 economies with 1, 2, 4, … worker processes and checks every result against unit 03's saved values |
| `python lessons/04_parallel/loop_vs_vectorized.py` | 02 | about 30 seconds | Solves the shares of 2,000 markets in one call and in one call per market, and compares the answers and the times |
| `python lessons/04_parallel/output_root.py` | extra exercise | about 10 seconds | Solves the output equations of unit 02's baseline economy three ways |
| `python lessons/04_parallel/check_gpu.py` | 03–08 | about 2 minutes on a GPU | Checks the GPU code against the CPU solver |

The page's "Try it yourself" and lesson 02 show what to expect from the first
two.

## Time a change yourself

Lessons 06 and 08 explain how to compare two versions of the code. When you
time a change of your own:

- Check the answer first. Solve the same economies with the same draws, and
  compare shares, markups, residuals, operating sets, exit paths and moments
  with the original version.
- Give each CPU worker one linear-algebra thread, and say whether a CPU count
  means physical cores or hardware threads.
- On a GPU, warm up first, because the first run compiles (see `docs/GPU.md`).
  Synchronize the GPU before the clock stops. Time the whole solve as well as
  the part you changed: a faster share update speeds up the whole solve by
  less.
- Profile to choose what to change, then time without the profiler, which adds
  its own cost.
- Keep every repeated time, failed runs included, with the hardware, the
  thread settings and what the clock includes.
- Keep the model equations, the objective, the candidate points, the root
  choice and the exit rule fixed. In the mixed-precision solver, change only
  the FP32 predictor and keep the FP64 checks.
- Write to new output folders, and do not time a run that resumed from saved
  checkpoints as if it had solved everything.

Plan the run time. With one worker, `scaling.py` takes about 20 minutes for all
256 economies; the earlier recordings with 16 workers took 81 seconds. One
NVIDIA L40S solved the 256 economies in 23 seconds. The GPU programs need an
NVIDIA GPU with a CUDA build of PyTorch.

## Extra: solve the output equation three ways

**Given:** the equations for aggregate output Y in the baseline economy of
unit 02, one in each exit round of each period, 29 in all. **Change:** the
method that solves them.

1. Open the [implementation map](index.html#optimization) and choose Root
   structure. Read `model/qmp/equilibrium.py::_solve_output`. Write the
   equation F(Y) = K1·Y^a − K2·Y^b − overhead = 0 and explain why qmp solves it
   in x = log Y on a bracket that starts at the top of the hump.
2. Run `python lessons/04_parallel/output_root.py`, about ten seconds. It
   solves each equation with Newton's method using a derivative written by
   hand, with Newton's method using automatic differentiation, and with
   bisection, and compares each root with qmp's.
3. Read the `Dual` class in the script. Explain how evaluating the residual at
   `Dual(x, 1.0)` gives its derivative without a formula for it.
4. Start Newton's method one unit of log Y to the left of the top of the hump.
   Which root does it find, and why is that not the economy?

**Your result:** the iterations of each method and its distance from qmp's
root, and two sentences on the wrong start.

<details>
<summary>Check your result</summary>

- With a > 0, F(Y) tends to −overhead as Y goes to 0, rises to a maximum and
  falls again, so it can have two positive roots; the economy is at the upper
  one. In log Y the top of the hump is x = [log(a/b) + log K1 − log K2]/(b − a).
  At x = (log K1 − log K2)/(b − a) the residual is negative, so these two
  points bracket the upper root and only that one.
- Iterations for the 29 equations, mean and maximum: Brent in qmp 8.9 and 10;
  Newton 6 and 6 with either derivative; bisection 50 and 50. Newton's roots
  are within 3.3 × 10⁻¹⁶ of qmp's in log Y, bisection's within 2.1 × 10⁻¹⁵.
  Five other economies, with M from 10 to 40, gave 5 to 7 Newton iterations
  and 50 for bisection.
- The automatic derivative equals the hand-written one. A dual number carries
  a value and its derivative, and each operation applies the chain rule, so
  the derivative comes from the same code as the residual.
- Started to the left of the hump, Newton's method takes 20 iterations to
  reach Y ≈ 3.8 × 10⁻⁵³, where F is also zero: the lower root, with almost no
  output. In another economy the same start does not converge at all. At the
  top of the hump the slope is zero, so Newton's method cannot start there.
  From the upper end of the bracket the residual is falling and concave, so
  each step stays to the right of the upper root and approaches it.

</details>
