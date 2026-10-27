"""Drawing helpers for Problem 2 (phosphorus diffusion into silicon).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging
import math
import random

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.ticker import NullFormatter

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # quiet font fallback notes

BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#d03b3b"
INK, INK2, MUTED, GRID, SURFACE = "#1f2328", "#59636e", "#818b98", "#d8dee4", "#f6f8fa"
HEAT = LinearSegmentedColormap.from_list(
    "heat", ["#fff4eb", "#fdd5b5", "#f7a26f", "#eb6834", "#c0441a", "#7a2a0e"])
STEPS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "figure.facecolor": "white",
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 10, "mathtext.fontset": "cm",
    "axes.edgecolor": "#afb8c1", "axes.labelcolor": INK2, "axes.titlesize": 11,
    "axes.titleweight": "semibold", "axes.titlelocation": "left", "axes.titlecolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": "#afb8c1", "ytick.color": "#afb8c1",
    "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "legend.frameon": False, "axes.grid": False,
})


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def schematic(c_As, D_cm2, T_C):
    """The CVD-coated wafer: P-rich source layer on top, silicon sink below, z pointing down."""
    fig = plt.figure(figsize=(7.4, 3.5))
    ax = fig.add_axes([0.02, 0.02, 0.6, 0.96])
    ax.set_xlim(-0.2, 1.08)
    ax.set_ylim(-1.0, 0.62)
    ax.axis("off")
    rng = random.Random(4)
    # gas phase
    ax.text(0.5, 0.55, r"POCl$_3$ vapour (CVD reactor, " f"{T_C:g} °C)", ha="center", va="center",
            fontsize=9.5, color=INK2)
    for xx in (0.15, 0.35, 0.55, 0.75):
        _arrow(ax, (xx, 0.48), (xx, 0.3), color=MUTED, lw=1.1, scale=9)
    # P-rich SiO2 coating: the source
    ax.add_patch(Rectangle((0, 0), 1, 0.24, fc="#c9ced6", ec=INK2, lw=1.0))
    for _ in range(70):
        ax.plot(rng.uniform(0.02, 0.98), rng.uniform(0.02, 0.22), "o", ms=2.2, color=INK, lw=0)
    ax.text(0.5, 0.12, r"P-rich SiO$_2$ coating  (source)", ha="center", va="center", fontsize=9.5,
            fontweight="semibold", bbox=dict(boxstyle="round,pad=0.2", fc="#c9ced6", ec="none"))
    # silicon wafer: the sink, dots thinning out with depth
    ax.add_patch(Rectangle((0, -0.92), 1, 0.92, fc="#e3eefc", ec=INK2, lw=1.0))
    for _ in range(260):
        zz = -abs(rng.gauss(0, 0.16))
        if zz > -0.9:
            ax.plot(rng.uniform(0.02, 0.98), zz, "o", ms=1.8, color=BLUE, lw=0)
    ax.text(0.5, -0.62, "crystalline Si wafer  (sink)\ninitially free of P", ha="center", va="center",
            fontsize=9.5, bbox=dict(boxstyle="round,pad=0.25", fc="#e3eefc", ec="none"))
    for xx in (0.2, 0.8):
        _arrow(ax, (xx, -0.03), (xx, -0.3), color=BLUE, lw=1.6, scale=11)
    ax.text(0.5, -0.2, "P diffuses in", ha="center", fontsize=8.5, color=INK2,
            bbox=dict(boxstyle="round,pad=0.2", fc="#e3eefc", ec="none"))
    # z axis
    _arrow(ax, (-0.08, 0.0), (-0.08, -0.88), color=INK, lw=1.2, scale=10)
    ax.plot([-0.12, 0.0], [0, 0], color=INK, lw=1.0)
    ax.text(-0.13, 0.0, "z = 0", ha="right", va="center", fontsize=9)
    ax.text(-0.11, -0.86, "z", ha="right", va="center", fontsize=10.5, style="italic")
    ax.text(1.02, 0.0, r"$c_A = c_{As}$", ha="left", va="center", fontsize=9.5)
    ax.text(1.02, -0.86, r"$c_A \to 0$" "\n" r"as $z \to \infty$", ha="left", va="center", fontsize=9)

    # qualitative concentration profile (sketch only)
    ax2 = fig.add_axes([0.73, 0.14, 0.24, 0.72])
    zz = [0.03 * j for j in range(101)]
    ax2.plot([math.erfc(v / 1.2) for v in zz], zz, color=ORANGE, lw=2)
    ax2.set_ylim(3, 0)
    ax2.set_xlim(0, 1.05)
    ax2.set_xticks([0, 1], ["0", r"$c_{As}$"])
    ax2.set_yticks([0], ["0"])
    ax2.set_ylabel("depth z", labelpad=2)
    ax2.set_title("expected profile", fontsize=9.5)
    ax2.xaxis.set_ticks_position("top")
    ax2.spines["top"].set_visible(True)
    ax2.spines["bottom"].set_visible(False)
    ax2.text(0.5, 2.6, f"$D_{{AB}}$ = {D_cm2:.1e} cm²/s".replace("e-13", r"$\times$10$^{-13}$"),
             ha="center", fontsize=8, color=INK2)
    plt.show()


def grid(N):
    """The space-time grid and the explicit (FTCS) stencil."""
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.12, top=0.95)
    ax.axis("off")
    cols = list(range(9)) + [10, 11]          # draw i = 0..8, a gap, then N-1, N
    labels = [str(i) for i in range(9)] + [f"{N - 1}", f"{N}"]
    rows = range(4)
    for n in rows:
        ax.plot([0, 8.4], [n, n], color=GRID, lw=1, zorder=1)
        ax.plot([9.6, 11], [n, n], color=GRID, lw=1, zorder=1)
        ax.text(9.0, n, "…", ha="center", va="center", color=MUTED)
        for c, lab in zip(cols, labels):
            color = ORANGE if c == 0 else (VIOLET if c == 11 else "white")
            ec = ORANGE if c == 0 else (VIOLET if c == 11 else MUTED)
            ax.scatter(c, n, s=34, fc=color, ec=ec, lw=1.1, zorder=3)
    for c in cols:
        ax.plot([c, c], [0, 3], color=GRID, lw=0.7, zorder=0)
    ax.scatter(range(1, 9), [0] * 8, s=34, color=BLUE, ec="white", lw=1, zorder=4)   # initial condition
    # stencil: (i-1, i, i+1) at level n -> i at level n+1
    for c in (3, 4, 5):
        ax.scatter(c, 1, s=70, color=BLUE, ec="white", lw=1.4, zorder=5)
        ax.add_patch(FancyArrowPatch((c, 1), (4, 2), arrowstyle="-|>", mutation_scale=10, color=INK2,
                                     lw=1.1, shrinkA=6, shrinkB=7, zorder=4))
    ax.scatter(4, 2, s=80, color=AQUA, ec="white", lw=1.4, zorder=5)
    for c, lab in zip(cols, labels):
        ax.text(c, -0.42, lab, ha="center", va="center", fontsize=8.5)
    ax.text(-0.6, -0.42, "i =", ha="right", va="center", fontsize=8.5, color=INK2)
    for n, lab in zip(rows, ["n = 0", "n", "n + 1", "…"]):
        ax.text(-0.6, n, lab, ha="right", va="center", fontsize=8.5, color=INK2)
    ax.text(0, 3.45, "surface\nC = 1", ha="center", va="center", fontsize=8, color=ORANGE)
    ax.text(11, 3.45, r"$z_{max}$" "\nC = 0", ha="center", va="center", fontsize=8, color=VIOLET)
    ax.text(4.25, 2.5, "new value from three old ones", fontsize=8.5, color=INK, va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
    ax.text(5.6, 0.3, "initial condition C = 0", fontsize=8.5, color=INK2, va="center")
    _arrow(ax, (-1.5, 0.3), (-1.5, 2.7), color=INK2, lw=1, scale=9)
    ax.text(-1.75, 1.5, "time", rotation=90, ha="center", va="center", fontsize=8.5, color=INK2)
    _arrow(ax, (1.0, -0.85), (7.0, -0.85), color=INK2, lw=1, scale=9)
    ax.text(7.2, -0.85, "depth z", va="center", fontsize=8.5, color=INK2)
    ax.set_xlim(-2.0, 11.6)
    ax.set_ylim(-1.05, 3.8)
    plt.show()


def profiles(z, snapshots, C_exact):
    """Concentration profiles at several times, FDM (dots) and exact (lines)."""
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.15, top=0.9)
    colors = STEPS[-len(snapshots):]
    zz = [z[-1] * j / 400 for j in range(401)]
    for color, (t, C) in zip(colors, snapshots.items()):
        if t > 0:
            ax.plot(zz, [C_exact(v, t) for v in zz], color=color, lw=1.4, zorder=2)
        ax.plot(z, C, "o", ms=3.6, color=color, mec="white", mew=0.6, zorder=3,
                label=f"t = {t / 60:g} min")
    ax.set_xlim(0, 3)
    ax.set_ylim(-0.02, 1.04)
    ax.set_xlabel("depth z [µm]")
    ax.set_ylabel(r"$C = c_A / c_{As}$")
    ax.set_title("Phosphorus moving into the wafer (dots: FDM, lines: exact)")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right")
    plt.show()


def compare(z, C, C_exact, t_end, c_As, target, depth_fdm):
    """FDM against the exact solution after 1 h, on linear and logarithmic scales."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.88, wspace=0.3)
    zz = [z[-1] * j / 500 for j in range(501)]
    exact = [C_exact(v, t_end) for v in zz]
    ax1.plot(zz, exact, color=INK, lw=1.6, label="exact (erfc)")
    ax1.plot(z, C, "o", ms=4.5, color=ORANGE, mec="white", mew=0.8, label="FDM")
    ax1.set_xlim(0, 3)
    ax1.set_xlabel("depth z [µm]")
    ax1.set_ylabel(r"$c_A / c_{As}$")
    ax1.set_title("After 1 h, linear scale")
    ax1.grid(axis="y", color=GRID, lw=0.6)
    ax1.legend(loc="upper right")
    keep = [k for k, v in enumerate(exact) if v > 1e-9]
    ax2.semilogy([zz[k] for k in keep], [c_As * exact[k] for k in keep], color=INK, lw=1.6)
    pts = [(zi, ci) for zi, ci in zip(z, C) if ci > 1e-9]
    ax2.semilogy([p[0] for p in pts], [c_As * p[1] for p in pts], "o", ms=4.5, color=ORANGE, mec="white",
                 mew=0.8)
    ax2.axhline(target * c_As, color=MUTED, lw=1)
    ax2.plot([depth_fdm, depth_fdm], [1e11, target * c_As], color=BLUE, lw=1.4)
    ax2.text(3.45, target * c_As * 1.8, "1 % of the surface value", ha="right", fontsize=8.5, color=INK2)
    ax2.text(depth_fdm + 0.05, 1e13, f"film depth\n≈ {depth_fdm:.2f} µm", fontsize=8.5, color=BLUE)
    ax2.set_xlim(0, 3.5)
    ax2.set_ylim(1e11, 1e21)
    ax2.set_xlabel("depth z [µm]")
    ax2.set_ylabel(r"$c_A$  [atoms P / cm³]")
    ax2.set_title("After 1 h, logarithmic scale")
    ax2.grid(axis="y", color=GRID, lw=0.6)
    plt.show()


def depth_vs_time(times, depths, exact_depth):
    """Penetration depth of the 1 % level versus time: it grows like the square root of t."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.88, wspace=0.3)
    tt = [times[-1] * j / 300 for j in range(1, 301)]
    ax1.plot([t / 60 for t in tt], [exact_depth(t) for t in tt], color=INK, lw=1.6, label="exact")
    every = max(1, len(times) // 25)
    ax1.plot([t / 60 for t in times[::every]], depths[::every], "o", ms=4, color=ORANGE, mec="white",
             mew=0.7, label="FDM")
    ax1.set_xlabel("time [min]")
    ax1.set_ylabel("film depth [µm]")
    ax1.set_title("Depth of the 1 % level")
    ax1.set_xlim(0, times[-1] / 60)
    ax1.set_ylim(0, None)
    ax1.grid(axis="y", color=GRID, lw=0.6)
    ax1.legend(loc="lower right")
    ax2.plot([math.sqrt(t) for t in tt], [exact_depth(t) for t in tt], color=INK, lw=1.6)
    ax2.plot([math.sqrt(t) for t in times[::every]], depths[::every], "o", ms=4, color=ORANGE,
             mec="white", mew=0.7)
    ax2.set_xlabel(r"$\sqrt{t}$  [s$^{1/2}$]")
    ax2.set_ylabel("film depth [µm]")
    ax2.set_title(r"Same data against $\sqrt{t}$: a straight line")
    ax2.set_xlim(0, math.sqrt(times[-1]))
    ax2.set_ylim(0, None)
    ax2.grid(axis="y", color=GRID, lw=0.6)
    plt.show()


def convergence(dzs, errors):
    """Grid-refinement study at fixed r: error versus grid spacing on log-log axes."""
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    fig.subplots_adjust(left=0.15, right=0.96, bottom=0.16, top=0.88)
    ax.loglog(dzs, errors, color=BLUE, lw=1.8, marker="o", ms=6, mec="white", label="largest error of FDM")
    ref = [errors[0] * (v / dzs[0]) ** 2 * 0.5 for v in dzs]
    ax.loglog(dzs, ref, color=MUTED, lw=1.1, label=r"slope 2  ($\propto\Delta z^2$)")
    ax.set_xticks(dzs, [f"{v:g}" for v in dzs])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel(r"grid spacing $\Delta z$ [µm]   (with $\Delta t \propto \Delta z^2$)")
    ax.set_ylabel(r"largest error in $c_A/c_{As}$")
    ax.set_title("Verification: halve Δz, error ÷ 4")
    ax.grid(color=GRID, lw=0.6, which="major")
    ax.legend(loc="upper left")
    plt.show()


def unstable(z, snapshots, r):
    """What happens when the time step breaks the stability limit."""
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.16, top=0.88)
    colors = STEPS[-len(snapshots):]
    for color, (n, C) in zip(colors, snapshots.items()):
        ax.plot(z, C, color=color, lw=1.6, marker="o", ms=2.5, label=f"after {n} steps")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(-1.5, 2.5)
    ax.axhspan(0, 1, color=AQUA, alpha=0.08, lw=0)
    ax.text(2.45, 0.5, "physically possible\nrange 0 ≤ C ≤ 1", ha="right", va="center", fontsize=8.5,
            color=INK2)
    ax.set_xlabel("depth z [µm]")
    ax.set_ylabel(r"$C = c_A / c_{As}$")
    ax.set_title(f"r = {r}: the explicit scheme is unstable")
    ax.legend(loc="upper right", fontsize=8.5)
    plt.show()
