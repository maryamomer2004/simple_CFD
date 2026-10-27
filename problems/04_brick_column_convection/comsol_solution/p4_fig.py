import json, re, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT = r"C:\Users\marya\Downloads\brick_comsol"
N = json.load(open(OUT + r"\p4_numbers.json"))
T = N["T"]
def parse(fn):
    rows = []
    for l in open(OUT + "\\" + fn):
        if l.startswith("%") or not l.strip(): continue
        rows.append([float(x) for x in l.split()])
    return np.array(rows)
P = parse("table_points.txt"); Q = parse("table_qrate.txt")
hm = P[:, 0]; pts = P[:, 1:9]; q = Q[:, 1]
dofs = [109, 373, 1401, 5329, 20781]
ref = np.array(N["study"]["256"]["nodes"])
print("COMSOL(1/64) - FDM256:", np.round(pts[-1] - ref, 4))
json.dump(dict(hm=hm.tolist(), pts=pts.tolist(), q=q.tolist(), dofs=dofs), open(OUT + r"\p4_comsol_table.json", "w"), indent=1)

# plate map: nodes, mirror, symmetry
fig, ax = plt.subplots(figsize=(5.4, 5.2))
ax.add_patch(Rectangle((0, 0), 1, 1, fc="#fce7d6", ec="none"))
for t in (.25, .5, .75):
    ax.plot([t, t], [0, 1], color="#d9a78a", lw=1); ax.plot([0, 1], [t, t], color="#d9a78a", lw=1)
for xs, ys in (([0, 1], [1, 1]), ([0, 0], [0, 1]), ([1, 1], [0, 1])):
    ax.plot(xs, ys, color="#c0392b", lw=6, solid_capstyle="butt")
ax.plot([0, 1], [0, 0], color="#2563eb", lw=6, solid_capstyle="butt")
ax.plot([.5, .5], [-.02, 1.02], color="#6d4bd0", ls="-.", lw=1.4)
ax.text(.5, 1.1, "top  500 K   (COMSOL boundary 3)", ha="center", fontsize=9)
ax.text(.5, -.12, "bottom: air, T∞ = 300 K, h = 10   (boundary 2)", ha="center", fontsize=9)
ax.text(-.05, .5, "left 500 K\n(boundary 1)", ha="right", va="center", fontsize=9)
ax.text(1.05, .5, "right 500 K\n(boundary 4)", ha="left", va="center", fontsize=9)
ax.text(.5, 1.04, "symmetry line", ha="center", fontsize=8, color="#6d4bd0")
pos = {1: (.25, .75), 2: (.5, .75), 3: (.25, .5), 4: (.5, .5), 5: (.25, .25), 6: (.5, .25), 7: (.25, 0), 8: (.5, 0)}
for n, (x, y) in pos.items():
    ax.plot(x, y, "o", color="#16a34a" if n >= 7 else "#2563eb", ms=8)
    for xx in ([x, 1 - x] if x < .5 else [x]):
        pass
    ax.text(x - .03, y + .025, str(n), ha="right", fontsize=10, fontweight="bold")
    ax.text(x + .015, y - .06, "%.1f" % T[n - 1], ha="left", fontsize=8, color="#1d4ed8")
    if x < .5:
        ax.plot(1 - x, y, "o", mfc="white", mec="#2563eb" if n < 7 else "#16a34a", ms=8)
        ax.text(1 - x + .03, y + .025, str(n), ha="left", fontsize=9, color="#888")
ax.set_xlim(-.55, 1.55); ax.set_ylim(-.2, 1.2); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout()
fig.savefig(OUT + r"\p4_platemap.png", dpi=200, facecolor="white", bbox_inches="tight", pad_inches=.05)
plt.close(fig)

# convergence
ns = [4, 8, 16, 32, 64, 128, 256]
fq = [N["study"][str(n)]["q"] for n in ns]
f7 = [N["study"][str(n)]["nodes"][6] for n in ns]
qref = 623.4
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
ax[0].loglog([.25 / (n / 4) for n in ns], [abs(v - qref) for v in fq], "o-", color="tab:orange", lw=2, label="FDM (trapezoid rule)")
ax[0].loglog(hm, np.abs(q - qref), "s-", color="tab:blue", lw=2, label="COMSOL (line integral)")
ax[0].set_xlabel("grid spacing / max element size (m)"); ax[0].set_ylabel("|q' - 623.4| (W/m)")
ax[0].set_title("Heat rate to the air: error vs mesh size"); ax[0].grid(alpha=.3, which="both"); ax[0].legend(fontsize=8)
ax[1].semilogx([.25 / (n / 4) for n in ns], f7, "o-", color="tab:orange", lw=2, label="FDM, node 7 (x=0.25, y=0)")
ax[1].semilogx(hm, pts[:, 6], "s-", color="tab:blue", lw=2, label="COMSOL, same point")
ax[1].semilogx([.25 / (n / 4) for n in ns], [N["study"][str(n)]["nodes"][7] for n in ns], "o--", color="tab:red", lw=1.5, label="FDM, node 8 (x=0.5, y=0)")
ax[1].semilogx(hm, pts[:, 7], "s--", color="tab:green", lw=1.5, label="COMSOL, same point")
ax[1].set_xlabel("grid spacing / max element size (m)"); ax[1].set_ylabel("temperature (K)")
ax[1].set_title("Surface temperatures"); ax[1].grid(alpha=.3, which="both"); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT + r"\p4_comparison.png", dpi=170)
print("ok")
