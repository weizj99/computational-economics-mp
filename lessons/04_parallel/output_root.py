"""Unit 04: solve the output equation three ways.

In every exit round of every period the model solves one equation for
aggregate output Y: production labor plus the fixed labor of the operating
firms equals the labor that households supply. As in qmp,

    F(Y) = K1 * Y**a - K2 * Y**b - overhead = 0,   with 0 < a < b.

F rises and then falls, so it can have two positive roots; the economy is at
the upper one. qmp solves the equation in x = log Y with SciPy's Brent method,
on a bracket that starts at the top of the hump and holds only the upper root.

This script records every such equation while it solves the baseline economy
of unit 02, and solves each one again three ways:
  - Newton's method with the derivative written by hand,
  - Newton's method with the derivative from automatic differentiation: a dual
    number carries a value and its derivative through +, -, * and exp,
  - bisection on qmp's bracket.
It prints the iterations of each method and the largest distance from qmp's
root. Last, it starts Newton's method on the wrong side of the hump.

Run from the repository root (it needs NumPy and SciPy):
    python lessons/04_parallel/output_root.py
It takes about fifteen seconds.
"""
from __future__ import annotations

import os

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import math  # noqa: E402
from pathlib import Path  # noqa: E402
import sys  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model"))

from qmp import generate_draws, simulate  # noqa: E402
from qmp import equilibrium  # noqa: E402
from qmp.estimation import FIXED  # noqa: E402

# Unit 02's baseline economy: the centre of the year-2000 search box, with the
# page's draws (18 potential firms per market, of which the economy uses 14).
X = [FIXED["theta"], FIXED["eta"], FIXED["rho"], 0.047041, 14.222682, 0.919212]
TOLERANCE = 5e-15  # on x = log Y, as qmp's call to brentq
EPS = 2.0 ** -52


class Dual:
    """A value and its derivative. Arithmetic follows f(x + e) = f(x) + f'(x) e."""

    def __init__(self, value, slope=0.0):
        self.value, self.slope = value, slope

    def __add__(self, other):
        other = lift(other)
        return Dual(self.value + other.value, self.slope + other.slope)

    __radd__ = __add__

    def __sub__(self, other):
        other = lift(other)
        return Dual(self.value - other.value, self.slope - other.slope)

    def __rsub__(self, other):
        return lift(other) - self

    def __mul__(self, other):
        other = lift(other)
        return Dual(self.value * other.value, self.slope * other.value + self.value * other.slope)

    __rmul__ = __mul__


def lift(value):
    return value if isinstance(value, Dual) else Dual(float(value))


def exp(value):
    if isinstance(value, Dual):
        e = math.exp(value.value)
        return Dual(e, e * value.slope)
    return math.exp(value)


def coefficients(wc, markets, sum_production_part, c):
    """K1, K2, a and b, as in qmp's equilibrium._solve_output."""
    ga, ac, ak = c.gamma, c.alpha_cogs, c.gamma - c.alpha_cogs
    k1 = c.varphibar * wc ** (c.varphi / ac)
    k2 = (1 / (wc ** (ak / ac) * markets)) ** (1 / ga) * c.psi_cogs * (c.r * ac / ak) ** (ak / ga) * sum_production_part
    return k1, k2, c.varphi * (ga - 1) / ac, (1 - ak) / ac


def residual(x, eq):
    """F(Y) / (K1 Y^a) at x = log Y. It works for floats and for dual numbers."""
    k1, k2, a, b, overhead = eq
    return 1 - exp(math.log(k2) - math.log(k1) + (b - a) * x) - overhead * exp(-math.log(k1) - a * x)


def slope(x, eq):
    """The derivative of the residual, written by hand."""
    k1, k2, a, b, overhead = eq
    return (-(b - a) * math.exp(math.log(k2) - math.log(k1) + (b - a) * x)
            + a * overhead * math.exp(-math.log(k1) - a * x))


def bracket(eq):
    """qmp's bracket: the top of the hump and the point where K1 Y^a = K2 Y^b."""
    k1, k2, a, b, _ = eq
    upper = (math.log(k1) - math.log(k2)) / (b - a)
    return (math.log(a / b) + math.log(k1) - math.log(k2)) / (b - a), upper


def newton(eq, x, derivative, limit=200):
    for iteration in range(1, limit + 1):
        step = residual(x, eq) / derivative(x, eq)
        x -= step
        if abs(step) <= TOLERANCE + 4 * EPS * abs(x):
            return x, iteration
    raise RuntimeError("Newton's method did not converge")


def automatic(x, eq):
    """The derivative of the residual by automatic differentiation."""
    return residual(Dual(x, 1.0), eq).slope


def bisection(eq):
    low, high = bracket(eq)
    iterations = 0
    while high - low > TOLERANCE + 4 * EPS * abs(high):
        middle = 0.5 * (low + high)
        iterations += 1
        if residual(middle, eq) > 0:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high), iterations


def record_equations():
    """Solve the economy and keep every output equation and qmp's answer."""
    equations, original = [], equilibrium._solve_output

    def recording(wc, markets, sum_production_part, overhead, c, n):
        output, relative_residual, iterations = original(wc, markets, sum_production_part, overhead, c, n)
        equations.append(((*coefficients(wc, markets, sum_production_part, c), overhead), output, iterations))
        return output, relative_residual, iterations

    bank = generate_draws(18, 10000, seed=100)
    equilibrium._solve_output = recording
    try:
        simulate(X, draws={name: value[:14] for name, value in bank.items()})
    finally:
        equilibrium._solve_output = original
    return equations


def main():
    equations = record_equations()
    a, b = equations[0][0][2:4]
    print(f"{len(equations)} output equations in unit 02's baseline economy "
          f"(every exit round of both periods); a = {a:.6f}, b = {b:.6f}")
    print(f"{'method':<34}{'iterations (mean, max)':>24}{'largest |x - x_qmp|':>22}")
    methods = {
        "Brent, as qmp (SciPy brentq)": None,
        "Newton, derivative by hand": lambda eq: newton(eq, bracket(eq)[1], slope),
        "Newton, automatic derivative": lambda eq: newton(eq, bracket(eq)[1], automatic),
        "Bisection on qmp's bracket": bisection,
    }
    agree = True
    for name, method in methods.items():
        if method is None:
            counts, gap = [iterations for _, _, iterations in equations], 0.0
        else:
            results = [method(eq) for eq, _, _ in equations]
            counts = [iterations for _, iterations in results]
            gap = max(abs(x - math.log(output)) for (x, _), (_, output, _) in zip(results, equations))
            agree &= gap <= 1e-13
        print(f"{name:<34}{sum(counts) / len(counts):>15.1f}, {max(counts):>3d}{gap:>22.1e}")

    eq, output, _ = equations[0]
    top, _ = bracket(eq)
    print()
    print(f"Round 1 of period 1 has its root at Y = {output:.6f}. Started one unit of log Y to the "
          "left of the top of the hump, Newton's method", end=" ")
    try:
        x, iterations = newton(eq, top - 1.0, slope)
        print(f"takes {iterations} iterations to reach Y = {math.exp(x):.3g}, the lower root, "
              "where F is also zero.")
    except (OverflowError, RuntimeError):
        print("does not converge.")
    print("All three methods find qmp's root to within 1e-13 in log Y." if agree else
          "A method missed qmp's root: check the code.")
    return 0 if agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
