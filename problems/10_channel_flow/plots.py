"""Drawing helpers for Problem 10 (developing laminar flow in a channel).

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
SPEED = LinearSegmentedColormap.from_list(
    "speed", ["#ffffff", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])
DIVERGING = LinearSegmentedColormap.from_list(
    "diverging", ["#0d366b", "#3987e5", "#cde2fb", "#ffffff", "#fdd5b5", "#eb6834", "#7a2a0e"])

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

RE_COLORS = {50: BLUE, 100: ORANGE}


def _re_label(Re):
    return f"$Re = {Re:g}$"


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11, z=5):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0, zorder=z))


def _plates(ax, x0, x1, t=0.07):
    for y in (-t, 1.0):
        ax.add_patch(Rectangle((x0, y), x1 - x0, t, fc="white", ec=INK2, lw=0.9, hatch="////", zorder=4))


def schematic():
    """The channel: uniform inlet, growing boundary layers, Poiseuille profile, outlet at p = 0."""
    fig, ax = plt.subplots(figsize=(8.6, 3.5))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    L = 10.0
    ax.set_xlim(-2.3, L + 1.3)
    ax.set_ylim(-0.75, 1.55)
    ax.set_aspect(1.6)
    ax.axis("off")
    _plates(ax, 0, L)
    # inlet: uniform profile
    for k in range(1, 8):
        y = k / 8
        _arrow(ax, (-1.0, y), (0.0, y), color=BLUE, lw=1.1, scale=7)
    ax.plot([-1.0, -1.0], [0.0, 1.0], color=BLUE, lw=1.0)
    ax.text(-1.15, 0.5, "uniform\ninlet\n$u = U$\n$v = 0$", ha="right", va="center", fontsize=8.5, color=BLUE)
    # developing profiles
    ys = [k / 40 for k in range(41)]
    plug = [1.0 - (1 - min(y, 1 - y) / 0.5) ** 6 for y in ys]
    rate = sum(plug) / 40
    for x0, blend in ((1.8, 0.25), (4.2, 0.8), (7.4, 1.0)):
        prof = [(1 - blend) * a / rate + blend * 6 * y * (1 - y) for a, y in zip(plug, ys)]
        ax.plot([x0 + 0.75 * q for q in prof], ys, color=INK, lw=1.3, zorder=3)
        ax.plot([x0, x0], [0, 1], color=MUTED, lw=0.7, zorder=3)
        for k in (5, 10, 20, 30, 35):
            _arrow(ax, (x0, ys[k]), (x0 + 0.75 * prof[k], ys[k]), color=INK, lw=0.8, scale=6, z=3)
    # boundary-layer edges
    xs = [0.05 * k for k in range(1, 101)]
    delta = [min(0.5, 0.24 * x ** 0.5) for x in xs]
    ax.plot(xs, delta, color=ORANGE, lw=1.1, ls="--", zorder=3)
    ax.plot(xs, [1 - d for d in delta], color=ORANGE, lw=1.1, ls="--", zorder=3)
    ax.text(0.95, 0.2, "boundary\nlayer", fontsize=8, color=ORANGE, ha="center", va="bottom", zorder=5)
    # outlet
    ax.plot([L, L], [0, 1], color=VIOLET, lw=2.2, zorder=5)
    ax.text(L + 0.15, 0.5, "outlet\n$p = 0$", ha="left", va="center", fontsize=8.5, color=VIOLET)
    # labels
    ax.text(L / 2, 1.13, "wall: no slip, $u = v = 0$", ha="center", va="bottom", fontsize=8.5, color=INK2)
    ax.text(L / 2, -0.12, "wall: no slip, $u = v = 0$", ha="center", va="top", fontsize=8.5, color=INK2)
    _arrow(ax, (0.0, -0.45), (4.5, -0.45), style="<->", lw=1.0, scale=8, color=AQUA)
    ax.text(2.25, -0.5, "entrance length $L_e$", ha="center", va="top", fontsize=8.5, color=AQUA)
    ax.text(7.9, -0.5, "fully developed:\n$u = 6U\\,(y/H)(1 - y/H)$", ha="center", va="top", fontsize=8.5,
            color=INK)
    _arrow(ax, (0.0, 1.38), (L, 1.38), style="<->", lw=1.0, scale=8)
    ax.text(L / 2, 1.41, "$L$", ha="center", va="bottom", fontsize=10)
    _arrow(ax, (-1.9, 0.0), (-1.9, 1.0), style="<->", lw=1.0, scale=8)
    ax.text(-2.0, 0.5, "$H$", ha="right", va="center", fontsize=10)
    _arrow(ax, (0.0, 0.0), (0.6, 0.0), color=INK, lw=1.0, scale=7, z=6)
    _arrow(ax, (0.0, 0.0), (0.0, 0.35), color=INK, lw=1.0, scale=7, z=6)
    ax.text(0.62, 0.02, "$x$", fontsize=9, va="bottom", zorder=6)
    ax.text(0.04, 0.33, "$y$", fontsize=9, zorder=6)
    plt.show()


def grid(nx, ny, title=None, labels=False):
    """The staggered (MAC) grid: p in the cells, u on vertical faces, v on horizontal faces, ghosts."""
    width = 1.25 * nx + 2.6
    fig, ax = plt.subplots(figsize=(min(width, 8.6), 0.95 * ny + 2.6))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.07, top=0.93)
    for k in range(nx + 1):
        ax.plot([k, k], [0, ny], color=GRID, lw=0.9, zorder=1)
    for k in range(ny + 1):
        ax.plot([0, nx], [k, k], color=GRID, lw=0.9, zorder=1)
    for y in (-1, ny + 1):   # ghost rows
        ax.plot([0, nx], [y, y], color=GRID, lw=0.7, ls=":", zorder=1)
    for k in range(nx + 1):
        ax.plot([k, k], [-1, 0], color=GRID, lw=0.7, ls=":", zorder=1)
        ax.plot([k, k], [ny, ny + 1], color=GRID, lw=0.7, ls=":", zorder=1)
    for y in (0, ny):
        ax.add_patch(Rectangle((0, y - (0.08 if y == 0 else 0)), nx, 0.08, fc=INK2, ec="none", zorder=2))
    ax.plot([nx, nx], [0, ny], color=VIOLET, lw=2.4, zorder=2)
    ax.plot([0, 0], [0, ny], color=BLUE, lw=2.4, zorder=2)
    for j in range(1, ny + 1):
        for i in range(1, nx + 1):
            ax.scatter([i - 0.5], [j - 0.5], s=34, color=INK, zorder=4)
            if labels:
                ax.text(i - 0.5, j - 0.62, f"$p_{{{i},{j}}}$", ha="center", va="top", fontsize=8, color=INK)
    for j in range(0, ny + 2):        # u: vertical faces (ghost rows j = 0 and ny + 1)
        ghost = j in (0, ny + 1)
        for i in range(0, nx + 1):
            color = MUTED if ghost else (BLUE if i == 0 else INK2 if i == nx else BLUE)
            y = j - 0.5
            _arrow(ax, (i - 0.22, y), (i + 0.22, y), color=MUTED if ghost else BLUE, lw=1.3 if not ghost else 0.9,
                   scale=8, z=4)
    for j in range(0, ny + 1):        # v: horizontal faces (ghost columns i = 0 and nx + 1)
        for i in range(0, nx + 2):
            ghost = i in (0, nx + 1)
            x = i - 0.5
            on_wall = j in (0, ny)
            _arrow(ax, (x, j - 0.22), (x, j + 0.22), color=MUTED if ghost else ORANGE,
                   lw=0.9 if ghost else 1.3, scale=8, z=4)
            if on_wall and not ghost:
                ax.scatter([x], [j], s=10, color=ORANGE, zorder=5)
    for i in range(nx + 2):
        ax.plot([i - 0.5], [-1.3], alpha=0)
    ax.text(-0.25, ny / 2, "inlet\n$u = 1$", ha="right", va="center", fontsize=8.5, color=BLUE)
    ax.text(nx + 0.95, ny / 2, "outlet\n$p = 0$", ha="left", va="center", fontsize=8.5, color=VIOLET)
    ax.text(nx / 2, ny + 1.15, "ghost row:  $u_{ghost} = -u$", ha="center", va="bottom", fontsize=8, color=MUTED)
    ax.text(nx / 2, -1.15, "ghost row:  $u_{ghost} = -u$", ha="center", va="top", fontsize=8, color=MUTED)
    handles = [plt.Line2D([], [], marker="o", ls="", color=INK, ms=5, label="$p$ at the cell centre"),
               plt.Line2D([], [], marker=r"$\rightarrow$", ls="", color=BLUE, ms=11,
                          label="$u$ on the vertical faces"),
               plt.Line2D([], [], marker=r"$\uparrow$", ls="", color=ORANGE, ms=11,
                          label="$v$ on the horizontal faces"),
               plt.Line2D([], [], marker=r"$\rightarrow$", ls="", color=MUTED, ms=11, label="ghost values")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8.2, handletextpad=0.2,
               columnspacing=1.0, bbox_to_anchor=(0.5, 0.0))
    if title:
        fig.text(0.02, 0.96, title, fontsize=11, fontweight="semibold", color=INK, va="top")
    ax.set_xlim(-1.4, nx + 1.9)
    ax.set_ylim(-1.6, ny + 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()


def checkerboard(xc, yc, p, p_bad, amplitude):
    """A smooth pressure and the same pressure plus a checkerboard (first part of the channel)."""
    fig, axes = plt.subplots(2, 1, figsize=(7.8, 4.7))
    fig.subplots_adjust(left=0.08, right=0.86, bottom=0.17, top=0.92, hspace=0.6)
    low = min(min(r) for r in p_bad)
    high = max(max(r) for r in p_bad)
    for ax, field, title in ((axes[0], p, "converged pressure $p$ (staggered solver)"),
                             (axes[1], p_bad, f"$p$ + {amplitude:g} × checkerboard $(-1)^{{i+j}}$")):
        mesh = ax.pcolormesh([x for x in xc], yc, field, cmap=DIVERGING, vmin=low, vmax=high,
                             shading="nearest")
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_ylabel("y / H")
        ax.set_yticks([0, 0.5, 1])
    axes[1].set_xlabel("x / H")
    cax = fig.add_axes([0.89, 0.14, 0.015, 0.72])
    cb = fig.colorbar(mesh, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8)
    cax.set_title("$p$", fontsize=9, color=INK2)
    fig.text(0.08, 0.015, "On a collocated grid both fields give exactly the same pressure gradient, "
             "(p$_E$ − p$_W$)/(2h), at every node.", fontsize=8.5, color=INK2)
    plt.show()


def history(histories, tol):
    """Steady-state residual and pressure sweeps per time step."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.27, top=0.88, wspace=0.3)
    for Re, (hist, dt) in histories.items():
        t = [dt * (k + 1) for k in range(len(hist))]
        ax1.semilogy(t, [r for r, _ in hist], color=RE_COLORS[Re], lw=1.6, label=_re_label(Re))
        ax2.plot(t, [s for _, s in hist], color=RE_COLORS[Re], lw=1.0)
    ax1.axhline(tol, color=MUTED, lw=1)
    ax1.text(0.3, tol * 1.6, "tolerance", fontsize=8.5, color=INK2)
    ax1.set_title("Distance from the steady state")
    ax1.set_ylabel("largest $|\\Delta u|/\\Delta t$ per step")
    ax2.set_title("Pressure equation")
    ax2.set_ylabel("SOR sweeps per time step")
    for ax in (ax1, ax2):
        ax.set_xlabel("time  $t\\,U/H$")
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    fig.legend(*ax1.get_legend_handles_labels(), loc="lower center", ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def fields(xc, yc, xf, yf, solutions, length):
    """Colour map of u (cell centres) and streamlines (contours of psi at the cell corners)."""
    n = len(solutions)
    fig, axes = plt.subplots(n, 1, figsize=(8.6, 2.1 * n + 0.9))
    fig.subplots_adjust(left=0.07, right=0.88, bottom=0.17 if n > 1 else 0.3, top=0.93, hspace=0.6)
    axes = axes if n > 1 else [axes]
    for ax, (Re, (u, psi)) in zip(axes, solutions.items()):
        cf = ax.contourf(xc, yc, u, levels=[0.1 * k for k in range(17)], cmap=SPEED, extend="max")
        ax.contour(xf, yf, psi, levels=[0.1 * k for k in range(1, 10)], colors=INK, linewidths=0.6)
        ax.set_aspect(2.0)
        ax.set_xlim(0, length)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 1])
        ax.set_title(f"$u / U$,  {_re_label(Re)}")
    axes[-1].set_xlabel("x / H")
    cax = fig.add_axes([0.9, 0.2, 0.012, 0.68])
    cb = fig.colorbar(cf, cax=cax, ticks=[0, 0.5, 1, 1.5])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8)
    fig.text(0.07, 0.02, "black lines: streamlines, 10 % of the flow between two neighbouring lines"
             "   (y stretched 2×)", fontsize=8, color=INK2)
    plt.show()


def profiles(y, cuts, exact):
    """u(y) at several stations x, for each Reynolds number, with the Poiseuille parabola."""
    n = len(cuts)
    fig, axes = plt.subplots(1, n, figsize=(4.1 * n, 3.9), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.28, top=0.9, wspace=0.12)
    axes = axes if n > 1 else [axes]
    for ax, (Re, stations) in zip(axes, cuts.items()):
        for k, (x, u) in enumerate(stations.items()):
            ax.plot(u, y, color=STEPS[min(1 + k, 6)], lw=1.7, marker="o", ms=2.6, label=f"x = {x:g} H")
        ys = [k / 100 for k in range(101)]
        ax.plot([exact(t) for t in ys], ys, color=RED, lw=1.1, ls="--", label="Poiseuille (exact)")
        ax.set_title(_re_label(Re))
        ax.set_xlabel("u / U")
        ax.set_xlim(0, 1.6)
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("y / H")
    fig.legend(*axes[-1].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def centreline(x, lines, lengths, durst, developed):
    """Centre-line velocity along the channel, with the entrance lengths (FDM and correlation)."""
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.27, top=0.9)
    for Re, uc in lines.items():
        color = RE_COLORS[Re]
        ax.plot(x, uc, color=color, lw=1.9, label=f"FDM, {_re_label(Re)}")
        ax.axvline(lengths[Re], color=color, lw=1.0, ls="--")
        ax.scatter([durst[Re]], [0.99 * developed[Re]], s=40, marker="s", fc="white", ec=color, lw=1.4,
                   zorder=5)
        ax.text(lengths[Re] + 0.08, 1.06, f"$L_e$ = {lengths[Re]:.2f} H", fontsize=8.5, color=color,
                rotation=90, va="bottom")
    ax.scatter([], [], s=40, marker="s", fc="white", ec=INK2, lw=1.4, label="Durst et al. (2005)")
    ax.axhline(1.5, color=RED, lw=1.0, ls=":", label="fully developed, 1.5 U")
    ax.set_xlabel("x / H")
    ax.set_ylabel("$u$ on the centre line / U")
    ax.set_ylim(0.98, 1.56)
    ax.set_xlim(0, max(x))
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Centre-line velocity: how the flow develops")
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def pressure(x, lines, length):
    """Centre-line pressure along the channel, with the fully developed straight line."""
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.27, top=0.9)
    for Re, pc in lines.items():
        color = RE_COLORS[Re]
        ax.plot(x, pc, color=color, lw=1.9, label=f"FDM, {_re_label(Re)}")
        ax.plot([0, length], [12 / Re * length, 0], color=color, lw=1.0, ls="--")
    ax.plot([], [], color=INK2, lw=1.0, ls="--", label="fully developed: $dp/dx = -12/Re$")
    ax.set_xlabel("x / H")
    ax.set_ylabel("$p$ on the centre line / $\\rho U^2$")
    ax.set_xlim(0, length)
    ax.set_ylim(0, None)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_title("Pressure along the channel")
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def grid_study(hs, values, extrapolated, durst):
    """Entrance length and outlet centre-line velocity on each grid."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 3.5))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.3, top=0.88, wspace=0.35)
    h2 = [h * h for h in hs]
    ax1.plot(h2, [v["Le"] for v in values], color=BLUE, lw=1.8, marker="o", ms=6, mec="white", label="FDM")
    ax1.scatter([0], [extrapolated], s=46, marker="*", color=BLUE, zorder=5, label="Richardson")
    ax1.axhline(durst, color=RED, lw=1.1, ls="--", label="Durst et al. (2005)")
    ax1.set_ylabel("$L_e$ / H")
    ax1.set_title("Entrance length")
    ax2.plot(h2, [v["uc"] for v in values], color=BLUE, lw=1.8, marker="o", ms=6, mec="white")
    ax2.axhline(1.5, color=RED, lw=1.1, ls=":", label="exact, 1.5")
    ax2.set_ylabel("$u$ on the centre line / U")
    ax2.set_title("Fully developed centre velocity")
    for ax in (ax1, ax2):
        ax.set_xlabel("$h^2$  (h = H/8, H/16, H/32)")
        ax.set_xlim(-0.0008, max(h2) * 1.08)
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    handles = ax1.get_legend_handles_labels()
    extra = ax2.get_legend_handles_labels()
    fig.legend(handles[0] + extra[0], handles[1] + extra[1], loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def hand_grid(u, v, p, title):
    """The 2 x 3 hand grid: p in the cells (black), u (blue) and v (orange) on the faces."""
    ny = len(p) - 2
    nx = len(p[0]) - 2
    s = 2.4
    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.92)
    for k in range(nx + 1):
        ax.plot([k * s, k * s], [0, ny * s], color=GRID, lw=1.0, zorder=1)
    for k in range(ny + 1):
        ax.plot([0, nx * s], [k * s, k * s], color=GRID, lw=1.0, zorder=1)
    for y in (0, ny * s):
        ax.add_patch(Rectangle((0, y - (0.12 if y == 0 else 0)), nx * s, 0.12, fc=INK2, ec="none", zorder=2))
    ax.plot([0, 0], [0, ny * s], color=BLUE, lw=2.6, zorder=2)
    ax.plot([nx * s, nx * s], [0, ny * s], color=VIOLET, lw=2.6, zorder=2)
    for j in range(1, ny + 1):
        for i in range(1, nx + 1):
            xc, yc = (i - 0.5) * s, (j - 0.5) * s
            ax.scatter([xc], [yc], s=26, color=INK, zorder=4)
            ax.text(xc, yc - 0.18, f"{p[j][i] + 0.0:.5f}", ha="center", va="top", fontsize=9, color=INK)
            ax.text(xc, yc + 0.18, f"cell ({i},{j})", ha="center", va="bottom", fontsize=7.5, color=MUTED)
    for j in range(1, ny + 1):
        for i in range(0, nx + 1):
            x, y = i * s, (j - 0.5) * s
            _arrow(ax, (x - 0.25, y), (x + 0.25, y), color=BLUE, lw=1.3, scale=9)
            ha = "left" if i < nx else "right"
            ax.text(x + (0.08 if i < nx else -0.08), y + 0.12, f"{u[j][i] + 0.0:.5f}", ha=ha, va="bottom",
                    fontsize=8.5, color=BLUE, rotation=0)
    for j in range(0, ny + 1):
        for i in range(1, nx + 1):
            x, y = (i - 0.5) * s, j * s
            _arrow(ax, (x, y - 0.25), (x, y + 0.25), color=ORANGE, lw=1.3, scale=9)
            ax.text(x + 0.1, y + (0.06 if j < ny else -0.06), f"{v[j][i] + 0.0:.5f}", ha="left",
                    va="bottom" if j < ny else "top", fontsize=8.5, color=ORANGE)
    ax.text(-0.15, ny * s / 2, "inlet\n$u = 1$", ha="right", va="center", fontsize=9, color=BLUE)
    ax.text(nx * s + 0.15, ny * s / 2, "outlet\n$p = 0$", ha="left", va="center", fontsize=9, color=VIOLET)
    fig.text(0.02, 0.95, title, fontsize=11, fontweight="semibold", color=INK)
    fig.text(0.98, 0.95, "black: p   blue: u   orange: v", ha="right", fontsize=8.5, color=INK2)
    ax.set_xlim(-1.5, nx * s + 1.5)
    ax.set_ylim(-0.5, ny * s + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()
