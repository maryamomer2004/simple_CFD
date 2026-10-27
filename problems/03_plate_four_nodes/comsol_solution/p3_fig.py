"""Figures + COMSOL table for Problem 3 guide."""
import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = r"C:\Users\marya\Downloads\plate_comsol"
N = json.load(open(OUT + r"\p3_numbers.json"))
ex = {int(k): v for k, v in N["exact"].items()}
# COMSOL Point Evaluation table (read from the 4.3a Table window); columns = points
# (1/3,1/3)=node2, (2/3,2/3)=node1, (2/3,1/3)=node3, (1/3,2/3)=node4
hm = ["1/3", "1/6", "1/12", "1/24", "1/48", "1/96"]
tab = np.array([
    [358.81006, 490.92252, 438.45265, 411.19642],
    [359.78585, 490.38364, 438.11403, 411.74231],
    [359.63533, 490.35805, 438.06899, 411.89831],
    [359.64115, 490.36019, 438.07217, 411.92777],
    [359.64074, 490.35922, 438.07183, 411.9282],
    [359.64083, 490.35917, 438.07183, 411.92814]])
node_of_col = [2, 1, 3, 4]
dofs = [65, 221, 805, 3045, 11781, 46325]     # 65 = 1+2F+B for 26 triangles, B=12 (not printed by COMSOL)
cm = {}
for r, h in zip(tab, hm):
    cm[h] = {node_of_col[j]: r[j] for j in range(4)}
cerr = [max(abs(cm[h][n] - ex[n]) for n in range(1, 5)) for h in hm]
print("COMSOL max node error:", cerr)
fd = {int(k): v for k, v in N["study"].items()}
ferr = {n: max(abs(fd[n][str(q)] - ex[q]) for q in range(1, 5)) for n in fd}
print("FDM max node error:", ferr)
json.dump(dict(comsol={h: cm[h] for h in hm}, comsol_err=cerr, dofs=dofs, fdm_err=ferr),
          open(OUT + r"\p3_comsol_table.json", "w"), indent=1)

# ---- plate map ----
fig, ax = plt.subplots(figsize=(5.2, 4.8))
ax.add_patch(Rectangle((0, 0), 1, 1, fc="#fce7f3", ec="none"))
for t in (1/3, 2/3):
    ax.plot([t, t], [0, 1], color="#c58aa8", lw=1)
    ax.plot([0, 1], [t, t], color="#c58aa8", lw=1)
cols = {"top": "#7f1d1d", "bottom": "#ea580c", "left": "#fdba74", "right": "#f97316"}
ax.plot([0, 1], [1, 1], color=cols["top"], lw=6, solid_capstyle="butt")
ax.plot([0, 1], [0, 0], color=cols["bottom"], lw=6, solid_capstyle="butt")
ax.plot([0, 0], [0, 1], color=cols["left"], lw=6, solid_capstyle="butt")
ax.plot([1, 1], [0, 1], color=cols["right"], lw=6, solid_capstyle="butt")
ax.text(0.5, 1.07, "top  700 °C   (COMSOL boundary 3)", ha="center", fontsize=9)
ax.text(0.5, -0.1, "bottom  500 °C   (COMSOL boundary 2)", ha="center", fontsize=9)
ax.text(-0.07, 0.5, "left  100 °C\n(boundary 1)", ha="right", va="center", fontsize=9)
ax.text(1.07, 0.5, "right  400 °C\n(boundary 4)", ha="left", va="center", fontsize=9)
pos = {1: (2/3, 2/3), 2: (1/3, 1/3), 3: (2/3, 1/3), 4: (1/3, 2/3)}
for n, (x, y) in pos.items():
    ax.plot(x, y, "o", color="#111", ms=7)
    dx = 0.035 if n in (1, 3) else -0.035
    ax.text(x + dx, y + 0.045, "T%d" % n, ha="left" if dx > 0 else "right", fontsize=10, fontweight="bold")
    ax.text(x + dx, y - 0.06, "%.1f" % N["direct"][n - 1], ha="left" if dx > 0 else "right", fontsize=8.5, color="#1d4ed8")
ax.text(0.5, 0.5, "", fontsize=1)
ax.set_xlim(-0.55, 1.55); ax.set_ylim(-0.2, 1.17); ax.set_aspect("equal"); ax.axis("off")
ax.text(0.5, -0.17, "blue = finite-difference value (°C)", ha="center", fontsize=8, color="#1d4ed8")
fig.tight_layout()
fig.savefig(OUT + r"\p3_platemap.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.05)
plt.close(fig)

# ---- convergence ----
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
ns = sorted(ferr)
ax[0].loglog([1 / n for n in ns], [ferr[n] for n in ns], "o-", color="tab:orange", lw=2, label="FDM (square grid)")
hh = [1/3, 1/6, 1/12, 1/24, 1/48, 1/96]
ax[0].loglog(hh, cerr, "s-", color="tab:blue", lw=2, label="COMSOL (max element size hm)")
ax[0].loglog([1/24, 1/3], [ferr[24], ferr[24] * 64], "k:", lw=1)
ax[0].text(0.06, 0.45, "slope 2", fontsize=9)
ax[0].set_xlabel("grid spacing / max element size (plate side = 1)")
ax[0].set_ylabel("max error at nodes 1-4 (°C)")
ax[0].set_title("Error at the four points vs exact series")
ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=8)
w = 0.2
labs = ["T1", "T2", "T3", "T4"]
x = np.arange(4)
ax[1].bar(x - w, [N["direct"][i] for i in range(4)], w, label="FDM, 4 unknowns", color="tab:orange")
ax[1].bar(x, [cm["1/3"][i + 1] for i in range(4)], w, label="COMSOL hm = 1/3", color="#93c5fd")
ax[1].bar(x + w, [cm["1/96"][i + 1] for i in range(4)], w, label="COMSOL hm = 1/96", color="tab:blue")
ax[1].plot(x, [ex[i + 1] for i in range(4)], "k_", ms=34, mew=2, label="exact series")
ax[1].set_xticks(x); ax[1].set_xticklabels(labs)
ax[1].set_ylim(340, 540)
ax[1].set_ylabel("temperature (°C)")
ax[1].set_title("The four temperatures")
ax[1].legend(fontsize=8, loc="upper center", ncol=2)
ax[1].grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(OUT + r"\p3_comparison.png", dpi=170)
print("figs saved")
