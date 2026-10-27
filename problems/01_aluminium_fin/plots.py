"""Drawing helpers for Problem 1 (the aluminium pin fin).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
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


def schematic(L, d, T_b, T_inf, h):
    """The fin, its base, the insulated tip and the surrounding air."""
    fig = plt.figure(figsize=(7.2, 2.9))
    ax = fig.add_axes([0.02, 0.02, 0.70, 0.96])
    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(-0.42, 0.42)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((-0.06, -0.32), 0.06, 0.64, color=RED, lw=0))          # hot base
    ax.add_patch(Rectangle((0, -0.06), 1, 0.12, fc="#b7d3f6", ec=INK2, lw=1.2))   # the fin
    ax.add_patch(Rectangle((1.0, -0.09), 0.035, 0.18, hatch="////", fc="white", ec=INK2, lw=0.8))
    ax.text(-0.09, 0.0, f"$T_b$ = {T_b:g} °C", ha="right", va="center", fontsize=10)
    ax.text(1.05, 0.13, "insulated\ntip", ha="left", va="bottom", fontsize=9, color=INK2)
    for xx in (0.2, 0.45, 0.7):
        _arrow(ax, (xx, 0.07), (xx + 0.06, 0.2), color=BLUE)
        _arrow(ax, (xx, -0.07), (xx + 0.06, -0.2), color=BLUE)
    ax.text(0.5, 0.29, f"air:  $T_\\infty$ = {T_inf:g} °C,   $h$ = {h:g} W/m²K",
            ha="center", va="center", fontsize=9.5)
    ax.text(0.5, -0.26, "heat is lost by convection all along the fin", ha="center", fontsize=8.5,
            color=INK2)
    _arrow(ax, (0, -0.36), (1, -0.36), style="<->", lw=1.0, scale=8)
    ax.text(0.5, -0.4, f"$L$ = {L * 100:g} cm", ha="center", va="top", fontsize=9.5)
    ax.text(0.03, 0.0, "x = 0", fontsize=8, va="center", color=INK2)
    # cross-section
    ax2 = fig.add_axes([0.74, 0.25, 0.22, 0.5])
    ax2.set_xlim(-1.6, 1.6)
    ax2.set_ylim(-1.6, 1.6)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.add_patch(Circle((0, 0), 1, fc="#b7d3f6", ec=INK2, lw=1.2))
    _arrow(ax2, (-1, 0), (1, 0), style="<->", lw=1.0, scale=8)
    ax2.text(0, 1.15, f"$d$ = {d * 1000:g} mm", ha="center", va="bottom", fontsize=9.5)
    ax2.text(0, -1.45, "cross-section", ha="center", fontsize=8.5, color=INK2)
    plt.show()


def grid(x, N):
    """Nodes of the 1D grid, including the ghost node used at the insulated tip."""
    fig, ax = plt.subplots(figsize=(7.2, 1.9))
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.05, top=0.95)
    ax.axis("off")
    L, dx = x[-1], x[1] - x[0]
    ax.add_patch(Rectangle((0, -0.02), L, 0.04, fc="#e3eefc", ec=INK2, lw=1))
    ax.add_patch(Rectangle((-0.006 * L, -0.06), 0.006 * L, 0.12, color=RED, lw=0))
    ax.scatter(x, [0] * len(x), s=46, color=BLUE, ec="white", lw=1.2, zorder=3)
    ax.scatter([x[0]], [0], s=60, color=RED, ec="white", lw=1.2, zorder=4)
    ax.scatter([L + dx], [0], s=46, fc="white", ec=MUTED, lw=1.2, zorder=3, ls=(0, (2, 1.5)))
    for i, xi in enumerate(x):
        ax.text(xi, -0.075, str(i), ha="center", va="top", fontsize=8.5, color=INK)
    ax.text(L + dx, -0.075, f"{N + 1}", ha="center", va="top", fontsize=8.5, color=MUTED)
    ax.text(L + dx, 0.05, "ghost\nnode", ha="center", va="bottom", fontsize=8, color=MUTED)
    ax.text(x[0], 0.05, "base\n(known)", ha="center", va="bottom", fontsize=8, color=INK2)
    ax.text(L, 0.05, "tip", ha="center", va="bottom", fontsize=8, color=INK2)
    ax.text(-0.02 * L, -0.075, "i =", ha="right", va="top", fontsize=8.5, color=INK2)
    _arrow(ax, (x[3], 0.035), (x[4], 0.035), style="<->", lw=0.9, scale=7)
    ax.text((x[3] + x[4]) / 2, 0.045, r"$\Delta x$", ha="center", va="bottom", fontsize=9.5)
    ax.set_xlim(-0.06 * L, L + 1.6 * dx)
    ax.set_ylim(-0.13, 0.13)
    plt.show()


def sweeps(x, history, changes, T_exact, tol):
    """How Gauss-Seidel walks from the initial 30 °C to the converged profile."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.6), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.3, top=0.9, wspace=0.32)
    shown = [k for k in (0, 1, 3, 10, 30, 100) if k < len(history)] + [len(history) - 1]
    xx = [x[-1] * j / 200 for j in range(201)]
    ax1.plot([v * 100 for v in xx], [T_exact(v) for v in xx], color=INK, lw=1.2, label="exact", zorder=1)
    for color, k in zip(STEPS[len(STEPS) - len(shown):], shown):
        ax1.plot([v * 100 for v in x], history[k], color=color, lw=1.8, marker="o", ms=3.5,
                 label=f"sweep {k}")
    ax1.set_xlabel("x [cm]")
    ax1.set_ylabel("T [°C]")
    ax1.set_title("Temperature after each sweep")
    fig.legend(*ax1.get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0), columnspacing=1.2, handlelength=1.8)
    ax2.semilogy(range(1, len(changes) + 1), changes, color=BLUE, lw=1.8)
    ax2.axhline(tol, color=MUTED, lw=1)
    ax2.text(len(changes) * 0.55, tol * 2, "tolerance", ha="center", fontsize=8.5, color=INK2)
    ax2.set_xlabel("sweep")
    ax2.set_ylabel("largest change [°C]")
    ax2.set_title("Convergence")
    plt.show()


def profile(x, T, T_exact, T_inf, T_b):
    """FDM temperatures against the exact solution, with the fin coloured by temperature."""
    fig = plt.figure(figsize=(7.2, 3.6))
    ax = fig.add_axes([0.1, 0.36, 0.86, 0.54])
    xx = [x[-1] * j / 300 for j in range(301)]
    ax.plot([v * 100 for v in xx], [T_exact(v) for v in xx], color=INK, lw=1.6, label="exact solution")
    ax.scatter([v * 100 for v in x], T, s=40, color=ORANGE, ec="white", lw=1.2, zorder=3,
               label=f"FDM, {len(x)} nodes")
    ax.set_ylabel("T [°C]")
    ax.set_xlim(0, x[-1] * 100)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right")
    ax.set_title("Steady temperature distribution along the fin")
    ax.tick_params(labelbottom=False)
    strip = fig.add_axes([0.1, 0.17, 0.86, 0.1])
    T_tip = T_exact(x[-1])
    strip.imshow([[T_exact(v) for v in xx]], cmap=HEAT, vmin=T_tip - 0.5 * (T_b - T_tip), vmax=T_b,
                 aspect="auto", extent=(0, x[-1] * 100, 0, 1))
    strip.text(0.5, 0.5, f"{T_b:.0f} °C", va="center", fontsize=8.5, color="white")
    strip.text(x[-1] * 100 - 0.5, 0.5, f"{T_tip:.1f} °C", ha="right", va="center", fontsize=8.5, color=INK)
    strip.set_yticks([])
    strip.set_xlabel("x [cm]")
    for s in ("left", "top", "right"):
        strip.spines[s].set_visible(False)
    fig.text(0.1, 0.29, "the fin, coloured by temperature", fontsize=8, color=INK2)
    plt.show()


def convergence(dxs, errors):
    """Grid-refinement study: error versus grid spacing on log-log axes."""
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    fig.subplots_adjust(left=0.15, right=0.96, bottom=0.16, top=0.88)
    ax.loglog([v * 100 for v in dxs], errors, color=BLUE, lw=1.8, marker="o", ms=6, mec="white",
              label="largest error of FDM")
    ref = [errors[0] * (v / dxs[0]) ** 2 * 0.5 for v in dxs]
    ax.loglog([v * 100 for v in dxs], ref, color=MUTED, lw=1.1, label=r"slope 2  ($\propto\Delta x^2$)")
    ax.set_xticks([v * 100 for v in dxs], [f"{v * 100:g}" for v in dxs])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel(r"grid spacing $\Delta x$ [cm]")
    ax.set_ylabel("largest error [°C]")
    ax.set_title("Verification: halve Δx, error ÷ 4")
    ax.grid(color=GRID, lw=0.6, which="major")
    ax.legend(loc="upper left")
    plt.show()
