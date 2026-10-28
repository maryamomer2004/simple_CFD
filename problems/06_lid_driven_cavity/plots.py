"""Drawing helpers for Problem 6 (the lid-driven cavity).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging
import math

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
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

SPIN = LinearSegmentedColormap.from_list(   # vorticity: blue = clockwise, orange = anticlockwise
    "spin", ["#0d366b", "#3987e5", "#cde2fb", "#ffffff", "#fdd5b5", "#eb6834", "#7a2a0e"])
GRID_COLORS = {8: STEPS[2], 16: STEPS[3], 32: STEPS[4], 64: STEPS[5], 128: STEPS[6]}


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def _cavity(ax, lid_width=0.035):
    """Walls (hatched) and the moving lid (orange) around the unit square."""
    for x, y, w, h in ((-0.04, -0.04, 0.04, 1.04), (1.0, -0.04, 0.04, 1.04), (-0.04, -0.04, 1.08, 0.04)):
        ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=INK2, lw=0.8, hatch="////", zorder=4))
    ax.add_patch(Rectangle((-0.06, 1.0), 1.12, lid_width, fc=ORANGE, ec="none", zorder=4))


def schematic(L, U):
    """The square cavity, the sliding lid and the expected vortex."""
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    ax.set_xlim(-0.55, 1.55)
    ax.set_ylim(-0.3, 1.32)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="#eef5fd", ec="none", zorder=1))
    _cavity(ax)
    _arrow(ax, (0.25, 1.11), (0.75, 1.11), color=INK, lw=1.8, scale=14)
    ax.text(0.5, 1.16, f"lid slides at $U$ = {U:g} m/s", ha="center", va="bottom", fontsize=10)
    # a sketch of the clockwise vortex
    for r, a in ((0.33, 0.9), (0.2, 0.6)):
        t = [k / 60 * 6.0 for k in range(61)]
        xs = [0.6 + r * math.cos(-tt) for tt in t]
        ys = [0.6 + 0.9 * r * math.sin(-tt) for tt in t]
        ax.plot(xs, ys, color=BLUE, lw=1.4, alpha=a, zorder=2)
        _arrow(ax, (xs[-2], ys[-2]), (xs[-1], ys[-1]), color=BLUE, lw=1.4, scale=12)
    ax.text(0.6, 0.6, "vortex", ha="center", va="center", fontsize=9, color=BLUE)
    ax.text(0.5, 0.08, "fluid, kinematic viscosity $\\nu$", ha="center", fontsize=9, color=INK2, zorder=5)
    ax.text(-0.08, 0.5, "wall at rest\n$u = v = 0$", ha="right", va="center", fontsize=9, color=INK2)
    ax.text(1.08, 0.5, "wall at rest\n$u = v = 0$", ha="left", va="center", fontsize=9, color=INK2)
    ax.text(0.5, -0.08, "wall at rest,  $u = v = 0$", ha="center", va="top", fontsize=9, color=INK2)
    _arrow(ax, (0, -0.2), (1, -0.2), style="<->", lw=1.0, scale=8)
    ax.text(0.5, -0.23, f"$L$ = {L:g} m", ha="center", va="top", fontsize=9.5)
    _arrow(ax, (1.42, 0), (1.42, 1), style="<->", lw=1.0, scale=8)
    ax.text(1.45, 0.25, "$L$", ha="left", va="center", fontsize=9.5)
    _arrow(ax, (-0.42, -0.12), (-0.27, -0.12), color=INK2, lw=1.0, scale=8)
    _arrow(ax, (-0.42, -0.12), (-0.42, 0.03), color=INK2, lw=1.0, scale=8)
    ax.text(-0.25, -0.12, "x", va="center", fontsize=9, color=INK2)
    ax.text(-0.42, 0.05, "y", ha="center", va="bottom", fontsize=9, color=INK2)
    plt.show()


def grid(N):
    """Wall nodes, interior nodes and the five-point stencil of one node."""
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.17, top=0.98)
    h = 1 / N
    for k in range(N + 1):
        ax.plot([0, 1], [k * h, k * h], color=GRID, lw=0.8, zorder=1)
        ax.plot([k * h, k * h], [0, 1], color=GRID, lw=0.8, zorder=1)
    wall = [(i * h, j * h) for i in range(N + 1) for j in range(N + 1) if i in (0, N) or j == 0]
    lid = [(i * h, 1.0) for i in range(1, N)]
    inner = [(i * h, j * h) for i in range(1, N) for j in range(1, N)]
    ax.scatter(*zip(*inner), s=26, color=BLUE, zorder=3, label="interior node: $\\psi$, $\\omega$ unknown")
    ax.scatter(*zip(*wall), s=26, color=INK2, zorder=3, label="wall: $\\psi = 0$, $\\omega$ from Thom's formula")
    ax.scatter(*zip(*lid), s=30, color=ORANGE, zorder=3, label="lid: $\\psi = 0$, $u = U$")
    P = (N // 2 - 1, N // 2 + 1) if N >= 8 else (N // 2, N // 2)
    for di, dj, lab in ((0, 0, "P"), (1, 0, "E"), (-1, 0, "W"), (0, 1, "N"), (0, -1, "S")):
        xx, yy = (P[0] + di) * h, (P[1] + dj) * h
        ax.scatter([xx], [yy], s=110, fc="none", ec=VIOLET, lw=1.6, zorder=4)
        ax.text(xx + 0.022, yy + 0.022, lab, fontsize=9.5, color=VIOLET, fontweight="bold", zorder=5)
    _arrow(ax, (0.3, 1.07), (0.7, 1.07), color=INK, lw=1.5, scale=12)
    ax.text(0.5, 1.1, "lid", ha="center", va="bottom", fontsize=9)
    _arrow(ax, ((N - 2) * h, -0.05), ((N - 1) * h, -0.05), style="<->", lw=0.9, scale=7)
    ax.text((N - 1.5) * h, -0.065, "$h$", ha="center", va="top", fontsize=10)
    for k in (0, N):
        ax.text(k * h, -0.06, f"i = {k}", ha="center", va="top", fontsize=8.5, color=INK2)
        ax.text(-0.05, k * h, f"j = {k}", ha="right", va="center", fontsize=8.5, color=INK2)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", fontsize=8.5, ncol=1,
               handletextpad=0.3, bbox_to_anchor=(0.5, 0.0))
    ax.set_xlim(-0.2, 1.08)
    ax.set_ylim(-0.12, 1.18)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def iterations(changes, tol):
    """Largest change of the vorticity and of the stream function in every iteration."""
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.15, top=0.9)
    it = range(1, len(changes) + 1)
    ax.semilogy(it, [c[0] for c in changes], color=ORANGE, lw=1.8, label="vorticity $\\omega$ [1/s]")
    ax.semilogy(it, [c[1] for c in changes], color=BLUE, lw=1.8, label="stream function $\\psi$ [m²/s]")
    ax.axhline(tol, color=MUTED, lw=1)
    ax.text(len(changes) * 0.02, tol * 1.6, "tolerance", fontsize=8.5, color=INK2)
    ax.set_xlabel("iteration")
    ax.set_ylabel("largest change")
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("Convergence of the coupled Gauss–Seidel iteration")
    plt.show()


def flow(x, psi, w, u, v, centre):
    """Streamlines with velocity arrows (left) and vorticity contours (right)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 4.6))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.27, top=0.92, wspace=0.18)
    levels = [-0.1, -0.09, -0.07, -0.05, -0.03, -0.01, -0.003, -0.001, -1e-4]
    ax1.contour(x, x, psi, levels=levels, colors=BLUE, linewidths=1.0, linestyles="solid")
    ax1.contour(x, x, psi, levels=[1e-6, 5e-6], colors=ORANGE, linewidths=0.9, linestyles="solid")
    N = len(x) - 1
    step = max(1, N // 16)
    pts = [(i, j) for j in range(step, N, step) for i in range(step, N, step)]
    ax1.quiver([x[i] for i, j in pts], [x[j] for i, j in pts], [u[j][i] for i, j in pts],
               [v[j][i] for i, j in pts], color=INK2, scale=6, width=0.004, alpha=0.75)
    ax1.scatter([centre[0]], [centre[1]], s=40, color=RED, zorder=5)
    ax1.text(centre[0] + 0.03, centre[1] + 0.03, "vortex centre", fontsize=8.5, color=RED, zorder=6,
             bbox=dict(fc="white", ec="none", pad=1, alpha=0.85))
    ax1.set_title("Streamlines ($\\psi$ = const) and velocity")
    vmax = 5
    clipped = [[max(-vmax, min(vmax, val)) for val in row] for row in w]
    cf = ax2.contourf(x, x, clipped, levels=[-5, -4, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 2, 3, 5],
                      cmap=SPIN, norm=TwoSlopeNorm(0, -vmax, vmax))
    ax2.contour(x, x, clipped, levels=[-3, -2, -1, 0, 1, 2], colors=INK2, linewidths=0.5, linestyles="solid")
    ax2.set_title("Vorticity $\\omega$ [1/s]")
    for ax in (ax1, ax2):
        ax.set_aspect("equal")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.04)
        ax.add_patch(Rectangle((0, 1.0), 1, 0.04, fc=ORANGE, ec="none"))
        ax.set_xlabel("x [m]")
        ax.set_xticks([0, 0.5, 1])
        ax.set_yticks([0, 0.5, 1])
    ax1.set_ylabel("y [m]")
    cax = fig.add_axes([0.56, 0.115, 0.4, 0.025])
    cb = fig.colorbar(cf, cax=cax, orientation="horizontal", ticks=[-5, -3, -1, 0, 1, 3, 5])
    cb.ax.tick_params(labelsize=8)
    cb.outline.set_visible(False)
    fig.text(0.07, 0.115, "the lid (orange) moves to the right;\norange streamlines: the two small corner eddies",
             fontsize=8, color=INK2, va="center")
    fig.text(0.56, 0.015, "vorticity beyond ±5 1/s (near the lid corners) is clipped", fontsize=8, color=INK2)
    plt.show()


def profiles(lines, ghia_y, ghia_u, ghia_x, ghia_v):
    """u on the vertical and v on the horizontal centre line, several grids, and the benchmark."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.9))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.3, top=0.9, wspace=0.3)
    for n, (u_line, v_line) in lines.items():
        pos = [k / n for k in range(n + 1)]
        ax1.plot(u_line, pos, color=GRID_COLORS[n], lw=1.6, label=f"FDM, N = {n}")
        ax2.plot(pos, v_line, color=GRID_COLORS[n], lw=1.6)
    ax1.scatter(ghia_u, ghia_y, s=26, marker="s", fc="white", ec=RED, lw=1.3, zorder=5,
                label="Ghia et al. (1982)")
    ax2.scatter(ghia_x, ghia_v, s=26, marker="s", fc="white", ec=RED, lw=1.3, zorder=5)
    ax1.set_xlabel("u [m/s] on the line x = 0.5")
    ax1.set_ylabel("y [m]")
    ax1.set_title("Horizontal velocity u")
    ax2.set_xlabel("x [m]")
    ax2.set_ylabel("v [m/s] on the line y = 0.5")
    ax2.set_title("Vertical velocity v")
    for ax in (ax1, ax2):
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*ax1.get_legend_handles_labels(), loc="lower center", ncol=5, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0), columnspacing=1.2, handlelength=1.8)
    plt.show()


def grid_study(grids, psi_mins, ghia_psi_min):
    """psi_min on every grid, and its change per halving of h on log-log axes."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.5))
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.17, top=0.88, wspace=0.35)
    ax1.plot(grids, psi_mins, color=BLUE, lw=1.8, marker="o", ms=6, mec="white", label="FDM")
    ax1.axhline(ghia_psi_min, color=RED, lw=1.1, ls="--", label="Ghia et al.")
    ax1.set_xscale("log", base=2)
    ax1.set_xticks(grids, [str(n) for n in grids])
    ax1.xaxis.set_minor_formatter(NullFormatter())
    ax1.set_xlabel("N (intervals per side)")
    ax1.set_ylabel(r"$\psi_{min}$ [m²/s]")
    ax1.set_title("Strength of the primary vortex")
    ax1.legend(loc="upper right", fontsize=8.5)
    hs = [1 / n for n in grids[1:]]
    changes = [abs(psi_mins[k + 1] - psi_mins[k]) for k in range(len(grids) - 1)]
    ax2.loglog(hs, changes, color=BLUE, lw=1.8, marker="o", ms=6, mec="white", label="change when h is halved")
    ref = [changes[-1] * 0.5 * (hh / hs[-1]) ** 2 for hh in hs[1:]]
    ax2.loglog(hs[1:], ref, color=MUTED, lw=1.1, label=r"slope 2  ($\propto h^2$)")
    ax2.set_xticks(hs, [f"1/{n}" for n in grids[1:]])
    ax2.xaxis.set_minor_formatter(NullFormatter())
    ax2.set_xlabel("grid spacing h [m]")
    ax2.set_ylabel(r"|change of $\psi_{min}$|")
    ax2.set_title("Second-order convergence")
    ax2.legend(loc="lower right", fontsize=8.5)
    for ax in (ax1, ax2):
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    plt.show()


def hand_grid(psi, w, title):
    """The 5 x 5 hand grid with the value of psi (top) and omega (bottom) written at every node."""
    N = len(psi) - 1
    fig, ax = plt.subplots(figsize=(6.0, 5.4))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.92)
    for k in range(N + 1):
        ax.plot([0, N], [k, k], color=GRID, lw=0.8, zorder=1)
        ax.plot([k, k], [0, N], color=GRID, lw=0.8, zorder=1)
    ax.add_patch(Rectangle((-0.08, N), N + 0.16, 0.1, fc=ORANGE, ec="none", zorder=2))
    for j in range(N + 1):
        for i in range(N + 1):
            corner = i in (0, N) and j in (0, N)
            inner = 0 < i < N and 0 < j < N
            ax.scatter([i], [j], s=22, color=BLUE if inner else INK2, zorder=3, alpha=0.35 if corner else 1)
            if corner:
                continue
            if inner:
                ax.text(i, j + 0.1, f"{psi[j][i] + 0.0:.5f}", ha="center", va="bottom", fontsize=7.5, color=BLUE)
            ax.text(i, j - 0.1, f"{w[j][i] + 0.0:.4f}", ha="center", va="top", fontsize=7.5, color=ORANGE,
                    fontweight="semibold")
    for k in range(N + 1):
        ax.text(k, -0.45, f"i = {k}", ha="center", va="top", fontsize=8, color=INK2)
        ax.text(-0.45, k, f"j = {k}", ha="right", va="center", fontsize=8, color=INK2)
    ax.text(N / 2, N + 0.2, "lid", ha="center", va="bottom", fontsize=8.5)
    fig.text(0.02, 0.95, title, fontsize=11, fontweight="semibold", color=INK)
    fig.text(0.98, 0.95, "blue: ψ [m²/s]   orange: ω [1/s]", ha="right", fontsize=8.5, color=INK2)
    ax.set_xlim(-0.9, N + 0.5)
    ax.set_ylim(-0.75, N + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()
