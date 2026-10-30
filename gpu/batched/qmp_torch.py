"""qmp_torch.py -- batched PyTorch solver for one QMP economy per parameter point.

Mirrors the v2 MATLAB engine line by line:
  calibrate_DRS.m  md5 0aed34f7   (entry threshold uses mu - gamma)
  solve_eq_DRS.m   md5 c9a22c7e
  solve_Y_DRS.m    md5 b35375d1
  solve_moments.m  md5 c87e5e84   (total cost carries the gamma/alpha_COGS factor)

What changes relative to MATLAB is only how the loops are written:
  * the parameter points of one batch share the number of potential entrants M
    and are stacked into [B, M, J] tensors (B points, M firms, J sectors);
  * the loop over the J sectors becomes one tensor operation;
  * every point carries its own (theta, eta, sigma, zeta, gamma, alpha_COGS),
    so points from different years can share a batch;
  * fsolve for aggregate output Y becomes a batched Newton iteration;
  * sectors that have converged are frozen with indicator variables (torch.where);
    points whose entry/exit game has stopped leave the batch.

Speed. Each line of plain array code reads and writes whole [B, M, J] arrays in the card's
memory, so the card spends its time moving data, not computing. The array code of one share
iteration and of each entry round therefore sits in five functions marked @torch.compile,
which merges their lines into a few GPU programs that read and write each array once.
torch.compile builds one set of programs per M and precision (B may change). The first call
with a new M compiles them; they are stored in the folders named by TORCHINDUCTOR_CACHE_DIR
and TRITON_CACHE_DIR, where later runs find them. Set both to a folder of your project: the
default is under /tmp, which is emptied at reboot. TORCH_COMPILE_DISABLE=1 runs the same
functions as plain array code.

Random numbers: calibrate_DRS resets rng(100,'twister') for every point, so the
standard-normal draws depend only on M. They are exported once from MATLAB by
matlab_ref/dump_draws.m and read here (draws/draws_M<M>.mat).

Model notation used below (code name -> model object):
  gamma      returns to scale (MATLAB glob.alpha)
  aC, aK     output elasticities of COGS and capital (glob.theta_COGS, alpha - theta_COGS)
  varphi     labour-supply elasticity (glob.varphi_1), varphibar its level
  phi        overhead labour per firm, set once from zeta in period 1
"""
import os
import numpy as np
import torch
import torch._dynamo

HERE = os.path.dirname(os.path.abspath(__file__))
DRAWS_DIR = os.path.join(HERE, "draws")

# Fixed settings shared by all points (glob fields of the MATLAB drivers).
CONST = dict(upsilon=0.35, J=10000, iter_S_max=500, tol_S=1e-3, P=1.0,
             varphi_1=0.25, psi_COGS=0.33, psi_SGA=0.33, R=1.16, zbar=1.0,
             varphibar=1.0, rho=0.90, kkk=3, entry_max=50, exit_share=1.0 / 3.0)

# STAT entries this port computes (MATLAB 1-based indices); all others stay NaN.
STAT_COMPUTED = [1, 2, 3, 4, 5, 6, 16, 17, 18, 19, 20, 21, 23, 27, 28, 49, 50, 51, 52, 53, 54]

# torch.compile keeps one set of programs per M and precision; only the number of points B is
# left free (free_b), so that points leaving the batch do not trigger new compilations.
torch._dynamo.config.automatic_dynamic_shapes = False
if hasattr(torch._dynamo.config, "recompile_limit"):
    torch._dynamo.config.recompile_limit = 1024
else:  # PyTorch 2.7 uses the earlier names for the same cache limits.
    torch._dynamo.config.cache_size_limit = 1024
if hasattr(torch._dynamo.config, "accumulated_recompile_limit"):
    torch._dynamo.config.accumulated_recompile_limit = 1024
else:
    torch._dynamo.config.accumulated_cache_size_limit = 1024


def free_b(*ts):
    """Mark dim 0 (the points) of each tensor as free to change. Sizes 0 and 1 are always
    compiled separately, so the batch is never cut below two points."""
    for t in ts:
        if isinstance(t, torch.Tensor) and t.dim() > 0 and t.shape[0] > 1:
            torch._dynamo.maybe_mark_dynamic(t, 0)
    return ts


# ----------------------------------------------------------------------------
# small helpers: evaluate a power only where a firm is active, 0 elsewhere
# ----------------------------------------------------------------------------
def spow(base, e, act):
    return torch.where(act, torch.where(act, base, 1.0) ** e, 0.0)


def load_draws(M, draws_dir=None):
    from scipy.io import loadmat
    d = loadmat(os.path.join(draws_dir or DRAWS_DIR, f"draws_M{M}.mat"))
    e1 = np.asarray(d["eps_z1"], dtype=np.float64).reshape(M, -1)
    e2 = np.asarray(d["eps_z2"], dtype=np.float64).reshape(M, -1)
    return e1, e2


_X_CACHE = {}


def quantile_positions(n):
    """X = cumsum(ones(n,1)/n) in double precision, summed in order as MATLAB does."""
    if n not in _X_CACHE:
        _X_CACHE[n] = np.cumsum(np.full(n, 1.0 / n))
    return _X_CACHE[n]


# ----------------------------------------------------------------------------
# 1. within-sector Cournot shares (solve_eq_DRS.m), all sectors of all points
# ----------------------------------------------------------------------------
@torch.compile(fullgraph=True)
def _share_start(z, act, ga, et):
    """z^(-1/gamma), the exponent of the best response, the initial guess z/sum(z), and the
    empty sectors (which count as finished from the start)."""
    zpow = torch.where(act, 1.0 / spow(z, 1.0 / ga, act).clamp_min(1e-300), 0.0)
    expo = ga * (1.0 - et) / (ga - ga * et + et)
    colsum = z.sum(1, keepdim=True)
    s = z / torch.where(colsum > 0, colsum, 1.0)
    return zpow, expo, s, act.sum(1) == 0


@torch.compile(fullgraph=True)
def _share_iter(s, mu_out, iters, done, act, zpow, th, et, expo, ups, tol, last):
    """One iteration in every sector; sectors that have stopped stay frozen."""
    eps = 1.0 / (s / th + (1.0 - s) / et)                          # Cournot elasticity
    mu = eps / (eps - 1.0)
    tmp = spow(torch.where(act, mu * zpow, 0.0), expo, act)
    tj = tmp.sum(1, keepdim=True)
    s_new = torch.where(act, tmp / torch.where(tj > 0, tj, 1.0), 0.0)
    num = torch.sqrt(((s_new - s) ** 2).sum(1))
    den = torch.sqrt((s ** 2).sum(1))
    dist = torch.where(den > 0, num / torch.where(den > 0, den, 1.0), 0.0)
    s_rel = ups * s_new + (1.0 - ups) * s
    ss = s_rel.sum(1, keepdim=True)
    s_rel = torch.where(ss > 0, s_rel / torch.where(ss > 0, ss, 1.0), s_rel)
    upd = ~done                                                     # sectors still iterating
    stop = upd & ((dist < tol) | last)
    s = torch.where(upd[:, None, :], s_rel, s)
    mu_out = torch.where(stop[:, None, :], mu, mu_out)
    return s, mu_out, iters + upd.to(iters.dtype), done | stop


def solve_shares(z, act, th, et, ga, c, check_from=6, check_every=2):
    """z, act: [B,M,J]; th, et, ga: [B,1,1].
    Returns s, mu (as MATLAB: mu from the last iteration, s after damping),
    iters [B,J] (iteration at which each sector stopped; 0 for empty sectors).
    Asking the GPU "is every sector done?" forces the CPU to wait for the GPU, so it
    is asked only every `check_every` iterations from iteration `check_from` on
    (sectors typically settle in 7-13 iterations). Finished sectors are frozen, so
    extra iterations never change results, they only cost time."""
    B, M, J = z.shape
    zpow, expo, s, done = _share_start(*free_b(z, act, ga, et))
    mu = torch.zeros_like(z)
    iters = torch.zeros((B, J), dtype=torch.int32, device=z.device)
    itmax = c["iter_S_max"]
    for it in range(1, itmax + 1):
        if it > check_from and it % check_every == 0 and bool(done.all()):
            break
        s, mu, iters, done = _share_iter(*free_b(s, mu, iters, done, act, zpow, th, et, expo),
                                         c["upsilon"], c["tol_S"], it == itmax)
    return s, mu, iters


# ----------------------------------------------------------------------------
# 2. market clearing for aggregate output Y (solve_Y_DRS.m + fsolve)
# ----------------------------------------------------------------------------
def solve_Y(WC, Jt, sum_temp, Noh, ga, aC, c, method="newton", steps=200, check_every=8):
    """Labour supply = production labour + overhead labour, one equation per point:
       F(Y) = K1*Y^a - K2*Y^b - Noh = 0.
    method: 'newton' (analytic derivative), 'autodiff' (derivative from torch.autograd),
            'bisection' (no derivative at all). All are batched over points.
    Newton stops once every point's relative step is below the precision of the
    floating-point type (checked every `check_every` steps)."""
    aK = ga - aC
    K1 = c["varphibar"] * WC ** (c["varphi_1"] / aC)
    a = c["varphi_1"] * (ga - 1.0) / aC
    K2 = (1.0 / (WC ** (aK / aC) * Jt)) ** (1.0 / ga) * c["psi_COGS"] \
        * (c["R"] * aC / aK) ** (aK / ga) * sum_temp
    b = (1.0 - aK) / aC

    def F(Y):
        return K1 * Y ** a - K2 * Y ** b - Noh

    # starting value: the closed-form root when gamma = 1 (calibrate_DRS Y_guess)
    Yg = ((K1 - Noh) / K2) ** (aC / (1.0 - aK))
    Yg = torch.where(torch.isfinite(Yg) & (Yg > 0), Yg, torch.full_like(Yg, 1e-8))
    if method == "bisection":
        lo = torch.full_like(Yg, 1e-12)
        hi = Yg * 4.0
        for _ in range(60):                                   # widen until F(hi) < 0
            grow = F(hi) > 0
            hi = torch.where(grow, hi * 4.0, hi)
        for _ in range(steps):
            mid = 0.5 * (lo + hi)
            pos = F(mid) > 0
            lo = torch.where(pos, mid, lo)
            hi = torch.where(pos, hi, mid)
        return 0.5 * (lo + hi)
    Y = Yg
    tol = 1e-14 if Y.dtype == torch.float64 else 1e-6
    for k in range(1, steps + 1):
        if method == "autodiff":
            with torch.enable_grad():
                Yv = Y.detach().requires_grad_(True)
                f = F(Yv)
                fp, = torch.autograd.grad(f.sum(), Yv)
            f, fp, Y = f.detach(), fp.detach(), Y.detach()
        else:
            f = F(Y)
            fp = K1 * a * Y ** (a - 1.0) - K2 * b * Y ** (b - 1.0)
        ok = (fp != 0) & torch.isfinite(fp)
        step = torch.where(ok, f / torch.where(ok, fp, torch.ones_like(fp)), torch.zeros_like(f))
        Yn = Y - step
        Y = torch.where((Yn <= 0) | ~torch.isfinite(Yn), Y / 2.0, Yn)
        if k % check_every == 0 and bool((step.abs() <= tol * Y.abs()).all()):
            break
    return Y


# ----------------------------------------------------------------------------
# 3. one period: entry/exit game around steps 1-2 (calibrate_DRS.m, loop over iter_Entry)
# ----------------------------------------------------------------------------
@torch.compile(fullgraph=True)
def _prices(z, act, s, mu, Njt, Jt, th, et, ga, aC, P, R):
    """B(a)-(b): wage-cost index WC, firm prices p, demand and sum_ij (d_ij/z_ij)^(1/gamma)."""
    aK = ga - aC
    c0 = (1.0 / aC) ** (aC / ga) * (R / aK) ** (aK / ga)
    th1, et1, ga1 = th[:, 0, 0], et[:, 0, 0], ga[:, 0, 0]
    Nr, Jr = Njt[:, None, :], Jt[:, None, None]
    Nsafe = torch.where(Nr > 0, Nr, 1.0)

    # B(a). wage-cost index WC = W^aC * Y^(1-gamma) from the price index P = 1
    base = (1.0 / Jr) * Nr ** ((1.0 - th) / (et - 1.0)) * spow(s, (et - th) / (et - 1.0), act)
    zinv = torch.where(act, 1.0 / spow(z, 1.0 / ga, act).clamp_min(1e-300), 0.0)
    tmp = torch.where(act, c0 * spow(base, 1.0 / ga - 1.0, act) * mu * zinv, 0.0)
    tmp = spow(tmp, ga * (1.0 - et) / (ga - ga * th + th), act)
    secsum = torch.where(act, tmp / Nsafe, 0.0).sum(1)                          # [B,J]
    inner = torch.where(secsum > 0, secsum ** ((1.0 - th1[:, None]) / (1.0 - et1[:, None])), 0.0)
    WC = ((1.0 / Jt[:, None]) * inner).sum(1) ** ((ga1 - ga1 * th1 + th1) / (th1 - 1.0)) * P ** ga1
    WCr = WC[:, None, None]

    # B(b). firm prices and sector price indices
    tmp = torch.where(act, c0 * spow(base * P ** th, 1.0 / ga - 1.0, act) * mu * zinv * WCr ** (1.0 / ga), 0.0)
    p = spow(tmp, ga / (ga - ga * th + th), act)
    sp = torch.where(act, spow(p, 1.0 - et, act) / Nsafe, 0.0).sum(1)
    p_j = torch.where(sp > 0, sp ** (1.0 / (1.0 - et1[:, None])), 0.0)
    pjsafe = torch.where(p_j > 0, p_j, 1.0)[:, None, :]
    demand = torch.where(act, (1.0 / Nsafe) * spow(p / pjsafe, -et, act) * (pjsafe / P) ** (-th), 0.0)
    zsafe = torch.where(act, z, 1.0)
    tt = spow(spow(Nr * s, (th - et) / (1.0 - et), act) * spow(p, -th, act) * P ** th
              / (Nr * zsafe), 1.0 / ga, act)                                     # (d_ij / z_ij)^(1/gamma)
    return WC, p, demand, tt.sum((1, 2))


@torch.compile(fullgraph=True)
def _profits(z, act, u, p, demand, WC, Y, Jt, phi, ga, aC, R, psiC, psiS):
    """B(d)-C: wage, quantities, production labour, and the profit of every loss maker
    (+inf for all other firms)."""
    aK = ga - aC
    W = (WC / Y ** (1.0 - ga[:, 0, 0])) ** (1.0 / aC[:, 0, 0])
    Wr = W[:, None, None]
    A = z * (1.0 / psiC) ** ga * (aK * Wr / (aC * R)) ** aK
    y = torch.where(act, (1.0 / Jt[:, None, None]) * demand * Y[:, None, None], 0.0)
    n = spow(y / torch.where(act, A, 1.0), 1.0 / ga, act)
    pi = p * y - ga * Wr * n / (aC * psiC) - Wr * (phi[:, None, None] * u) / psiS
    loss = act & (pi <= 0)
    return W, y, n, torch.where(loss, pi, float("inf")), loss.sum((1, 2))


@torch.compile(fullgraph=True)
def _apply_exit(loss_pi, pi_cut, z, u, captured):
    """Exit of the loss makers at or below the cut-off; captured points stay as they are."""
    drop = (loss_pi <= pi_cut[:, None, None]) & ~captured[:, None, None]
    return torch.where(drop, 0.0, z), torch.where(drop, 0.0, u), (drop & (z > 0)).sum((1, 2))


def solve_period(z0, pp, c, phi=None, y_method="newton"):
    """z0 [B,M,J] productivity of all potential entrants in this period.
    pp: dict of per-point parameters shaped [B,1,1] (th, et, ga, aC) and [B] (zeta).
    phi: [B] overhead level; computed from zeta in the first round if None.
    A point whose entry/exit game stops is stored in `cap` and leaves the working arrays
    (unless fewer than two points would be left)."""
    th, et, ga, aC = pp["th"], pp["et"], pp["ga"], pp["aC"]
    B, M, J = z0.shape
    dev, dt = z0.device, z0.dtype
    P, R = c["P"], c["R"]
    psiC, psiS = c["psi_COGS"], c["psi_SGA"]
    vbar, vphi = c["varphibar"], c["varphi_1"]
    z = z0
    u = torch.ones_like(z)
    compute_phi = phi is None
    phi_all = phi                                    # all B points, returned for period 2

    keys = ["z", "u", "s", "mu", "p", "y", "n", "phi_ij"]
    cap = {k: torch.zeros_like(z) for k in keys}
    cap.update(W=torch.zeros(B, dtype=dt, device=dev), Y=torch.zeros(B, dtype=dt, device=dev),
               Njt=torch.zeros((B, J), dtype=dt, device=dev),
               err=torch.zeros((B, 3), dtype=torch.float64, device=dev),
               rounds=torch.zeros(B, dtype=torch.int32, device=dev))
    rows = torch.arange(B, device=dev)              # row in `cap` of each working point
    captured = torch.zeros(B, dtype=torch.bool, device=dev)
    third = torch.tensor(c["exit_share"], dtype=torch.float64, device=dev)

    for it in range(1, c["entry_max"] + 1):
        Bw = z.shape[0]
        act = z > 0
        Njt = act.sum(1).to(dt)                                       # [B,J]
        Jt = (Njt > 0).sum(1).to(dt)                                  # [B]

        # A. shares and markups in every sector
        s, mu, iters = solve_shares(z, act, th, et, ga, c)

        # B(a)-(b). wage-cost index, prices and demand
        WC, p, demand, sum_tt = _prices(*free_b(z, act, s, mu, Njt, Jt, th, et, ga, aC), P, R)

        # B(c). overhead level phi from zeta: break-even overhead Gamma, v2 uses (mu - gamma)
        if compute_phi and it == 1:
            WCr = WC[:, None, None]
            dpow = spow(demand, 1.0 / ga, act)
            temp1 = torch.where(act, (mu - ga) * vbar * WCr ** (vphi / aC) * dpow, 0.0)
            temp2 = aC * psiC * u * spow(z, 1.0 / ga, act) * (1.0 / psiS) * sum_tt[:, None, None] \
                + (mu - ga) * dpow * u.sum((1, 2))[:, None, None]
            temp2 = torch.where(act, temp2, 0.0)
            ok = act & (temp2 != 0)
            Gam = torch.where(ok, temp1 / torch.where(ok, temp2, 1.0), 0.0)
            n_all = M * J                                              # all potential entrants active
            Gs = torch.sort(Gam.reshape(B, n_all), dim=1).values
            X = quantile_positions(n_all)
            zeta_np = pp["zeta"].double().cpu().numpy()
            idx = np.minimum(np.searchsorted(X, zeta_np, side="right"), n_all - 1)  # find(X>zeta,1)
            idx_t = torch.as_tensor(idx, device=dev)
            phi = torch.where(pp["zeta"] < 1.0, Gs[torch.arange(B, device=dev), idx_t], Gs[:, -1] * pp["zeta"])
            phi_all = phi

        # B(d). overhead labour, market clearing, quantities and profits
        Noh = phi * u.sum((1, 2))
        Y = solve_Y(WC, Jt, sum_tt, Noh, ga[:, 0, 0], aC[:, 0, 0], c, method=y_method)
        W, y, n, loss_pi, n_loss = _profits(*free_b(z, act, u, p, demand, WC, Y, Jt, phi, ga, aC),
                                            R, psiC, psiS)

        # C. exit of the least profitable third of loss makers: the cut-off is the
        # (floor(n/3)+1)-th smallest loss, found by topk instead of sorting every firm
        k = torch.floor(third * n_loss.double()).long().clamp(max=M * J - 1)
        smallest = torch.topk(loss_pi.reshape(Bw, -1), int(k.max()) + 1, dim=1, largest=False).values
        pi_cut = torch.where(n_loss > 0, smallest[torch.arange(Bw, device=dev), k], 0.0)
        z_new, u_new, dropped = _apply_exit(*free_b(loss_pi, pi_cut, z, u, captured))

        # stop when fewer than kkk firms exit; keep the state of THIS round (before the exit)
        stop = ((dropped < c["kkk"]) | (it == c["entry_max"])) & ~captured
        if bool(stop.any()):
            r = rows[stop]
            for key, val in zip(keys, [z, u, s, mu, p, y, n]):
                cap[key][r] = val[stop]
            cap["phi_ij"][r] = phi[stop][:, None, None] * u[stop]
            cap["W"][r], cap["Y"][r], cap["Njt"][r] = W[stop], Y[stop], Njt[stop]
            cap["err"][r] = torch.stack([(iters[stop] == c["iter_S_max"]).double().mean(1),
                                         iters[stop].double().mean(1),
                                         z[stop].double().mean((1, 2))], 1)
            cap["rounds"][r] = it
            captured = captured | stop
        n_left = int((~captured).sum())
        if n_left == 0:
            break
        z, u = z_new, u_new
        if 2 <= n_left < Bw:                         # the stopped points leave the batch
            keep = ~captured
            z, u, th, et, ga, aC, phi, rows, captured = [
                x[keep] for x in (z, u, th, et, ga, aC, phi, rows, captured)]
    return cap, phi_all


# ----------------------------------------------------------------------------
# 4. moments (solve_moments.m, v2)
# ----------------------------------------------------------------------------
def moments(c1, c2, pp, phi, c):
    ga, aC = pp["ga"], pp["aC"]
    psiC, psiS = c["psi_COGS"], c["psi_SGA"]
    B = ga.shape[0]
    zero = torch.zeros_like(c1["n"])
    mu0 = torch.where(c1["z"] > 0, c1["mu"], zero)
    n0 = torch.where(c1["z"] > 0, c1["n"], zero)
    n1 = torch.where(c2["z"] > 0, c2["n"], zero)
    z0 = torch.where(n0 > 0, c1["z"], zero)
    z1 = torch.where(n1 > 0, c2["z"], zero)
    p0 = torch.where(z0 > 0, c1["p"], zero)
    y0 = torch.where(z0 > 0, c1["y"], zero)
    f0 = torch.where(z0 > 0, c1["phi_ij"], zero)
    f1 = torch.where(z1 > 0, c2["phi_ij"], zero)
    W0 = c1["W"][:, None, None]

    on0 = n0 > 0
    on1 = n1 > 0
    ever = on0 | on1
    r0 = p0 * y0
    TC = (ga / aC) * (1.0 / psiC) * W0 * n0 + (1.0 / psiS) * W0 * f0
    SGA = (1.0 / psiS) * f0 * W0
    cogs = (W0 / psiC) * n0
    kexp = ((ga - aC) / aC) * cogs

    def wsum(w, v):  # weighted mean over operating firms in period 0
        w = torch.where(on0, w, zero)
        return (w * v).sum((1, 2)) / w.sum((1, 2))

    stat = torch.full((B, 54), float("nan"), dtype=torch.float64, device=ga.device)
    # 1. job reallocation rate, employment = production + overhead labour
    inc = ever & on0 & on1
    ex = ever & on0 & ~on1
    en = ever & ~on0 & on1
    e0, e1 = n0 + f0, n1 + f1
    dpos = torch.where(inc & (e1 > e0), e1 - e0, zero).sum((1, 2))
    dneg = torch.where(inc & (e0 > e1), e0 - e1, zero).sum((1, 2))
    JC = dpos + torch.where(en, e1, zero).sum((1, 2))
    JD = dneg + torch.where(ex, e0, zero).sum((1, 2))
    L0 = torch.where(inc | ex, e0, zero).sum((1, 2))
    L1 = torch.where(inc | en, e1, zero).sum((1, 2))
    stat[:, 0] = (JC + JD) / (0.5 * (L0 + L1))
    # 2. profit rate
    stat[:, 1] = torch.where(on0, r0 - TC, zero).sum((1, 2)) / torch.where(on0, r0, zero).sum((1, 2))
    # 3. sales-weighted markup; 4. its sales-weighted 75th percentile
    stat[:, 2] = wsum(r0, mu0)
    om = torch.where(on0, r0, zero).reshape(B, -1)
    om = om / om.sum(1, keepdim=True)
    mu_flat = torch.where(on0, mu0, torch.full_like(mu0, float("inf"))).reshape(B, -1)
    order = torch.argsort(mu_flat, 1)
    cum = torch.cumsum(torch.gather(om, 1, order), 1)
    first = torch.argmax((cum > 0.75).to(torch.int8), 1)
    stat[:, 3] = torch.gather(mu_flat, 1, torch.gather(order, 1, first[:, None]))[:, 0]
    # 5-6. overhead (SGA) share of total cost: unweighted and sales-weighted
    sga_tc = torch.where(on0, SGA / torch.where(on0, TC, torch.ones_like(TC)), zero)
    nop = on0.sum((1, 2)).to(sga_tc.dtype)
    stat[:, 4] = sga_tc.sum((1, 2)) / nop
    stat[:, 5] = wsum(r0, sga_tc)
    # 16-18. wage, labour supply and output in period 1
    stat[:, 15] = c1["W"]
    stat[:, 16] = c["varphibar"] * c1["W"] ** c["varphi_1"]
    stat[:, 17] = c1["Y"]
    # 19. labour share of sales (gamma on production labour); 20. firm entry rate
    stat[:, 18] = (torch.where(on0, ga * W0 * n0 + W0 * f0, zero).sum((1, 2))
                   / torch.where(on0, r0, zero).sum((1, 2)))
    stat[:, 19] = (~on0 & on1).sum((1, 2)).double() / on1.sum((1, 2)).double()
    # 21. overhead level; 23. mean number of operating firms per sector (period 1)
    stat[:, 20] = phi
    stat[:, 22] = c1["Njt"].mean(1)
    # 27-28. unweighted and employment-weighted markups
    stat[:, 26] = torch.where(on0, mu0, zero).sum((1, 2)) / nop
    stat[:, 27] = wsum(n0, mu0)
    # 49-50. share of job destruction from exit, of job creation from entry
    stat[:, 48] = torch.where(ex, e0, zero).sum((1, 2)) / JD
    stat[:, 49] = torch.where(en, e1, zero).sum((1, 2)) / JC
    # 51-54. cost-weighted markups: COGS, COGS+capital, total cost, COGS+SGA
    stat[:, 50] = wsum(cogs, mu0)
    stat[:, 51] = wsum(cogs + kexp, mu0)
    stat[:, 52] = wsum(cogs + kexp + SGA, mu0)
    stat[:, 53] = wsum(cogs + SGA, mu0)
    return stat


# ----------------------------------------------------------------------------
# 5. solve a batch of points that share M
# ----------------------------------------------------------------------------
def solve_batch(params, M, device="cuda", dtype=torch.float64, c=CONST, draws=None,
                y_method="newton"):
    """params: array [B, 6] = (theta, eta, sigma, zeta, gamma, alpha_COGS); all share M.
    Returns STAT [B,54] (NaN where not computed or invalid), ERR [B,3], rounds [B,2]."""
    dev = torch.device(device)
    q = torch.as_tensor(np.asarray(params, dtype=np.float64), dtype=dtype, device=dev)
    th, et, sg, ze, ga, aC = [q[:, k].clone() for k in range(6)]   # own memory, as after points leave
    pp = dict(th=th[:, None, None], et=et[:, None, None], ga=ga[:, None, None],
              aC=aC[:, None, None], zeta=ze)
    e1, e2 = draws if draws is not None else load_draws(M)
    e1 = torch.as_tensor(e1, dtype=dtype, device=dev).contiguous()[None]   # one memory layout
    e2 = torch.as_tensor(e2, dtype=dtype, device=dev).contiguous()[None]   # for every batch
    rho = c["rho"]
    s3 = sg[:, None, None]
    m = -0.5 * s3 ** 2 / (1.0 + rho)
    logz1 = m / (1.0 - rho) + torch.sqrt(s3 ** 2 / (1.0 - rho ** 2)) * e1
    logz2 = rho * logz1 + m + s3 * e2
    z1 = c["zbar"] * torch.exp(logz1)
    z2 = c["zbar"] * torch.exp(logz2)
    cap1, phi = solve_period(z1, pp, c, None, y_method)
    del z1
    cap2, _ = solve_period(z2, pp, c, phi, y_method)
    stat = moments(cap1, cap2, pp, phi, c)
    valid = (cap1["Y"] > 0) & (cap2["Y"] > 0) & (th <= et) & torch.isfinite(stat[:, 0])
    stat[~valid] = float("nan")
    err = cap2["err"].clone()
    err[th > et] = float("nan")
    rounds = torch.stack([cap1["rounds"], cap2["rounds"]], 1)
    return (stat.cpu().numpy(), err.cpu().numpy(), rounds.cpu().numpy(), valid.cpu().numpy())


def solve_batch_current(x, **kwargs):
    """Use the current qmp contract on this module's compiled batch engine.

    The historical ``solve_batch`` above remains unchanged. The adapter imports
    configuration, parameter/input validation and productivity construction
    from the authoritative ``model/qmp`` package.
    """
    from qmp_torch_current import solve_batch_current as current
    return current(x, **kwargs)
