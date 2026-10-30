"""Choose the market for lesson 02.1's "Between two periods" table and save its firms.

The replay of lesson 02.1 solves the baseline economy (σ = 0.047041,
N = 14.222682, seed 100, the page's draws) with φ held at 2.064 per million.
The script solves both periods of that economy again and checks the result
against the saved replay: the whole-economy counts of continuing, entering and
exiting firms, and the final shares of Market 1's fourteen firms. It then saves
the firms of the first market in which some firms continue, at least one enters
and at least one exits, so that the table shows all three. The rounds of the
replay stay in Market 1.

    python tools/site/entry_transitions.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "model"), str(ROOT / "lessons/02_one_economy")]

from qmp import ModelConfig, Numerics  # noqa: E402
from qmp.draws import build_productivity  # noqa: E402
from qmp.equilibrium import _solve_period  # noqa: E402
from qmp.estimation import FIXED  # noqa: E402
import parameters_to_moments as page  # noqa: E402

DATA = ROOT / "website/modules/02_one_economy/assets/entry_process_data.js"
# The replay's fixed labor per operating firm, shown as 2.064 per million.
REPLAY_PHI = 2.063722001422419e-06
LABELS = {"continuing": "Continuing", "entrant": "Entrant · period 2 only",
          "exiting": "Exiting · period 1 only", "inactive": "Inactive in both periods"}


def solve_replay():
    """Both periods of the replay economy, with φ held at REPLAY_PHI."""
    config, numerics = ModelConfig(), Numerics()
    baseline = page.BASELINE
    x = np.array([FIXED["theta"], FIXED["eta"], FIXED["rho"], baseline["sigma"], baseline["N"], baseline["zeta"]])
    draws = page.page_draws(int(np.floor(baseline["N"])), config.markets, baseline["seed"])
    productivity, overhead, _ = build_productivity(x, config.markets, config.zbar, draws)
    periods = []
    for t in range(2):
        period, phi, _, _ = _solve_period(productivity[:, :, t], overhead, x[0], x[1], x[5], config, numerics, REPLAY_PHI)
        if phi != REPLAY_PHI:
            raise SystemExit("the solver changed the fixed φ")
        periods.append(period)
    return periods


def classify(first, second):
    return np.where(first & second, "continuing", np.where(second, "entrant", np.where(first, "exiting", "inactive")))


def rows_for(market, periods, classes):
    rows = []
    for i, kind in enumerate(classes[:, market]):
        shares = [float(period["s"][i, market] * 100) if period["z"][i, market] > 0 else 0.0 for period in periods]
        rows.append({"id": i + 1, "label": f"Firm {i + 1:02d}", "classification": str(kind),
                     "classification_label": LABELS[str(kind)],
                     "period0_share_label": f"{shares[0]:.2f}%", "period1_share_label": f"{shares[1]:.2f}%",
                     "period0_share_percent": shares[0], "period1_share_percent": shares[1]})
    return rows


def main():
    raw = DATA.read_text(encoding="utf-8")
    head, tail = raw[:raw.index("{")], raw[raw.rindex("}") + 1:]
    data = json.loads(raw[len(head):len(raw) - len(tail)])
    periods = solve_replay()
    classes = classify(periods[0]["z"] > 0, periods[1]["z"] > 0)
    counts = {kind: int((classes == kind).sum()) for kind in LABELS}
    saved = {item["label"].split(" ·")[0]: int(item["value"].replace(",", "")) for item in data["transitions"]["summary"]}
    if saved != {"Continuing": counts["continuing"], "Entrant": counts["entrant"], "Exiting": counts["exiting"]}:
        raise SystemExit(f"whole-economy counts {counts} differ from the saved replay {saved}")
    # Market 1's final shares in each period, as the replay's last round saved them.
    for t, period in enumerate(periods):
        saved_shares = {row["id"]: row["share_percent"] for row in data["periods"][t]["rounds"][-1]["rows"]}
        for i in range(classes.shape[0]):
            share = float(period["s"][i, 0] * 100) if period["z"][i, 0] > 0 else 0.0
            if abs(share - saved_shares[i + 1]) > 1e-9:
                raise SystemExit(f"Market 1, firm {i + 1}, period {t + 1}: share {share} differs from the replay")
    found = [(classes == kind).any(axis=0) for kind in ("continuing", "entrant", "exiting")]
    market = int(np.flatnonzero(found[0] & found[1] & found[2])[0])
    rows = rows_for(market, periods, classes)
    kinds = [row["classification"] for row in rows]
    number, entrants, exits = market + 1, kinds.count("entrant"), kinds.count("exiting")
    transitions = data["transitions"]
    transitions["title"] = f"Entry and exit across two periods · Market {number}"
    transitions["note"] = (
        f"The totals cover all 10,000 markets. The table shows Market {number}: {entrants} "
        f"entrant{'s' * (entrants != 1)}, {exits} exiting firm{'s' * (exits != 1)} and "
        f"{kinds.count('continuing')} continuing firms. In Market 1, the market of the rounds above, "
        "the same nine firms operate in both periods.")
    transitions["market"] = number
    transitions["rows"] = rows
    DATA.write_text(head + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + tail, encoding="utf-8")
    print(f"Market {number}: " + ", ".join(f"{row['label']} {row['classification']} "
                                          f"{row['period0_share_label']} → {row['period1_share_label']}" for row in rows))
    print("whole economy:", counts)


if __name__ == "__main__":
    main()
