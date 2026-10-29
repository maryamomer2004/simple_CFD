"""Finite difference reference numbers for the COMSOL comparison of Problem 9.

Recomputes, in plain Python, the numbers of the notebook 03_fdm_solver.ipynb that a
COMSOL comparison needs, and writes them to fdm_reference.json next to this script:

* peak, minimum and largest error after one lap on 100 intervals, for both pulses,
  every scheme and C = 0.5, 1.0 and 1.1;
* the node values after one lap (N = 100, C = 0.5) for plotting against COMSOL;
* the error study (Gaussian, C = 0.5, N = 25 ... 1600) with the modified-equation peaks;
* EXPECTATIONS (not COMSOL results) for what COMSOL should give with linear Lagrange elements,
  no stabilisation and a fixed time step: the Galerkin finite element equations
  M du/dt = -A u on the same uniform periodic mesh, marched with implicit Euler (BDF order 1),
  BDF2 and the trapezoidal rule (generalized-alpha with rho_inf = 1 behaves like it).

Usage:  python fdm_reference.py      (runs in a few seconds, no packages needed)
"""

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent          # all paths relative to this folder

L, c, t_lap = 1.0, 1.0, 1.0
x0, sigma, width = 0.5, 0.05, 0.2


def gaussian(xx):
    return math.exp(-(xx - x0)**2 / (2 * sigma**2))


def square(xx):
    return 1.0 if abs(xx - x0) <= width / 2 + 1e-9 else 0.0


PULSES = {"gaussian": gaussian, "square": square}


def u_exact(xx, t, pulse):
    return pulse((xx - c * t) % L)


def step(u, C, scheme):
    N = len(u)
    new = [0.0] * N
    for i in range(N):
        W, P, E = u[i - 1], u[i], u[(i + 1) % N]
        if scheme == "FTCS":
            new[i] = P - C / 2 * (E - W)
        elif scheme == "upwind":
            new[i] = P - C * (P - W)
        else:                                   # Lax-Wendroff
            new[i] = P - C / 2 * (E - W) + C**2 / 2 * (E - 2 * P + W)
    return new


def solve(pulse, scheme, N, C, t_end=t_lap):
    dx = L / N
    n_steps = round(t_end / (C * dx / c))
    x = [i * dx for i in range(N)]
    u = [pulse(xi) for xi in x]
    for _ in range(n_steps):
        u = step(u, C, scheme)
    return x, u, n_steps, n_steps * C * dx / c


def solve_cyclic(sub, diag, sup, r):
    """Solve a cyclic tridiagonal system with constant coefficients (Sherman-Morrison + Thomas)."""
    n = len(r)

    def thomas(a, b, c_, d):
        cp, dp = [0.0] * n, [0.0] * n
        cp[0], dp[0] = c_[0] / b[0], d[0] / b[0]
        for i in range(1, n):
            m = b[i] - a[i] * cp[i - 1]
            cp[i] = c_[i] / m if i < n - 1 else 0.0
            dp[i] = (d[i] - a[i] * dp[i - 1]) / m
        y = [0.0] * n
        y[-1] = dp[-1]
        for i in range(n - 2, -1, -1):
            y[i] = dp[i] - cp[i] * y[i + 1]
        return y

    gamma = -diag
    b = [diag] * n
    b[0] = diag - gamma
    b[-1] = diag - sup * sub / gamma
    a = [sub] * n
    c_ = [sup] * n
    y = thomas(a, b, c_, r)
    uvec = [0.0] * n
    uvec[0], uvec[-1] = gamma, sup          # corner entries: A[0][n-1] = sub, A[n-1][0] = sup
    q = thomas(a, b, c_, uvec)
    vn = sub / gamma
    factor = (y[0] + vn * y[-1]) / (1 + q[0] + vn * q[-1])
    return [y[i] - factor * q[i] for i in range(n)]


def fem_linear(pulse, N, C, method, t_end=t_lap):
    """Galerkin linear elements, M u' = -A u, fixed time step dt = C dx / c (expectation only)."""
    h = L / N
    dt = C * h / c
    n_steps = round(t_end / dt)
    x = [i * h for i in range(N)]
    u = [pulse(xi) for xi in x]

    def mass(v):                             # M v, M = h/6 (1, 4, 1)
        return [h / 6 * (v[i - 1] + 4 * v[i] + v[(i + 1) % N]) for i in range(N)]

    def conv(v):                             # A v, A = c/2 (-1, 0, 1)
        return [c / 2 * (v[(i + 1) % N] - v[i - 1]) for i in range(N)]

    u_old = None
    for n in range(n_steps):
        if method == "implicit Euler" or (method == "BDF2" and u_old is None):
            k, rhs = dt, mass(u)                                  # (M + dt A) u_new = M u
            sub, diag, sup = h / 6 - k * c / 2, 4 * h / 6, h / 6 + k * c / 2
        elif method == "BDF2":                                    # (3/2 M + dt A) u_new = M (2u - u_old/2)
            rhs = mass([2 * u[i] - 0.5 * u_old[i] for i in range(N)])
            sub, diag, sup = 1.5 * h / 6 - dt * c / 2, 1.5 * 4 * h / 6, 1.5 * h / 6 + dt * c / 2
        else:                                                     # trapezoidal rule
            Mu, Au = mass(u), conv(u)
            rhs = [Mu[i] - dt / 2 * Au[i] for i in range(N)]
            sub, diag, sup = h / 6 - dt * c / 4, 4 * h / 6, h / 6 + dt * c / 4
        u_old, u = u, solve_cyclic(sub, diag, sup, rhs)
    return x, u, n_steps * dt


def summary(name, scheme, N, C):
    x, u, n, t = solve(PULSES[name], scheme, N, C)
    err = max(abs(u[i] - u_exact(x[i], t, PULSES[name])) for i in range(N))
    return {"pulse": name, "scheme": scheme, "N": N, "C": C, "dt": C * (L / N) / c, "steps": n,
            "t_end": round(t, 12), "peak": max(u), "min": min(u), "max_error": err,
            "amount": sum(u) * L / N}


def main():
    ref = {"description": "FDM reference for Problem 9 (advection of a pulse), from fdm_reference.py; "
                          "same numbers as 03_fdm_solver.ipynb",
           "data": {"L_m": L, "c_m_per_s": c, "t_lap_s": t_lap, "x0_m": x0, "sigma_m": sigma,
                    "square_from_m": x0 - width / 2, "square_to_m": x0 + width / 2,
                    "gaussian_area": sigma * math.sqrt(2 * math.pi)},
           "exact_after_one_lap": {"peak": 1.0, "min": 0.0,
                                   "amount_gaussian": sigma * math.sqrt(2 * math.pi),
                                   "amount_square": width}}

    runs = []
    for C in (0.5, 1.0, 1.1):
        for scheme in ("FTCS", "upwind", "Lax-Wendroff"):
            for name in PULSES:
                runs.append(summary(name, scheme, 100, C))
    ref["one_lap_N100"] = runs

    profiles = {}
    for name, pulse in PULSES.items():
        x, u_up, _, _ = solve(pulse, "upwind", 100, 0.5)
        _, u_lw, _, _ = solve(pulse, "Lax-Wendroff", 100, 0.5)
        profiles[name] = {"x": x, "exact": [u_exact(xi, t_lap, pulse) for xi in x],
                          "upwind": u_up, "Lax-Wendroff": u_lw}
    ref["profiles_N100_C0.5_t1"] = profiles

    study = []
    for N in (25, 50, 100, 200, 400, 800, 1600):
        D_num = c * (L / N) / 2 * (1 - 0.5)
        row = {"N": N, "dx": L / N, "dt": 0.5 * (L / N) / c, "steps": round(N / 0.5),
               "D_num_upwind": D_num,
               "upwind_peak_predicted": sigma / math.sqrt(sigma**2 + 2 * D_num * t_lap)}
        for scheme in ("upwind", "Lax-Wendroff"):
            s = summary("gaussian", scheme, N, 0.5)
            row[f"{scheme}_peak"] = s["peak"]
            row[f"{scheme}_max_error"] = s["max_error"]
        study.append(row)
    ref["error_study_gaussian_C0.5"] = study

    fem = []
    for N, C in ((100, 0.5), (100, 1.0), (200, 0.5)):
        for method in ("implicit Euler", "BDF2", "trapezoidal"):
            for name, pulse in PULSES.items():
                x, u, t = fem_linear(pulse, N, C, method)
                err = max(abs(u[i] - u_exact(x[i], t, pulse)) for i in range(N))
                fem.append({"pulse": name, "time stepping": method, "N": N, "C": C,
                            "dt": C * (L / N) / c, "peak": max(u), "min": min(u), "max_error": err})
    ref["EXPECTED_fem_linear_no_stabilisation"] = {
        "note": "NOT COMSOL results: plain-Python Galerkin linear elements without stabilisation, "
                "fixed time step, to check COMSOL's numbers against. COMSOL's BDF is variable order "
                "(1 to 5) and adaptive, so it will only be close to these when its steps are forced.",
        "runs": fem}

    out = HERE / "fdm_reference.json"
    out.write_text(json.dumps(ref, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    for r in runs:
        if r["N"] == 100 and r["scheme"] != "FTCS":
            print(f"C = {r['C']:3.1f}  {r['scheme']:12s} {r['pulse']:8s}  peak {r['peak']:10.4g}"
                  f"  min {r['min']:10.4g}  max error {r['max_error']:9.3g}")
    for r in fem:
        print(f"EXPECTED FEM N = {r['N']} C = {r['C']:3.1f}  {r['time stepping']:14s} {r['pulse']:8s}"
              f"  peak {r['peak']:7.4f}  min {r['min']:8.4f}  max error {r['max_error']:7.4f}")


if __name__ == "__main__":
    main()
