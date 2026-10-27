import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
OUT = r"C:\Users\marya\Downloads\convdiff_comsol"
N5 = json.load(open(OUT + r"\p5_numbers.json")); CN = json.load(open(OUT + r"\p5_comsol.json")); CS = json.load(open(OUT + r"\p5_comsol_stab.json"))
def ex(x, u): return 1 - (np.exp(u*x/0.1) - 1) / (np.exp(u/0.1) - 1)

# domain diagram
fig, ax = plt.subplots(figsize=(7.2, 2.7))
ax.add_patch(Rectangle((-0.28, -0.3), 0.28, 0.6, fc="#c8452b", ec="#444"))
ax.add_patch(Rectangle((1.0, -0.3), 0.28, 0.6, fc="#fbe7dc", ec="#444"))
ax.add_patch(Rectangle((0, -0.12), 1, 0.24, fc="#e98c6b", ec="none", alpha=.55))
ax.text(-0.14, 0.0, "reservoir\nφ₀ = 1", ha="center", va="center", color="white", fontsize=9)
ax.text(1.14, 0.0, "reservoir\nφL = 0", ha="center", va="center", fontsize=9)
ax.add_patch(FancyArrowPatch((0.15, 0.0), (0.55, 0.0), arrowstyle="-|>", mutation_scale=16, color="#222", lw=1.5))
ax.text(0.35, 0.065, "flow, velocity u", ha="center", fontsize=8.5)
for i in range(6):
    ax.plot(i*0.2, -0.17, "o", color="#2563eb", ms=6)
    ax.text(i*0.2, -0.27, str(i), ha="center", fontsize=8.5)
ax.text(0.5, -0.38, "nodes 0 … 5, Δx = 0.2 m (unknown nodes 1 … 4);  L = 1 m", ha="center", fontsize=8.5)
ax.annotate("", xy=(0, 0.2), xytext=(1, 0.2), arrowprops=dict(arrowstyle="<->", color="#444"))
ax.text(0.5, 0.23, "L = 1 m", ha="center", fontsize=8.5)
ax.set_xlim(-0.35, 1.35); ax.set_ylim(-0.45, 0.35); ax.axis("off")
fig.tight_layout(); fig.savefig(OUT + r"\p5_domain.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=.04); plt.close(fig)

# exact solutions for several u
xx = np.linspace(0, 1, 400)
fig, ax = plt.subplots(figsize=(4.8, 3.3))
for u, col in ((0.1, "#2563eb"), (0.5, "#16a34a"), (1.0, "#f59e0b"), (2.5, "#dc2626")):
    ax.plot(xx, ex(xx, u), color=col, lw=2, label="u = %.1f m/s  (Pe$_L$ = %g)" % (u, u*10))
ax.set_xlabel("x (m)"); ax.set_ylabel("φ"); ax.grid(alpha=.3); ax.legend(fontsize=8); ax.set_title("Exact solution for increasing u", fontsize=10)
fig.tight_layout(); fig.savefig(OUT + r"\p5_exact.png", dpi=200, facecolor="white"); plt.close(fig)

# cases comparison
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2))
for ax, key, u, ttl in ((axs[0], "u0.1", 0.1, "Case 1: u = 0.1 m/s (Pe$_L$ = 1, Pe$_Δ$ = 0.2)"), (axs[1], "u2.5", 2.5, "Case 2: u = 2.5 m/s (Pe$_L$ = 25, Pe$_Δ$ = 5)")):
    d = N5[key]; x = np.array(d["x"])
    ax.plot(xx, ex(xx, u), "k-", lw=1.4, label="exact")
    ax.plot(x, d["CDS"], "o-", color="tab:red", ms=6, lw=1.5, label="central (CDS) = COMSOL, stabilisation off")
    ax.plot(x, d["UDS"], "s-", color="tab:blue", ms=5, lw=1.5, label="upwind (UDS)")
    if key == "u2.5":
        ax.plot(x, CS["1"]["nodes"], "^--", color="tab:green", ms=6, lw=1.3, label="COMSOL, default stabilisation")
    ax.set_title(ttl, fontsize=10); ax.set_xlabel("x (m)"); ax.set_ylabel("φ"); ax.grid(alpha=.3); ax.legend(fontsize=7.5, loc="lower left")
fig.tight_layout(); fig.savefig(OUT + r"\p5_cases.png", dpi=170); plt.close(fig)

# convergence
S = N5["study"]; dxs = np.array(S["dx"])
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.3))
ax = axs[0]
ax.loglog(dxs, S["CDS"], "o-", color="tab:red", lw=2, label="CDS (finite difference)")
ax.loglog(dxs, S["UDS"], "s-", color="tab:blue", lw=2, label="UDS (finite difference)")
ax.loglog(dxs[1:], [CS[str(k)]["maxerr"] for k in range(1, 8)][1:], "^--", color="tab:green", lw=1.5, label="COMSOL, default stabilisation")
ax.loglog(dxs[1:], [CN[str(k)]["maxerr"] for k in range(1, 8)][1:], "x", color="k", ms=8, label="COMSOL, stabilisation off (= CDS)")
ax.loglog(dxs, 0.9*dxs, "k:", lw=1); ax.loglog(dxs, 4.8*dxs**2, "k:", lw=1)
ax.text(0.011, 0.012, "slope 1", fontsize=8); ax.text(0.011, 0.0007, "slope 2", fontsize=8)
ax.axvline(0.08, color="gray", ls="--", lw=1); ax.text(0.085, 2e-4, "Pe$_Δ$ = 2", fontsize=8, color="gray")
ax.set_xlabel("Δx (m)"); ax.set_ylabel("max nodal error"); ax.set_title("Case 3: u = 2.5 m/s, grid refinement", fontsize=10)
ax.grid(alpha=.3, which="both"); ax.legend(fontsize=7.5)
ax = axs[1]
for N_, col in ((5, "tab:red"), (10, "tab:orange"), (20, "tab:green")):
    x = np.linspace(0, 1, N_+1)
    from importlib import util
    import subprocess
ax.plot(xx, ex(xx, 2.5), "k-", lw=1.4, label="exact")
import numpy as _np
def cds(N):
    dx = 1/N; F = 2.5; D = 0.1/dx; aW, aE = D+F/2, D-F/2; aP = aW+aE; n = N-1
    A = _np.diag([aP]*n) - _np.diag([aW]*(n-1), -1) - _np.diag([aE]*(n-1), 1); b = _np.zeros(n); b[0] = aW
    return _np.concatenate([[1], _np.linalg.solve(A, b), [0]])
for N_, col in ((5, "tab:red"), (10, "tab:orange"), (20, "tab:green"), (40, "tab:blue")):
    ax.plot(_np.linspace(0, 1, N_+1), cds(N_), "o-", color=col, ms=4, lw=1.2, label="CDS N=%d (Pe$_Δ$=%.2f)" % (N_, 25/N_))
ax.set_xlabel("x (m)"); ax.set_ylabel("φ"); ax.set_ylim(-0.15, 1.5); ax.grid(alpha=.3); ax.legend(fontsize=7.5, loc="upper left")
ax.set_title("CDS profiles: wiggles disappear when Pe$_Δ$ < 2", fontsize=10)
fig.tight_layout(); fig.savefig(OUT + r"\p5_convergence.png", dpi=170); plt.close(fig)
# wiggle check
for N_ in (5, 10, 12, 13, 20, 40):
    p = cds(N_); print(N_, "Pe_dx=%.2f" % (25/N_), "monotone" if _np.all(_np.diff(p) <= 1e-12) else "OSCILLATES", "range %.3f..%.3f" % (p.min(), p.max()))
print("orders CDS", [round(float(np.log2(S['CDS'][i]/S['CDS'][i+1])), 2) for i in range(6)])
print("orders UDS", [round(float(np.log2(S['UDS'][i]/S['UDS'][i+1])), 2) for i in range(6)])
