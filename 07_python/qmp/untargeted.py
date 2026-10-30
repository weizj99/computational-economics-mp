"""An untargeted check: decompose the change in the sales-weighted markup.

``markup_decomposition`` splits the change into within-firm change, reallocation
and net entry; ``centred_moving_average`` smooths a yearly series. A firm is the
slot (row i, market j) of the solved economies, so two years describe the same
firms only when they share the same random numbers.
"""
import numpy as np

_FIELDS = ("mu_ijt", "s_ijt", "p_ijt", "y_ijt")


def _period_one(equi):
    """Period-1 markups, shares, prices and output; inactive firms are zero."""
    missing = [name for name in _FIELDS if name not in equi]
    if missing:
        raise ValueError(f"equilibrium is missing {', '.join(missing)}")
    mu, s, p, y = (np.array(np.asarray(equi[name], dtype=np.float64)[:, :, 0]) for name in _FIELDS)
    if not mu.shape == s.shape == p.shape == y.shape:
        raise ValueError("equilibrium mu, s, p and y arrays must have the same shape")
    inactive = (s <= 0) | ~np.isfinite(mu) | ~np.isfinite(p) | ~np.isfinite(y)
    mu[inactive] = 0.0
    p[inactive] = 0.0
    y[inactive] = 0.0
    return mu, s, p, y


def _pad(arrays, rows):
    """Add empty firm rows so that two years have the same number of slots."""
    return tuple(np.vstack((a, np.zeros((rows - a.shape[0], a.shape[1])))) for a in arrays)


def markup_decomposition(equi_0, equi_1):
    """Split the change in the sales-weighted markup between two years.

    ``equi_0`` and ``equi_1`` are solved economies for the earlier and the later
    year; only their period-1 arrays are used. Sales weights are p*y over all
    active firms. Every term is measured around the earlier year's mean markup:

        total = within + reallocation + net_entry,
        reallocation = share + cross.

    ``error`` is total minus the sum of the parts, a rounding check.
    """
    mu0, s0, p0, y0 = _period_one(equi_0)
    mu1, s1, p1, y1 = _period_one(equi_1)
    if mu0.shape[1] != mu1.shape[1]:
        raise ValueError(f"adjacent years have {mu0.shape[1]} and {mu1.shape[1]} markets")
    rows = max(mu0.shape[0], mu1.shape[0])
    mu0, s0, p0, y0 = _pad((mu0, s0, p0, y0), rows)
    mu1, s1, p1, y1 = _pad((mu1, s1, p1, y1), rows)

    r0, r1 = p0 * y0, p1 * y1
    in0, in1 = (s0 > 0) & (r0 > 0), (s1 > 0) & (r1 > 0)
    r0[~in0] = 0.0
    r1[~in1] = 0.0
    if r0.sum() <= 0 or r1.sum() <= 0:
        raise ValueError("markup decomposition needs positive sales of active firms")
    w0, w1 = r0 / r0.sum(), r1 / r1.sum()
    mu0[~in0] = 0.0
    mu1[~in1] = 0.0

    both, entrant, exiter = in0 & in1, ~in0 & in1, in0 & ~in1
    dmu, dw = mu1 - mu0, w1 - w0
    mu_bar_0, mu_bar_1 = float((mu0 * w0).sum()), float((mu1 * w1).sum())
    within = float((w0[both] * dmu[both]).sum())
    share = float(((mu0[both] - mu_bar_0) * dw[both]).sum())
    cross = float((dw[both] * dmu[both]).sum())
    entry = float(((mu1[entrant] - mu_bar_0) * w1[entrant]).sum())
    exit_part = float(((mu0[exiter] - mu_bar_0) * w0[exiter]).sum())
    net_entry = entry - exit_part
    total = mu_bar_1 - mu_bar_0
    return {
        "total": total, "within": within, "reallocation": share + cross,
        "share": share, "cross": cross, "net_entry": net_entry,
        "error": total - within - share - cross - net_entry,
        "mu_bar": (mu_bar_0, mu_bar_1),
    }


def centred_moving_average(values, order=5):
    """Centred moving average that keeps the endpoints, ignoring missing values.

    Near the ends the window shrinks to the available years, so the first value
    averages the first ``(order + 1) // 2`` observations. A window with no
    finite value gives NaN.
    """
    if int(order) != order or order < 1 or order % 2 != 1:
        raise ValueError("order must be a positive odd integer")
    x = np.asarray(values, dtype=np.float64).ravel()
    half = (int(order) - 1) // 2
    out = np.full(x.shape, np.nan)
    for i in range(x.size):
        window = x[max(0, i - half):min(x.size, i + half + 1)]
        window = window[~np.isnan(window)]
        if window.size:
            out[i] = window.mean()
    return out
