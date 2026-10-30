"""Unit 04: check and time only the strict-precision Cournot share block on a GPU.

The NumPy solver and an eager float64 PyTorch version of the same share
iteration solve the same markets, with all firms active and with a mix of
empty, monopoly and oligopoly markets. The script checks that they agree and
times both. It needs NumPy, SciPy, threadpoolctl and CUDA-enabled PyTorch.

Run from the repository root:
    python lessons/04_parallel/gpu_share_check.py
"""
from __future__ import annotations
import argparse
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gpu_shares(z, theta, eta, gamma, n, torch):
    """Tensor equivalent of frozen qmp.equilibrium.solve_shares.

    Arrays are [firms, markets]. Converged markets freeze individually.
    The final markup uses pre-damping shares, exactly as the CPU reference.
    No torch.compile, mixed precision, TF32 or relaxed tolerance is used.
    """
    active = z > 0
    count = active.sum(dim=0)
    total = z.sum(dim=0)
    s = z / torch.where(total > 0, total, 1.0)
    mu = torch.zeros_like(z)
    iterations = torch.zeros(z.shape[1], dtype=torch.int64, device=z.device)
    residual = torch.zeros(z.shape[1], dtype=z.dtype, device=z.device)
    done = count == 0
    monopoly = count == 1
    mu = torch.where(monopoly[None, :], active.to(z.dtype) * theta / (theta - 1), mu)
    iterations = torch.where(monopoly, 1, iterations)
    done = done | monopoly
    safe_z = torch.where(active, z, 1.0)
    z_inverse = torch.where(active, safe_z ** (-1 / gamma), 0.0)
    exponent = gamma * (1 - eta) / (gamma - gamma * eta + eta)

    def update(shares):
        elasticity = 1 / (shares / theta + (1 - shares) / eta)
        markups = elasticity / (elasticity - 1)
        product = torch.where(active, markups * z_inverse, 1.0)
        weight = torch.where(active, product ** exponent, 0.0)
        denominator = weight.sum(dim=0)
        proposed = weight / torch.where(denominator > 0, denominator, 1.0)
        return proposed, torch.where(active, markups, 0.0)

    for iteration in range(1, n.share_max_iter + 1):
        if bool(done.all()):
            break
        proposed, current_mu = update(s)
        denominator = torch.linalg.vector_norm(s, dim=0)
        distance = torch.linalg.vector_norm(proposed - s, dim=0) / torch.where(denominator > 0, denominator, 1.0)
        working = ~done
        relaxed = n.share_damping * proposed + (1 - n.share_damping) * s
        normalizer = relaxed.sum(dim=0)
        relaxed = relaxed / torch.where(normalizer > 0, normalizer, 1.0)
        s = torch.where(working[None, :], relaxed, s)
        mu = torch.where(working[None, :], current_mu, mu)
        iterations = torch.where(working, iteration, iterations)
        residual = torch.where(working, distance, residual)
        done = done | (working & (distance < n.share_tol))
    if not bool(done.all()):
        raise RuntimeError("GPU share fixed point reached its iteration cap")
    proposed, _ = update(s)
    denominator = torch.linalg.vector_norm(s, dim=0)
    returned = torch.linalg.vector_norm(proposed - s, dim=0) / torch.where(denominator > 0, denominator, 1.0)
    if not bool(torch.isfinite(s).all() & torch.isfinite(mu).all()):
        raise RuntimeError("GPU share fixed point is nonfinite")
    return s, mu, {"iterations": iterations, "stopping_residual": residual, "returned_residual": returned}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/gpu_share_check.json")
    parser.add_argument("--markets", type=int, default=10000)
    parser.add_argument("--firms", type=int, default=14)
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--repetitions", type=int, default=5)
    args = parser.parse_args(argv)
    if args.markets < 10 or args.firms < 3 or args.repetitions < 5:
        parser.error("require markets >= 10, firms >= 3, repetitions >= 5")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    import numpy as np
    import torch
    from threadpoolctl import threadpool_info, threadpool_limits
    threadpool_limits(limits=1)
    sys.path.insert(0, str(ROOT / "model"))
    from qmp.draws import generate_draws, build_productivity
    from qmp.equilibrium import Numerics, solve_shares, EquilibriumError
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.backends.cuda.matmul.allow_tf32 = False
    if not torch.cuda.is_available():
        raise RuntimeError("This check needs a CUDA GPU")
    n = Numerics()
    theta, eta, gamma = 1.13125, 4.36875, 1.0252
    x = np.array([theta, eta, .9, .047041, float(args.firms), .919212])
    draws = generate_draws(args.firms, args.markets, args.seed)
    productivity, _, _ = build_productivity(x, args.markets, 1.0, draws)
    all_active = np.ascontiguousarray(productivity[:, :, 0])
    mixed = all_active.copy()
    # Predeclared masks, independent of the numerical outcomes.
    columns = np.arange(args.markets)
    mixed[:, columns % 5 == 0] = 0.0
    mixed[1:, columns % 5 == 1] = 0.0
    mixed[2:, columns % 5 == 2] = 0.0
    mixed[3:, columns % 5 == 3] = 0.0
    device = torch.device("cuda")
    props = torch.cuda.get_device_properties(device)
    cpu_model = platform.processor()
    if Path("/proc/cpuinfo").is_file():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    report = {"schema_version": 1, "scope": "Cournot market-share block only; not a full economy or annual estimate",
              "implementation": "eager float64 PyTorch; market-wise freezing; current CPU algorithm; no compilation",
              "seed": args.seed, "rng": "NumPy PCG64", "shape": [args.firms, args.markets],
              "parameters": {"theta": theta, "eta": eta, "gamma": gamma, "sigma": .047041, "rho": .9},
              "numerics": asdict(n), "repetitions": args.repetitions,
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__, "cuda": torch.version.cuda,
                          "gpu": props.name, "gpu_memory_bytes": props.total_memory, "cpu": cpu_model, "cpu_threads": 1,
                          "native_threadpools": [{key: value.get(key) for key in ("internal_api", "version", "num_threads")} for value in threadpool_info()]},
              "source_sha256": {name: sha(ROOT / "model/qmp" / name) for name in ("equilibrium.py", "draws.py")},
              "driver_sha256": sha(__file__), "cases": {},
              "timing_boundary": {"cpu": "wall time of the single-thread NumPy share solve; input already in host memory",
                                  "gpu_resident": "synchronized wall time of the eager GPU share solve, including host convergence checks; input/output remain on GPU",
                                  "gpu_transfer": "synchronized wall time including host-to-device input and device-to-host all returned arrays",
                                  "excluded": "queueing, environment setup, imports, input generation, warmup; no torch.compile"}}

    def synchronize():
        torch.cuda.synchronize(device)

    def host_result(result):
        s, mu, diag = result
        return s.cpu().numpy(), mu.cpu().numpy(), {key: value.cpu().numpy() for key, value in diag.items()}

    def timings(call, gpu=False):
        values = []
        for _ in range(args.repetitions):
            if gpu:
                synchronize()
            start = time.perf_counter()
            result = call()
            if gpu:
                synchronize()
            values.append(time.perf_counter() - start)
            del result
        return {"seconds": values, "median_seconds": float(np.median(values)), "minimum_seconds": min(values)}

    for case_name, z in (("all_active", all_active), ("mixed_active", mixed)):
        cpu = solve_shares(z, theta, eta, gamma, n)
        z_gpu = torch.as_tensor(z, dtype=torch.float64, device=device)
        gpu = host_result(gpu_shares(z_gpu, theta, eta, gamma, n, torch))
        active = z > 0
        count = active.sum(axis=0)
        error_share = float(np.max(np.abs(cpu[0] - gpu[0])))
        error_markup = float(np.max(np.abs(cpu[1] - gpu[1])))
        checks = {"shares_match": error_share <= n.share_tol,
                  "markups_match": error_markup <= 10 * n.share_tol,
                  "cpu_returned_residual": float(cpu[2]["returned_residual"].max()) <= n.share_tol,
                  "gpu_returned_residual": float(gpu[2]["returned_residual"].max()) <= n.share_tol,
                  "inactive_shares_zero": bool(np.all(gpu[0][~active] == 0)),
                  "inactive_markups_zero": bool(np.all(gpu[1][~active] == 0)),
                  "share_sums": bool(np.max(np.abs(gpu[0].sum(axis=0) - (count > 0))) <= n.share_tol),
                  "monopoly_closed_form": bool(np.all(gpu[0][:, count == 1] == active[:, count == 1]) and np.allclose(
                      gpu[1][:, count == 1], active[:, count == 1] * theta / (theta - 1),
                      rtol=0, atol=8 * np.finfo(np.float64).eps * theta / (theta - 1)))}
        if not all(checks.values()):
            raise RuntimeError(f"CPU/GPU validation failed: {case_name}: {checks}")
        cpu_call = lambda: solve_shares(z, theta, eta, gamma, n)
        resident_call = lambda: gpu_shares(z_gpu, theta, eta, gamma, n, torch)
        def transfer_call():
            return host_result(gpu_shares(torch.as_tensor(z, dtype=torch.float64, device=device), theta, eta, gamma, n, torch))
        cpu_call()
        for _ in range(2):
            resident_call()
            transfer_call()
        synchronize()
        report["cases"][case_name] = {"input_sha256": hashlib.sha256(z.tobytes()).hexdigest(),
            "market_counts": {"empty": int((count == 0).sum()), "monopoly": int((count == 1).sum()), "oligopoly": int((count > 1).sum())},
            "checks": checks, "maximum_abs_share_difference": error_share, "maximum_abs_markup_difference": error_markup,
            "maximum_returned_residual_cpu": float(cpu[2]["returned_residual"].max()),
            "maximum_returned_residual_gpu": float(gpu[2]["returned_residual"].max()),
            "maximum_iteration_difference": int(np.max(np.abs(cpu[2]["iterations"] - gpu[2]["iterations"]))),
            "maximum_iterations_cpu": int(cpu[2]["iterations"].max()), "maximum_iterations_gpu": int(gpu[2]["iterations"].max()),
            "cpu": timings(cpu_call), "gpu_resident": timings(resident_call, True), "gpu_transfer": timings(transfer_call, True)}
    cap_n = replace(n, share_max_iter=1)
    cap_checks = {"cpu_rejects_cap": False, "gpu_rejects_cap": False}
    try:
        solve_shares(all_active, theta, eta, gamma, cap_n)
    except EquilibriumError:
        cap_checks["cpu_rejects_cap"] = True
    try:
        gpu_shares(torch.as_tensor(all_active, dtype=torch.float64, device=device), theta, eta, gamma, cap_n, torch)
    except RuntimeError as exc:
        if "iteration cap" not in str(exc):
            raise
        cap_checks["gpu_rejects_cap"] = True
    if not all(cap_checks.values()):
        raise RuntimeError(f"Iteration-cap rejection failed: {cap_checks}")
    report["cap_checks"] = cap_checks
    report["passed"] = True
    target = args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "cases": list(report["cases"]), "output": str(target)}))


if __name__ == "__main__":
    main()
