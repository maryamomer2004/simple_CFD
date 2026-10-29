"""Drawing helpers for Problem 8 (cooling a steel billet).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # quiet font fallback notes

BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#d03b3b"
INK, INK2, MUTED, GRID, SURFACE = "#1f2328", "#59636e", "#818b98", "#d8dee4", "#f6f8fa"
STEPS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
STEEL = "#c9d1d9"

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

TEMP = LinearSegmentedColormap.from_list(    # cold (blue) to hot (red)
    "temp", ["#0d366b", "#3987e5", "#cde2fb", "#fff4eb", "#f7a26f", "#d03b3b", "#7a2a0e"])
POINT_COLORS = {"centre": RED, "surface middle": ORANGE, "corner": BLUE}


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def _style(ax):
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def schematic():
    """The billet cross-section, the cooling fluid on all four sides, and the quarter we model."""
    fig, ax = plt.subplots(figsize=(6.6, 4.9))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    ax.set_xlim(-1.75, 1.95)
    ax.set_ylim(-1.62, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((-1, -1), 2, 2, fc="#f7a26f", ec=INK, lw=1.4, zorder=1))
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="#eb6834", ec="none", alpha=0.55, zorder=2))
    ax.plot([-1.08, 1.08], [0, 0], color=INK, lw=1.0, ls=(0, (6, 3)), zorder=3)
    ax.plot([0, 0], [-1.08, 1.08], color=INK, lw=1.0, ls=(0, (6, 3)), zorder=3)
    ax.text(0.5, 0.5, "the quarter\nwe model", ha="center", va="center", fontsize=9, color=INK, zorder=4)
    ax.text(-0.5, -0.5, "steel\n$T(x, y, 0) = T_i$", ha="center", va="center", fontsize=9, color=INK,
            zorder=4)
    for s in (-0.6, 0.0, 0.6):          # cooling arrows on all four sides
        _arrow(ax, (s, 1.32), (s, 1.08), color=BLUE)
        _arrow(ax, (s, -1.32), (s, -1.08), color=BLUE)
        _arrow(ax, (-1.32, s), (-1.08, s), color=BLUE)
        _arrow(ax, (1.32, s), (1.08, s), color=BLUE)
    ax.text(1.38, 0.95, "cooling fluid\n$T_\\infty$, $h$\non all four sides", ha="left", va="center",
            fontsize=9, color=BLUE)
    _arrow(ax, (0, 0), (0.42, 0), color=INK, lw=1.3, scale=10)
    _arrow(ax, (0, 0), (0, 0.42), color=INK, lw=1.3, scale=10)
    ax.text(0.44, -0.04, "$x$", ha="left", va="top", fontsize=10.5)
    ax.text(-0.04, 0.44, "$y$", ha="right", va="bottom", fontsize=10.5)
    ax.text(-0.96, 0.04, "symmetry line $y = 0$", ha="left", va="bottom", fontsize=8.5, color=INK)
    ax.text(0.05, -0.96, "symmetry line $x = 0$", ha="left", va="bottom", fontsize=8.5, color=INK,
            rotation=90)
    _arrow(ax, (-1, -1.45), (1, -1.45), style="<->", lw=1.0, scale=8)
    ax.text(0, -1.5, "$2L$", ha="center", va="top", fontsize=10)
    _arrow(ax, (-1.55, 0), (-1.55, 1), style="<->", lw=1.0, scale=8)
    ax.text(-1.6, 0.5, "$L$", ha="right", va="center", fontsize=10)
    ax.text(1.38, -0.62, "long bar:\nnothing changes\nalong its length", ha="left", va="center",
            fontsize=8.5, color=INK2)
    plt.show()


def grid(N):
    """The quarter grid: node types, ghost nodes on the symmetry lines, control volumes."""
    fig, ax = plt.subplots(figsize=(6.2, 5.8))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.22, top=0.98)
    d = 1 / N
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="#fff4eb", ec="none", zorder=0))
    for k in range(N + 1):
        ax.plot([0, 1], [k * d, k * d], color=GRID, lw=0.8, zorder=1)
        ax.plot([k * d, k * d], [0, 1], color=GRID, lw=0.8, zorder=1)
    ax.plot([0, 1], [0, 0], color=INK, lw=1.0, ls=(0, (6, 3)), zorder=2)
    ax.plot([0, 0], [0, 1], color=INK, lw=1.0, ls=(0, (6, 3)), zorder=2)
    ax.plot([1, 1, 0], [0, 1, 1], color=BLUE, lw=3, zorder=2)
    inner = [(i * d, j * d) for i in range(1, N) for j in range(1, N)]
    sym = [(0, j * d) for j in range(1, N)] + [(i * d, 0) for i in range(1, N)]
    edge = [(1, j * d) for j in range(0, N)] + [(i * d, 1) for i in range(0, N)]
    ax.scatter(*zip(*inner), s=26, color=INK, zorder=3, label="interior node")
    ax.scatter(*zip(*(sym + [(0, 0)])), s=34, fc="white", ec=VIOLET, lw=1.5, zorder=3,
               label="symmetry line (ghost node outside)")
    ax.scatter(*zip(*edge), s=34, color=ORANGE, zorder=3, label="convective surface (energy balance)")
    ax.scatter([1], [1], s=60, marker="s", color=BLUE, zorder=3, label="corner (energy balance)")
    ghost = [(-d, j * d) for j in range(0, N + 1)] + [(i * d, -d) for i in range(1, N + 1)]
    ax.scatter(*zip(*ghost), s=24, fc="white", ec=MUTED, lw=1.0, ls=(0, (2, 1.5)), zorder=3)
    ax.text(-d - 0.04, 0.6, "ghost nodes\n$T_{-1,j} = T_{1,j}$", ha="right", va="center", fontsize=8,
            color=MUTED)
    # control volumes of a surface node and of the corner
    j_e = N // 2
    ax.add_patch(Rectangle((1 - d / 2, (j_e - 0.5) * d), d / 2, d, fc="none", ec=ORANGE, lw=1.3,
                           ls="--", zorder=4))
    ax.add_patch(Rectangle((1 - d / 2, 1 - d / 2), d / 2, d / 2, fc="none", ec=BLUE, lw=1.3, ls="--",
                           zorder=4))
    ax.add_patch(Rectangle((0.5 * d, 0.5 * d), d, d, fc="none", ec=INK2, lw=1.0, ls="--", zorder=4))
    ax.text(1 + 0.04, j_e * d, "half cell\n$\\Delta x/2 \\times \\Delta y$", ha="left", va="center",
            fontsize=8, color=ORANGE)
    ax.text(1 + 0.04, 1 + 0.02, "quarter cell\n$\\Delta x/2 \\times \\Delta y/2$", ha="left",
            va="center", fontsize=8, color=BLUE)
    _arrow(ax, (1 - 2 * d, 1.07), (1 - d, 1.07), style="<->", lw=0.9, scale=7)
    ax.text(1 - 1.5 * d, 1.085, "$\\Delta x$", ha="center", va="bottom", fontsize=10)
    for k in (0, N):
        ax.text(k * d, -d - 0.06, f"i = {k}", ha="center", va="top", fontsize=8.5, color=INK2)
        ax.text(-d - 0.05, k * d, f"j = {k}", ha="right", va="center", fontsize=8.5, color=INK2)
    ax.text(0.02, 0.02, "centre", ha="left", va="bottom", fontsize=8, color=VIOLET, zorder=5)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", fontsize=8.5, ncol=2,
               handletextpad=0.3, bbox_to_anchor=(0.5, 0.01))
    ax.set_xlim(-0.42, 1.38)
    ax.set_ylim(-d - 0.12, 1.16)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def stability(cases, T_inf):
    """Corner temperature against time for several values of r (one panel per grid)."""
    fig, axes = plt.subplots(1, len(cases), figsize=(7.8, 3.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.88, wspace=0.22)
    colors = [AQUA, ORANGE, RED]
    for ax, (title, runs) in zip(axes, cases.items()):
        for color, (label, (times, values)) in zip(colors, runs.items()):
            ms = 3 if len(times) < 100 else 0
            ax.plot(times, values, color=color, lw=1.4 if ms else 0.9, marker="o", ms=ms, label=label)
        ax.axhline(T_inf, color=MUTED, lw=0.9, ls="--")
        ax.set_ylim(-150, 650)
        ax.set_xlabel("time [s]")
        ax.set_title(title, fontsize=9.5)
        ax.legend(loc="upper right", fontsize=8, frameon=True, facecolor="white", edgecolor="none",
                  framealpha=0.9)
        _style(ax)
    axes[0].set_ylabel("corner temperature [°C]")
    plt.show()


def history(curves, exact, lumped, target, t_target):
    """Temperature at the centre, the middle of a face and the corner against time."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.13, top=0.9)
    t_ex, ex = exact
    for name, values in ex.items():
        ax.plot(t_ex, values, color=POINT_COLORS[name], lw=1.6, label=f"exact, {name}")
    t_n, num = curves
    for name, values in num.items():
        ax.plot(t_n, values, ls="none", marker="o", ms=4.5, mec=POINT_COLORS[name], mfc="white", mew=1.2,
                label=f"FDM, {name}")
    ax.plot(*lumped, color=INK2, lw=1.4, ls="--", label="lumped capacitance")
    ax.axhline(target, color=MUTED, lw=0.9, ls=":")
    ax.text(t_ex[-1], target + 8, f"target {target:g} °C", ha="right", va="bottom", fontsize=8.5,
            color=INK2)
    ax.axvline(t_target, color=RED, lw=0.9, ls=":")
    ax.text(t_target + 6, 330, f"centre reaches {target:g} °C\nafter {t_target:.0f} s", fontsize=8.5,
            color=RED, va="top")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("temperature [°C]")
    ax.set_xlim(0, t_ex[-1])
    ax.set_ylim(0, 620)
    ax.set_title("Cooling of the billet: FDM against the exact solution")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    _style(ax)
    plt.show()


def fields(L, maps):
    """Temperature over the whole cross-section (the quarter mirrored) at several times.

    Each map has its own colour scale, with labelled isotherms, so the pattern stays visible
    as the billet cools."""
    fig, axes = plt.subplots(1, len(maps), figsize=(8.4, 3.4))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.86, wspace=0.18)
    for ax, (t, T) in zip(axes, maps.items()):
        N = len(T) - 1
        coords = [1000 * L * k / N for k in range(-N, N + 1)]          # mm, from -L to L
        full = [[T[abs(j)][abs(i)] for i in range(-N, N + 1)] for j in range(-N, N + 1)]
        low, high = T[N][N], T[0][0]
        step = 10 if high - low < 150 else 25 if high - low < 300 else 50
        lines = [step * m for m in range(int(low // step) + 1, int(high // step) + 1)]
        ax.contourf(coords, coords, full, levels=40, cmap=TEMP, vmin=low - 0.15 * (high - low),
                    vmax=high + 0.15 * (high - low))
        cs = ax.contour(coords, coords, full, levels=lines, colors=INK, linewidths=0.6,
                        linestyles="solid")
        ax.clabel(cs, cs.levels[::2], fontsize=7, fmt="%.0f")
        ax.set_title(f"t = {t:g} s\ncentre {high:.0f} °C, corner {low:.0f} °C", fontsize=9)
        ax.set_aspect("equal")
        ax.set_xticks([-50, 0, 50])
        ax.set_yticks([-50, 0, 50])
        ax.spines["top"].set_visible(True)
        ax.spines["right"].set_visible(True)
        for side in ax.spines.values():
            side.set_color(BLUE)
            side.set_linewidth(2)
        ax.set_xlabel("x [mm]")
    axes[0].set_ylabel("y [mm]")
    plt.show()


def profiles(x_mm, numerical, exact):
    """Temperature along the line y = 0, from the centre to the surface, at several times."""
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.14, top=0.9)
    colors = [STEPS[6], STEPS[4], STEPS[3], ORANGE, RED]
    for color, (t, values) in zip(colors, numerical.items()):
        x_fine, fine = exact[t]
        ax.plot(x_fine, fine, color=color, lw=1.5, label=f"t = {t:g} s")
        ax.plot(x_mm, values, ls="none", marker="o", ms=4.5, mec=color, mfc="white", mew=1.2)
    ax.plot([], [], ls="none", marker="o", ms=4.5, mec=INK2, mfc="white", label="FDM nodes")
    ax.plot([], [], color=INK2, lw=1.5, label="exact (lines)")
    ax.set_xlabel("x [mm]   (along the symmetry line y = 0, from the centre to the surface)")
    ax.set_ylabel("temperature [°C]")
    ax.set_xlim(0, x_mm[-1])
    ax.set_ylim(0, 620)
    ax.set_title("Temperature profiles: flat inside, steep near the cooled surface")
    ax.legend(loc="center left", bbox_to_anchor=(0.02, 0.38), fontsize=8, ncol=2)
    _style(ax)
    plt.show()


def adi_large_steps(runs, exact, point):
    """ADI with growing time steps: the temperature at one point against time."""
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.14, top=0.9)
    ax.plot(*exact, color=INK, lw=1.6, label="exact")
    colors = [AQUA, ORANGE, RED]
    for color, (label, (times, values)) in zip(colors, runs.items()):
        ax.plot(times, values, color=color, lw=1.3, marker="o", ms=4, label=label)
    ax.set_xlabel("time [s]")
    ax.set_ylabel(f"{point} temperature [°C]")
    ax.set_xlim(0, exact[0][-1])
    ax.set_ylim(0, 620)
    ax.set_title(f"ADI is always stable, but large steps cost accuracy ({point})")
    ax.legend(loc="upper right", fontsize=8.5)
    _style(ax)
    plt.show()


def convergence(space, time_study):
    """Error against grid spacing (left) and against time step (right), on log-log axes."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.7))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.3, top=0.88, wspace=0.32)
    dxs, errors = space
    ax1.loglog(dxs, errors, color=ORANGE, marker="o", ms=6, mec="white", lw=1.8,
               label="FTCS, $r = 0.2$ (largest error)")
    ref = [errors[0] * (d / dxs[0]) ** 2 for d in dxs]
    ax1.loglog(dxs, ref, color=MUTED, lw=1, ls="--", label="slope 2")
    ax1.set_xticks(dxs, [f"{d:g}" for d in dxs])
    ax1.minorticks_off()
    ax1.set_xlabel("$\\Delta x$ [mm]")
    ax1.set_ylabel("error at t = 300 s [°C]")
    ax1.set_title("Refining the grid")
    ax1.legend(loc="lower right", fontsize=8.5)
    colors = {"FTCS": ORANGE, "ADI": BLUE}
    for name, (dts, errs) in time_study.items():
        ax2.loglog(dts, errs, color=colors[name], marker="o", ms=6, mec="white", lw=1.8, label=name)
    for name, p in (("FTCS", 1), ("ADI", 2)):
        dts, errs = time_study[name]
        ax2.loglog(dts, [errs[-1] * (t / dts[-1]) ** p for t in dts], color=MUTED, lw=1, ls="--")
        ax2.text(dts[0] * 1.15, errs[-1] * (dts[0] / dts[-1]) ** p, f"slope {p}", fontsize=8,
                 color=INK2, va="center")
    ax2.set_xlabel("$\\Delta t$ [s]")
    ax2.set_ylabel("time error at the centre [°C]")
    ax2.set_title("Refining the time step")
    ax2.legend(loc="lower right", fontsize=8.5)
    for ax in (ax1, ax2):
        ax.grid(color=GRID, lw=0.6, which="major")
        ax.set_axisbelow(True)
    fig.text(0.5, 0.02, "left: FDM against the exact solution (Δt shrinks with Δx²).   right: same grid "
             "(N = 10), against a run with a tiny time step.", ha="center", fontsize=8, color=INK2)
    plt.show()


def hand_grid(states, T_inf):
    """The 3 x 3 hand grid: temperatures at every node, for several states side by side."""
    rows = (len(states) + 2) // 3
    fig, axes = plt.subplots(rows, 3, figsize=(8.4, 3.0 * rows + 0.4))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=1 - 0.5 / (3.0 * rows + 0.4),
                        wspace=0.08, hspace=0.25)
    axes = [ax for row in axes for ax in row] if rows > 1 else list(axes)
    for ax in axes[len(states):]:
        ax.axis("off")
    for ax, (title, T) in zip(axes, states.items()):
        N = len(T) - 1
        ax.add_patch(Rectangle((0, 0), N, N, fc="#fff4eb", ec="none", zorder=0))
        for k in range(N + 1):
            ax.plot([0, N], [k, k], color=GRID, lw=0.8, zorder=1)
            ax.plot([k, k], [0, N], color=GRID, lw=0.8, zorder=1)
        ax.plot([N, N, 0], [0, N, N], color=BLUE, lw=3, zorder=2)
        ax.plot([0, N], [0, 0], color=INK, lw=1.0, ls=(0, (6, 3)), zorder=2)
        ax.plot([0, 0], [0, N], color=INK, lw=1.0, ls=(0, (6, 3)), zorder=2)
        for j in range(N + 1):
            for i in range(N + 1):
                ax.scatter([i], [j], s=18, color=INK, zorder=3)
                ax.text(i + 0.07, j + 0.08, f"{T[j][i]:.1f}", ha="left", va="bottom", fontsize=9,
                        color=RED, zorder=4, bbox=dict(fc="white", ec="none", pad=0.5, alpha=0.8))
        ax.set_title(title, fontsize=9.5)
        ax.set_xlim(-0.25, N + 0.75)
        ax.set_ylim(-0.25, N + 0.45)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.text(0.02, 1 - 0.25 / (3.0 * rows + 0.4), f"Hand grid (N = 2): temperatures in °C   ·   cooling fluid at {T_inf:g} °C on the "
             "blue edges", fontsize=9, color=INK2)
    plt.show()
