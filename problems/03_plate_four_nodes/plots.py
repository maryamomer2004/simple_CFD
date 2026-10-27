"""Drawing helpers for Problem 3 (the square plate with four interior nodes).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
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

NODE_COLORS = {1: BLUE, 2: ORANGE, 3: AQUA, 4: VIOLET}   # one colour per node, in every figure
T_MIN, T_MAX = 100.0, 700.0                              # colour scale of every temperature map


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def _edges(ax, T_top, T_left, T_right, T_bottom, size=3, width=0.09):
    """Coloured bars along the four edges, labelled with their temperature."""
    norm = Normalize(T_MIN, T_MAX)
    for (x, y, w, h), T in (((0, size, size, width), T_top), ((0, -width, size, width), T_bottom),
                            ((-width, 0, width, size), T_left), ((size, 0, width, size), T_right)):
        ax.add_patch(Rectangle((x, y), w, h, color=HEAT(norm(T)), lw=0, zorder=3))


def schematic(T_top, T_left, T_right, T_bottom):
    """The plate as in the textbook figure: 3 x 3 squares, four interior nodes."""
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    ax.set_xlim(-1.3, 4.3)
    ax.set_ylim(-0.75, 3.75)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 3, 3, fc="#fbe7ef", ec="none", zorder=1))
    for v in range(4):
        ax.plot([v, v], [0, 3], color="#c9a3b4", lw=1.0, zorder=2)
        ax.plot([0, 3], [v, v], color="#c9a3b4", lw=1.0, zorder=2)
    _edges(ax, T_top, T_left, T_right, T_bottom)
    for n, (i, j) in {4: (1, 2), 1: (2, 2), 2: (1, 1), 3: (2, 1)}.items():
        ax.scatter(i, j, s=55, color=INK, zorder=5)
        ax.text(i - 0.08, j + 0.1, str(n), ha="right", va="bottom", fontsize=12, fontweight="semibold",
                zorder=5)
    ax.text(1.5, 3.25, f"{T_top:g} °C", ha="center", va="bottom", fontsize=11)
    ax.text(1.5, -0.25, f"{T_bottom:g} °C", ha="center", va="top", fontsize=11)
    ax.text(-0.25, 1.5, f"{T_left:g} °C", ha="right", va="center", fontsize=11)
    ax.text(3.25, 1.5, f"{T_right:g} °C", ha="left", va="center", fontsize=11)
    _arrow(ax, (2, -0.5), (3, -0.5), style="<->", lw=1.0, scale=8)
    ax.text(2.5, -0.58, r"$\Delta x$", ha="center", va="top", fontsize=10)
    _arrow(ax, (3.62, 2), (3.62, 3), style="<->", lw=1.0, scale=8)
    ax.text(3.7, 2.5, r"$\Delta y = \Delta x$", ha="left", va="center", fontsize=10)
    plt.show()


def grid(M, nodes, boundary_value):
    """Grid indices (i, j), the known boundary nodes, the unused corners and one stencil."""
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    ax.set_xlim(-1.0, M + 2.4)
    ax.set_ylim(-0.9, M + 0.6)
    ax.set_aspect("equal")
    ax.axis("off")
    for v in range(M + 1):
        ax.plot([v, v], [0, M], color=GRID, lw=1.0, zorder=1)
        ax.plot([0, M], [v, v], color=GRID, lw=1.0, zorder=1)
    for j in range(M + 1):
        for i in range(M + 1):
            T = boundary_value(i, j, M)
            if T is not None:
                ax.scatter(i, j, s=150, marker="s", color=HEAT(Normalize(T_MIN, T_MAX)(T)), ec=INK2,
                           lw=0.8, zorder=3)
                ax.text(i + 0.13, j + 0.13, f"{T:g}", fontsize=8, color=INK2, zorder=4)
    for i, j in ((0, 0), (M, 0), (0, M), (M, M)):
        ax.scatter(i, j, s=70, marker="x", color=MUTED, lw=1.5, zorder=3)
    # the stencil of node 1
    i1, j1 = nodes[1]
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ax.plot([i1, i1 + di], [j1, j1 + dj], color=BLUE, lw=3.0, alpha=0.55, zorder=2)
    for n, (i, j) in nodes.items():
        ax.scatter(i, j, s=260, color=NODE_COLORS[n], ec="white", lw=1.5, zorder=5)
        ax.text(i, j, str(n), ha="center", va="center", fontsize=10, color="white",
                fontweight="bold", zorder=6)
    for v in range(M + 1):
        ax.text(v, -0.35, str(v), ha="center", va="top", fontsize=9.5, color=INK)
        ax.text(-0.35, v, str(v), ha="right", va="center", fontsize=9.5, color=INK)
    ax.text(M / 2, -0.7, "i  (x direction)", ha="center", va="top", fontsize=9, color=INK2)
    ax.text(-0.8, M / 2, "j  (y direction)", ha="center", va="center", rotation=90, fontsize=9,
            color=INK2)
    legend = [("s", HEAT(0.6), "boundary node (known T, °C)"), ("o", BLUE, "interior node (unknown)"),
              ("x", MUTED, "corner: never used")]
    for k, (marker, color, text) in enumerate(legend):
        y = M - 0.2 - 0.45 * k
        ax.scatter(M + 0.55, y, s=60 if marker != "x" else 40, marker=marker, color=color,
                   ec=INK2 if marker == "s" else None, lw=0.8 if marker == "s" else 1.5)
        ax.text(M + 0.8, y, text, va="center", fontsize=8.5, color=INK)
    ax.text(M + 0.45, 0.85, "blue lines: the 5-point\nstencil of node 1", fontsize=8.5, color=INK2,
            va="center")
    plt.show()


def iterations(table, tol_changes):
    """Gauss-Seidel: the four temperatures settle down iteration by iteration."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.17, top=0.88, wspace=0.42)
    its = list(range(len(table)))
    for k, n in enumerate((1, 2, 3, 4)):
        values = [row[k] for row in table]
        ax1.plot(its, values, color=NODE_COLORS[n], lw=1.8, marker="o", ms=3.5)
        ax1.text(its[-1] + 0.3, values[-1], f"$T_{n}$", va="center", fontsize=10, color=INK)
    ax1.set_xlabel("iteration")
    ax1.set_ylabel("T [°C]")
    ax1.set_xlim(0, its[-1] + 1.2)
    ax1.set_title("Gauss–Seidel iterations")
    ax1.grid(axis="y", color=GRID, lw=0.6)
    ax1.set_axisbelow(True)
    changes, tol = tol_changes
    ax2.semilogy(range(1, len(changes) + 1), changes, color=BLUE, lw=1.8, marker="o", ms=3.5)
    ax2.axhline(tol, color=MUTED, lw=1)
    ax2.text(1, tol * 2, "tolerance", fontsize=8.5, color=INK2)
    ax2.set_xlabel("iteration")
    ax2.set_ylabel("largest change [°C]")
    ax2.set_title("Each iteration: error ÷ 4")
    plt.show()


def plate(T_nodes, T_top, T_left, T_right, T_bottom, flows):
    """Left: the four temperatures on the plate. Right: discrete heat flow through every edge."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.9))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.03, top=0.9, wspace=0.08)
    norm = Normalize(T_MIN, T_MAX)
    positions = {4: (1, 2), 1: (2, 2), 2: (1, 1), 3: (2, 1)}
    for ax in (ax1, ax2):
        ax.set_xlim(-1.25, 4.25)
        ax.set_ylim(-0.95, 3.95)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), 3, 3, fc=SURFACE, ec="none"))
        for v in range(4):
            ax.plot([v, v], [0, 3], color=GRID, lw=1.0, zorder=1)
            ax.plot([0, 3], [v, v], color=GRID, lw=1.0, zorder=1)
        _edges(ax, T_top, T_left, T_right, T_bottom)
    ax1.set_title("Temperatures at the four nodes")
    for n, (i, j) in positions.items():
        ax1.scatter(i, j, s=1250, color=HEAT(norm(T_nodes[n])), ec="white", lw=2, zorder=4)
        ax1.text(i, j + 0.06, f"{T_nodes[n]:.1f}", ha="center", va="center", fontsize=9.5,
                 fontweight="semibold", color="white" if norm(T_nodes[n]) > 0.55 else INK, zorder=5)
        ax1.text(i, j - 0.22, f"node {n}", ha="center", va="center", fontsize=7.5,
                 color="white" if norm(T_nodes[n]) > 0.55 else INK2, zorder=5)
    for (x, y, ha, va), T in (((1.5, 3.2, "center", "bottom"), T_top), ((1.5, -0.2, "center", "top"), T_bottom),
                              ((-0.2, 1.5, "right", "center"), T_left), ((3.2, 1.5, "left", "center"), T_right)):
        ax1.text(x, y, f"{T:g} °C", ha=ha, va=va, fontsize=9.5, color=INK2)
    ax2.set_title("Heat flow through each edge,  q′/k  [K]")
    scale = 0.0017
    for edge, (x, y, dx, dy) in {"top": (1.5, 3.12, 0, 1), "bottom": (1.5, -0.12, 0, -1),
                                 "left": (-0.12, 1.5, -1, 0), "right": (3.12, 1.5, 1, 0)}.items():
        q = flows[edge]                        # positive = into the plate
        length = 0.25 + scale * abs(q)
        tail = (x + dx * length, y + dy * length) if q > 0 else (x, y)
        head = (x, y) if q > 0 else (x + dx * length, y + dy * length)
        _arrow(ax2, tail, head, color=RED if q > 0 else BLUE, lw=2.4, scale=16)
        if dx == 0:   # top and bottom: label beside the arrow, so it stays clear of the title
            tx, ty, ha, va = x + 0.15, y + dy * length / 2, "left", "center"
        else:
            tx, ty = x + dx * (length + 0.12), y
            ha, va = ("right" if dx < 0 else "left"), "center"
        ax2.text(tx, ty, f"{'in' if q > 0 else 'out'}\n{abs(q):.1f}", ha=ha, va=va, fontsize=9, color=INK)
    ax2.text(1.5, 1.5, f"in − out\n= {sum(flows.values()):.1f}", ha="center", va="center",
             fontsize=10, color=INK)
    plt.show()


def field(T, M, coarse, locations):
    """Colour map of the fine-grid temperature field, with the four node locations."""
    fig = plt.figure(figsize=(6.6, 4.6))
    ax = fig.add_axes([0.08, 0.1, 0.62, 0.82])
    xs = [i / M for i in range(M + 1)]
    levels = [100 + 25 * k for k in range(25)]
    cf = ax.contourf(xs, xs, T, levels=levels, cmap=HEAT, vmin=T_MIN, vmax=T_MAX)
    ax.contour(xs, xs, T, levels=list(range(150, 700, 50)), colors=INK, linewidths=0.5, alpha=0.45)
    for n, (x, y) in locations.items():
        fine = T[round(y * M)][round(x * M)]
        ax.scatter(x, y, s=70, color=NODE_COLORS[n], ec="white", lw=1.5, zorder=4)
        ax.text(x + 0.025, y + 0.03, f"{n}: {fine:.1f}", fontsize=9, fontweight="semibold", zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_aspect("equal")
    ax.set_xlabel("x / side length")
    ax.set_ylabel("y / side length")
    ax.set_xticks([0, 1 / 3, 2 / 3, 1], ["0", "1/3", "2/3", "1"])
    ax.set_yticks([0, 1 / 3, 2 / 3, 1], ["0", "1/3", "2/3", "1"])
    ax.set_title(f"Fine grid: {M} × {M} squares, isotherms every 50 °C")
    cax = fig.add_axes([0.74, 0.1, 0.03, 0.82])
    cb = fig.colorbar(cf, cax=cax, ticks=[100, 200, 300, 400, 500, 600, 700])
    cb.outline.set_visible(False)
    cb.set_label("T [°C]", color=INK2)
    fig.text(0.85, 0.9, "coarse grid\n(4 nodes):", fontsize=8.5, color=INK2, va="top")
    for k, n in enumerate((1, 2, 3, 4)):
        fig.text(0.85, 0.8 - 0.06 * k, f"{n}: {coarse[n]:.1f}", fontsize=9, color=INK, va="top")
    plt.show()


def grid_study(Ms, values, exact):
    """Temperature at the four node locations as the grid is refined."""
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    fig.subplots_adjust(left=0.11, right=0.8, bottom=0.15, top=0.88)
    for n in (1, 2, 3, 4):
        err = [values[M][n] - exact[n] for M in Ms]
        ax.plot(Ms, err, color=NODE_COLORS[n], lw=1.8, marker="o", ms=6, mec="white")
        ax.text(Ms[0] * 0.93, err[0], f"node {n}", ha="right", va="center", fontsize=9, color=INK)
    ax.axhline(0, color=INK, lw=1)
    ax.text(Ms[-1] * 1.08, 0, "exact\nsolution", va="center", fontsize=9, color=INK)
    ax.set_xscale("log", base=2)
    ax.set_xticks(Ms, [str(M) for M in Ms])
    ax.minorticks_off()
    ax.set_xlim(Ms[0] * 0.55, Ms[-1] * 1.5)
    ax.set_xlabel("squares per side  M")
    ax.set_ylabel("FDM − exact  [°C]")
    ax.set_title("Refining the grid: every node converges to the exact value")
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    plt.show()
