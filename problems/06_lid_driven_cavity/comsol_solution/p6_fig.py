import json, numpy as np
import matplotlib, matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.interpolate import CubicSpline
from p6_solver import *

num = json.load(open("p6_numbers.json")); cnum = json.load(open("p6_comsol_numbers.json"))
F = np.load("p6_comsol_fields.npz")
NAVY = "#17356b"; RED = "#c62828"; GRN = "#2e7d32"; ORG = "#ef6c00"
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3})

# --- A. domain sketch
fig, ax = plt.subplots(figsize=(4.6, 4.2))
ax.grid(False)
ax.add_patch(Rectangle((0, 0), 1, 1, fc="#eef3fb", ec=NAVY, lw=2))
ax.add_patch(Rectangle((-0.02, 1.0), 1.04, 0.045, fc="#9aa7bd", ec=NAVY))
ax.annotate("", xy=(0.9, 1.14), xytext=(0.1, 1.14), arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.5))
ax.text(0.5, 1.18, "lid: u = U = 1 m/s, v = 0", ha="center", color=RED, fontsize=10, fontweight="bold")
# clockwise circular arrow
ang = np.linspace(np.pi * 0.9, -np.pi * 0.9, 100)
cx, cy, r = 0.5, 0.52, 0.26
ax.plot(cx + r * np.cos(ang), cy + r * np.sin(ang), color=NAVY, lw=2)
ax.annotate("", xy=(cx + r * np.cos(ang[-1]), cy + r * np.sin(ang[-1])), xytext=(cx + r * np.cos(ang[-6]), cy + r * np.sin(ang[-6])),
            arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))
ax.text(0.5, 0.5, "clockwise\nvortex", ha="center", va="center", color=NAVY, fontsize=9)
ax.text(-0.04, 0.5, "u = v = 0", ha="right", va="center", fontsize=9, rotation=90)
ax.text(1.04, 0.5, "u = v = 0", ha="left", va="center", fontsize=9, rotation=90)
ax.text(0.5, -0.07, "u = v = 0", ha="center", va="top", fontsize=9)
ax.text(0.5, -0.17, "L = 1 m, nu = 0.01 m$^2$/s, Re = UL/nu = 100", ha="center", fontsize=9.5)
ax.set_xlim(-0.2, 1.2); ax.set_ylim(-0.25, 1.28); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(); fig.savefig("p6_domain.png", dpi=200); plt.close(fig)

# --- A2. 4x4 grid for hand calculation
fig, ax = plt.subplots(figsize=(4.2, 4.2))
ax.grid(False)
h = 0.25
for k in range(5):
    ax.plot([0, 1], [k * h, k * h], color="#9aa7bd", lw=1); ax.plot([k * h, k * h], [0, 1], color="#9aa7bd", lw=1)
for i in range(5):
    for j in range(5):
        interior = 0 < i < 4 and 0 < j < 4
        ax.plot(i * h, j * h, "o", ms=11 if interior else 7, color=NAVY if interior else "#9aa7bd", zorder=3)
        if interior:
            ax.text(i * h + 0.03, j * h + 0.035, "(%d,%d)" % (i, j), fontsize=8.5, color=RED)
ax.plot([0, 1], [1, 1], color=RED, lw=4)
ax.text(0.5, 1.07, "lid: omega = -2U/h = -8 (psi = 0)", ha="center", color=RED, fontsize=9)
ax.text(0.5, -0.1, "psi = 0, omega = -2 psi$_1$/h$^2$", ha="center", fontsize=9)
ax.set_xlim(-0.12, 1.12); ax.set_ylim(-0.18, 1.15); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout(); fig.savefig("p6_grid4.png", dpi=200); plt.close(fig)

# --- B. streamlines and vorticity, N=32 FDM
N = 32; psi = np.load("p6_psi_32.npy"); w = np.load("p6_w_32.npy")
xs = np.linspace(0, 1, N + 1); X, Y = np.meshgrid(xs, xs, indexing="ij")
fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.7))
lev = np.sort(np.unique(np.concatenate([np.linspace(psi.min(), 0, 16)[:-1], [-3e-4, -1e-4, -1e-5]])))
ax[0].contour(X, Y, psi, levels=lev, cmap="viridis")
cc = centre(psi, N)
ax[0].plot(cc[0], cc[1], "r+", ms=12, mew=2, label="centre (FDM 32x32): %.3f, %.3f" % (cc[0], cc[1]))
ax[0].plot(GHIA_XC, GHIA_YC, "kx", ms=9, mew=1.6, label="Ghia: 0.6172, 0.7344")
ax[0].set_title("Streamlines (contours of $\\psi$), FDM 32$\\times$32")
ax[0].legend(loc="lower left", fontsize=8); ax[0].set_aspect("equal"); ax[0].set_xlabel("x (m)"); ax[0].set_ylabel("y (m)")
wl = [-5, -4, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 3, 4, 5]
cf = ax[1].contourf(X, Y, np.clip(w, -12, 8), levels=np.linspace(-12, 8, 21), cmap="RdBu_r", extend="both")
ax[1].contour(X, Y, w, levels=wl, colors="k", linewidths=0.5)
fig.colorbar(cf, ax=ax[1], shrink=0.82, label="$\\omega$ (1/s), clipped to [-12, 8]")
ax[1].set_title("Vorticity $\\omega$, FDM 32$\\times$32"); ax[1].set_aspect("equal"); ax[1].set_xlabel("x (m)")
fig.tight_layout(); fig.savefig("p6_flow.png", dpi=190); plt.close(fig)

# --- C. centrelines
fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.5))
yy = np.linspace(0, 1, 400)
u, v = velocities(psi, N)
ax[0].plot(CubicSpline(xs, u[N // 2])(yy), yy, color=NAVY, lw=2, label="FDM 32$\\times$32")
ax[0].plot(CubicSpline(xs, F["u32"][N // 2])(yy), yy, color=GRN, lw=2, ls="--", label="COMSOL 32$\\times$32")
p128 = np.load("p6_psi_128.npy"); u128, v128 = velocities(p128, 128); x128 = np.linspace(0, 1, 129)
ax[0].plot(CubicSpline(x128, u128[64])(yy), yy, color="gray", lw=1, label="FDM 128$\\times$128")
ax[0].plot(GHIA_U, GHIA_Y, "o", color=RED, ms=5, label="Ghia et al. (1982)")
ax[0].set_xlabel("u (m/s) along x = 0.5"); ax[0].set_ylabel("y (m)"); ax[0].legend(fontsize=8, loc="upper left")
ax[1].plot(xs, v[:, N // 2], color=NAVY, lw=2, label="FDM 32$\\times$32")
ax[1].plot(xs, F["v32"][:, N // 2], color=GRN, lw=2, ls="--", label="COMSOL 32$\\times$32")
ax[1].plot(x128, v128[:, 64], color="gray", lw=1, label="FDM 128$\\times$128")
ax[1].plot(GHIA_X, GHIA_V, "o", color=RED, ms=5, label="Ghia et al. (1982)")
ax[1].set_xlabel("x (m)"); ax[1].set_ylabel("v (m/s) along y = 0.5"); ax[1].legend(fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig("p6_centrelines.png", dpi=190); plt.close(fig)

# --- D. convergence
Ns = np.array([4, 8, 16, 32, 64, 128])
g = num["grid"]
pf = np.array([g[str(n)]["psi_min"] for n in Ns]); pc = np.array([cnum["res"][str(n)]["psi_min"] for n in Ns])
ru_f = np.array([g[str(n)]["rms_u"] for n in Ns]); ru_c = np.array([cnum["res"][str(n)]["rms_u"] for n in Ns])
fig, ax = plt.subplots(1, 3, figsize=(11.6, 4.0))
ax[0].plot(Ns, pf, "o-", color=NAVY, label="FDM"); ax[0].plot(Ns, pc, "s--", color=GRN, label="COMSOL")
ax[0].axhline(GHIA_PSI, color=RED, lw=1.2, label="Ghia  -0.103423")
ax[0].set_xscale("log", base=2); ax[0].set_xlabel("intervals per side N"); ax[0].set_ylabel("$\\psi_{min}$ (primary vortex)"); ax[0].legend(fontsize=8)
ef, ec = [], []
for n in [4, 8, 16, 32, 64]:
    s = 128 // n
    ef.append(np.abs(np.load("p6_psi_%d.npy" % n) - np.load("p6_psi_128.npy")[::s, ::s]).max())
    ec.append(np.abs(F["psi%d" % n] - F["psi128"][::s, ::s]).max())
hh = 1.0 / np.array([4, 8, 16, 32, 64])
ax[1].loglog(hh, ef, "o-", color=NAVY, label="FDM"); ax[1].loglog(hh, ec, "s--", color=GRN, label="COMSOL")
ax[1].loglog(hh, 0.85 * hh**2, "k:", label="slope 2"); ax[1].loglog(hh, 0.2 * hh, "k-.", lw=0.8, label="slope 1")
ax[1].set_xlabel("h = 1/N (m)"); ax[1].set_ylabel("max |$\\psi_h - \\psi_{h=1/128}$| at nodes"); ax[1].legend(fontsize=8)
ax[2].loglog(1.0 / Ns, ru_f, "o-", color=NAVY, label="FDM"); ax[2].loglog(1.0 / Ns, ru_c, "s--", color=GRN, label="COMSOL")
ax[2].set_xlabel("h = 1/N (m)"); ax[2].set_ylabel("rms error of u(0.5, y) against Ghia"); ax[2].legend(fontsize=8)
for a_ in ax[1:]:
    a_.tick_params(which="minor", labelbottom=False, labelleft=False)
    a_.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); a_.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
fig.tight_layout(); fig.savefig("p6_convergence.png", dpi=190); plt.close(fig)
print("self-conv FDM", ef, "COMSOL", ec)
json.dump(dict(ef=[float(x) for x in ef], ec=[float(x) for x in ec]), open("p6_selfconv.json", "w"))

# --- E. corner eddies N=128
p = np.load("p6_psi_128.npy"); X, Y = np.meshgrid(x128, x128, indexing="ij")
fig, ax = plt.subplots(1, 2, figsize=(10.0, 4.2))
for a, (x0, x1, y0, y1), ttl, lv in ((ax[0], (0.55, 1, 0, 0.45), "bottom-right corner eddy", [2e-6, 5e-6, 8e-6, 1.1e-5, 1.25e-5]),
                                     (ax[1], (0, 0.45, 0, 0.45), "bottom-left corner eddy", [1e-7, 5e-7, 1e-6, 1.5e-6, 1.9e-6])):
    a.contour(X, Y, p, levels=[-1e-3, -1e-4, -1e-5, -1e-6], colors="#7e8aa0", linewidths=0.8, linestyles="--")
    a.contour(X, Y, p, levels=lv, colors=RED, linewidths=1.5)
    a.set_xlim(x0, x1); a.set_ylim(y0, y1); a.set_aspect("equal"); a.set_title(ttl + " (FDM 128$\\times$128)", fontsize=10); a.set_xlabel("x (m)")
    a.text(0.5 * (x0 + x1), y1 - 0.03, "red: $\\psi>0$ (counter-clockwise)", ha="center", fontsize=8, color=RED)
fig.tight_layout(); fig.savefig("p6_corners.png", dpi=190); plt.close(fig)

# --- F. spin-up / convergence history
hist = np.load("p6_hist32.npy")
fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9))
ax[0].semilogy(np.arange(1, len(hist) + 1), hist, color=NAVY); ax[0].axhline(1e-8, color=RED, lw=1)
ax[0].set_xlabel("iteration"); ax[0].set_ylabel("largest change of $\\omega$ or $\\psi$ in one sweep"); ax[0].set_title("Convergence history, 32$\\times$32")
sp = np.array(num["spin"]); ax[1].semilogx(sp[:, 0], sp[:, 1], "o-", color=NAVY)
ax[1].axhline(g["32"]["psi_min"], color="gray", lw=1)
ax[1].set_xlabel("iteration"); ax[1].set_ylabel("$\\psi_{min}$"); ax[1].set_title("Spin-up from rest: the vortex overshoots, then settles")
fig.tight_layout(); fig.savefig("p6_spinup.png", dpi=190); plt.close(fig)

# --- G. N=4 converged values for the hand page
psi4, w4, it4, h4 = run(4, 1.0, 1.0, 1e-8, 1000)
json.dump(dict(psi4=psi4.tolist(), w4=w4.tolist(), it4=int(it4)), open("p6_n4.json", "w"))
print(np.round(psi4.T[::-1], 5)); print(np.round(w4.T[::-1], 3), it4)
