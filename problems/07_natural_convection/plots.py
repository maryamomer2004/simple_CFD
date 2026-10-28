"""Drawing helpers for Problem 7 (natural convection in a heated square cavity).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging
import math

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle

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

TEMP = LinearSegmentedColormap.from_list(    # cold (blue) to hot (red)
    "temp", ["#0d366b", "#3987e5", "#cde2fb", "#fff4eb", "#f7a26f", "#d03b3b", "#7a2a0e"])
RA_COLORS = {1e3: STEPS[3], 1e4: ORANGE}
RA_LABELS = {1e3: "$Ra = 10^3$", 1e4: "$Ra = 10^4$"}


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def _walls(ax, t=0.04):
    """Hot left wall (red), cold right wall (blue), insulated top and bottom (hatched)."""
    ax.add_patch(Rectangle((-t, -t), t, 1 + 2 * t, fc=RED, ec="none", zorder=4))
    ax.add_patch(Rectangle((1, -t), t, 1 + 2 * t, fc=BLUE, ec="none", zorder=4))
    for y in (-t, 1.0):
        ax.add_patch(Rectangle((0, y), 1, t, fc="white", ec=INK2, lw=0.8, hatch="////", zorder=4))


def schematic():
    """The cavity, its four walls, gravity and the buoyancy-driven circulation."""
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    ax.set_xlim(-0.62, 1.62)
    ax.set_ylim(-0.3, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")
    xx = [k / 100 for k in range(101)]
    ax.imshow([[1 - v for v in xx]], cmap=TEMP, vmin=0, vmax=1, extent=(0, 1, 0, 1), aspect="auto",
              alpha=0.35, zorder=1)
    _walls(ax)
    t = [k / 80 * 2 * math.pi * 0.93 for k in range(81)]
    xs = [0.5 + 0.34 * math.cos(-tt + math.pi) for tt in t]
    ys = [0.5 + 0.34 * math.sin(-tt + math.pi) for tt in t]
    ax.plot(xs, ys, color=INK, lw=1.4, zorder=3)
    _arrow(ax, (xs[-2], ys[-2]), (xs[-1], ys[-1]), color=INK, lw=1.4, scale=12)
    ax.text(0.04, 0.9, "warm air rises", ha="left", va="center", fontsize=8.5, color=RED, zorder=5)
    ax.text(0.96, 0.1, "cool air sinks", ha="right", va="center", fontsize=8.5, color=BLUE, zorder=5)
    ax.text(-0.07, 0.62, "hot wall\n$T = T_h$", ha="right", va="center", fontsize=9.5, color=RED)
    ax.text(1.07, 0.62, "cold wall\n$T = T_c$", ha="left", va="center", fontsize=9.5, color=BLUE)
    ax.text(0.5, 1.07, "insulated:  $\\partial T/\\partial y = 0$", ha="center", va="bottom", fontsize=9,
            color=INK2)
    ax.text(0.5, -0.07, "insulated:  $\\partial T/\\partial y = 0$", ha="center", va="top", fontsize=9,
            color=INK2)
    _arrow(ax, (1.42, 0.85), (1.42, 0.55), color=INK, lw=1.4, scale=12)
    ax.text(1.46, 0.7, "$g$", ha="left", va="center", fontsize=11)
    _arrow(ax, (0, -0.22), (1, -0.22), style="<->", lw=1.0, scale=8)
    ax.text(0.5, -0.25, "$L$", ha="center", va="top", fontsize=10)
    ax.text(0.5, 0.5, "air, $Pr = 0.71$", ha="center", va="center", fontsize=9, color=INK2, zorder=5)
    ax.text(-0.5, 0.15, "all four walls:\nno slip, $u = v = 0$", ha="left", va="center", fontsize=8.5,
            color=INK2)
    plt.show()


def grid(N):
    """Node types: fixed-temperature walls, insulated walls, interior nodes; one stencil."""
    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.2, top=0.98)
    h = 1 / N
    for k in range(N + 1):
        ax.plot([0, 1], [k * h, k * h], color=GRID, lw=0.8, zorder=1)
        ax.plot([k * h, k * h], [0, 1], color=GRID, lw=0.8, zorder=1)
    inner = [(i * h, j * h) for i in range(1, N) for j in range(1, N)]
    hot = [(0, j * h) for j in range(N + 1)]
    cold = [(1, j * h) for j in range(N + 1)]
    insulated = [(i * h, y) for i in range(1, N) for y in (0, 1)]
    ax.scatter(*zip(*inner), s=26, color=INK, zorder=3, label="interior: $\\psi$, $\\omega$, $T$ unknown")
    ax.scatter(*zip(*insulated), s=34, fc="white", ec=VIOLET, lw=1.5, zorder=3,
               label="insulated wall: $\\psi = 0$, $T$ unknown (ghost node)")
    ax.scatter(*zip(*hot), s=30, color=RED, zorder=3, label="hot wall: $\\psi = 0$, $T = 1$")
    ax.scatter(*zip(*cold), s=30, color=BLUE, zorder=3, label="cold wall: $\\psi = 0$, $T = 0$")
    ghost = [(i * h, -h) for i in range(1, N)]
    ax.scatter(*zip(*ghost), s=26, fc="white", ec=MUTED, lw=1.0, ls=(0, (2, 1.5)), zorder=3)
    ax.text(1.0 + 0.04, -h, "ghost nodes\n$T_{i,-1} = T_{i,1}$", fontsize=8, color=MUTED, va="center")
    P = (N // 2 - 1, N // 2 + 1) if N >= 8 else (N // 2, N // 2)
    for di, dj, lab in ((0, 0, "P"), (1, 0, "E"), (-1, 0, "W"), (0, 1, "N"), (0, -1, "S")):
        xx, yy = (P[0] + di) * h, (P[1] + dj) * h
        ax.scatter([xx], [yy], s=110, fc="none", ec=AQUA, lw=1.6, zorder=4)
        ax.text(xx + 0.022, yy + 0.022, lab, fontsize=9.5, color=AQUA, fontweight="bold", zorder=5)
    _arrow(ax, ((N - 2) * h, 1.06), ((N - 1) * h, 1.06), style="<->", lw=0.9, scale=7)
    ax.text((N - 1.5) * h, 1.075, "$h$", ha="center", va="bottom", fontsize=10)
    for k in (0, N):
        ax.text(k * h, 1.06, f"i = {k}", ha="center", va="bottom", fontsize=8.5, color=INK2)
        ax.text(-0.05, k * h, f"j = {k}", ha="right", va="center", fontsize=8.5, color=INK2)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", fontsize=8.5, ncol=1,
               handletextpad=0.3, bbox_to_anchor=(0.5, 0.0))
    ax.set_xlim(-0.2, 1.3)
    ax.set_ylim(-h - 0.08, 1.14)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def iterations(changes, tol, label):
    """Largest change of T, omega and psi in every iteration."""
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.15, top=0.9)
    it = range(1, len(changes) + 1)
    for k, (name, color) in enumerate((("temperature $T$", RED), ("vorticity $\\omega$", ORANGE),
                                       ("stream function $\\psi$", BLUE))):
        ax.semilogy(it[1:], [c[k] for c in changes[1:]], color=color, lw=1.8, label=name)
    ax.axhline(tol, color=MUTED, lw=1)
    ax.text(len(changes) * 0.02, tol * 1.6, "tolerance", fontsize=8.5, color=INK2)
    ax.set_xlabel("iteration")
    ax.set_ylabel("largest change")
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title(f"Convergence of the coupled Gauss–Seidel iteration ({label})")
    ax.set_xlim(0, len(changes))
    plt.show()


def fields(x, solutions):
    """Streamlines (top row) and isotherms (bottom row) for each Rayleigh number."""
    fig, axes = plt.subplots(2, len(solutions), figsize=(7.4, 7.6))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.12, top=0.95, wspace=0.18, hspace=0.25)
    for col, (Ra, (psi, w, T)) in enumerate(solutions.items()):
        ax1, ax2 = axes[0][col], axes[1][col]
        low = min(min(row) for row in psi)
        levels = [low * f for f in (0.95, 0.8, 0.6, 0.4, 0.2, 0.05)]
        ax1.contour(x, x, psi, levels=sorted(levels), colors=BLUE, linewidths=1.1, linestyles="solid")
        ax1.set_title(f"Streamlines, {RA_LABELS[Ra]}")
        ax1.text(0.04, 0.95, f"$|\\psi|_{{max}}$ = {-low:.2f}", ha="left", va="top", fontsize=8.5,
                 color=INK2, bbox=dict(fc="white", ec="none", pad=1, alpha=0.8))
        cf = ax2.contourf(x, x, T, levels=[k / 10 for k in range(11)], cmap=TEMP, vmin=0, vmax=1)
        ax2.contour(x, x, T, levels=[k / 10 for k in range(1, 10)], colors=INK2, linewidths=0.6,
                    linestyles="solid")
        ax2.set_title(f"Isotherms, {RA_LABELS[Ra]}")
        for ax in (ax1, ax2):
            ax.set_aspect("equal")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([0, 0.5, 1])
            ax.set_yticks([0, 0.5, 1])
            ax.spines["top"].set_visible(True)
            ax.spines["right"].set_visible(True)
            ax.spines["left"].set_color(RED)
            ax.spines["left"].set_linewidth(3)
            ax.spines["right"].set_color(BLUE)
            ax.spines["right"].set_linewidth(3)
        ax2.set_xlabel("x / L")
    axes[0][0].set_ylabel("y / L")
    axes[1][0].set_ylabel("y / L")
    cax = fig.add_axes([0.08, 0.025, 0.4, 0.015])
    cb = fig.colorbar(cf, cax=cax, orientation="horizontal", ticks=[0, 0.5, 1])
    cb.ax.tick_params(labelsize=8)
    cb.outline.set_visible(False)
    fig.text(0.5, 0.032, "T  (1 = hot wall, 0 = cold wall)", fontsize=8, color=INK2, va="center")
    plt.show()


def nusselt(x, local):
    """Local Nusselt number along the hot wall."""
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.15, top=0.9)
    for Ra, values in local.items():
        ax.plot(values, x, color=RA_COLORS[Ra], lw=1.8, label=RA_LABELS[Ra])
    ax.axvline(1, color=MUTED, lw=1, ls="--")
    ax.text(1.03, 0.95, "pure\nconduction", fontsize=8, color=INK2, va="top")
    ax.set_xlabel("local Nusselt number on the hot wall,  $-\\partial T/\\partial x$")
    ax.set_ylabel("y / L")
    ax.set_xlim(0, None)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="center right", fontsize=9)
    ax.set_title("Heat flux along the hot wall")
    plt.show()


def grid_study(grids, study, davis):
    """|psi_mid| and Nu on every grid, against the benchmark."""
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.27, top=0.88, wspace=0.32)
    for ax, name, title in ((axes[0], "psi_mid", r"$|\psi|$ at the centre"), (axes[1], "Nu", r"average $Nu$")):
        for Ra in study:
            values = [study[Ra][n][name] / davis[Ra][name] for n in grids]
            ax.plot(grids, values, color=RA_COLORS[Ra], lw=1.8, marker="o", ms=6, mec="white",
                    label=RA_LABELS[Ra])
        ax.axhline(1, color=RED, lw=1.1, ls="--", label="de Vahl Davis (1983)")
        ax.set_xscale("log", base=2)
        ax.set_xticks(grids, [str(n) for n in grids])
        ax.minorticks_off()
        ax.set_xlabel("N (intervals per side)")
        ax.set_ylabel("FDM / benchmark")
        ax.set_title(title)
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def profiles(x, lines, davis):
    """u on the vertical and v on the horizontal centre line, with the benchmark maxima."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.8))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.28, top=0.9, wspace=0.3)
    for Ra, (u_line, v_line) in lines.items():
        ax1.plot(u_line, x, color=RA_COLORS[Ra], lw=1.8, label=f"FDM, {RA_LABELS[Ra]}")
        ax2.plot(x, v_line, color=RA_COLORS[Ra], lw=1.8)
        ax1.scatter([davis[Ra]["u_max"][0]], [davis[Ra]["u_max"][1]], s=32, marker="s", fc="white",
                    ec=RED, lw=1.3, zorder=5)
        ax2.scatter([davis[Ra]["v_max"][1]], [davis[Ra]["v_max"][0]], s=32, marker="s", fc="white",
                    ec=RED, lw=1.3, zorder=5)
    ax1.scatter([], [], s=32, marker="s", fc="white", ec=RED, lw=1.3, label="de Vahl Davis maxima")
    ax1.axvline(0, color=MUTED, lw=0.8)
    ax2.axhline(0, color=MUTED, lw=0.8)
    ax1.set_xlabel("u  on the line x = 0.5")
    ax1.set_ylabel("y / L")
    ax1.set_title("Horizontal velocity")
    ax2.set_xlabel("x / L")
    ax2.set_ylabel("v  on the line y = 0.5")
    ax2.set_title("Vertical velocity")
    for ax in (ax1, ax2):
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*ax1.get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    fig.text(0.98, 0.01, "velocities in units of $\\alpha / L$", ha="right", fontsize=8, color=INK2)
    plt.show()


def hand_grid(psi, w, T, title):
    """The 5 x 5 hand grid with T (red), omega (orange) and psi (blue) at every node."""
    N = len(psi) - 1
    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.93)
    for k in range(N + 1):
        ax.plot([0, N], [k, k], color=GRID, lw=0.8, zorder=1)
        ax.plot([k, k], [0, N], color=GRID, lw=0.8, zorder=1)
    ax.add_patch(Rectangle((-0.1, -0.05), 0.1, N + 0.1, fc=RED, ec="none", zorder=2))
    ax.add_patch(Rectangle((N, -0.05), 0.1, N + 0.1, fc=BLUE, ec="none", zorder=2))
    for j in range(N + 1):
        for i in range(N + 1):
            inner = 0 < i < N and 0 < j < N
            corner = i in (0, N) and j in (0, N)
            ax.scatter([i], [j], s=20, color=INK if inner else INK2, zorder=3)
            dx, ha = (-0.2, "right") if i == 0 else (0.2, "left") if i == N else (0, "center")
            ax.text(i + dx, j + 0.1, f"{T[j][i] + 0.0:.4f}", ha=ha, va="bottom", fontsize=9, color=RED)
            if not corner:
                ax.text(i + dx, j - 0.08, f"{w[j][i] + 0.0:.3f}", ha=ha, va="top", fontsize=9, color=ORANGE,
                        fontweight="semibold")
            if inner:
                ax.text(i, j - 0.34, f"{psi[j][i] + 0.0:.4f}", ha="center", va="top", fontsize=9, color=BLUE)
    for k in range(N + 1):
        ax.text(k, -0.6, f"i = {k}", ha="center", va="top", fontsize=8, color=INK2)
        ax.text(-0.95, k, f"j = {k}", ha="right", va="center", fontsize=8, color=INK2)
    fig.text(0.02, 0.95, title, fontsize=11, fontweight="semibold", color=INK)
    fig.text(0.98, 0.95, "red: T   orange: ω   blue: ψ", ha="right", fontsize=8.5, color=INK2)
    ax.set_xlim(-1.5, N + 1.0)
    ax.set_ylim(-0.85, N + 0.45)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()
