"""Drawing helpers for Problem 4 (the fireclay brick column).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
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

BRICK = "#f4dccb"
# grid position (column i, row j) of the eight unknown nodes; row 0 is the bottom surface
NODE_IJ = {1: (1, 3), 2: (2, 3), 3: (1, 2), 4: (2, 2), 5: (1, 1), 6: (2, 1), 7: (1, 0), 8: (2, 0)}
MIRROR_IJ = {1: (3, 3), 3: (3, 2), 5: (3, 1), 7: (3, 0)}


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def _full_field(T, T_s):
    """5 x 5 nodal field (rows from the bottom) built from the eight unknowns and the walls."""
    field = [[T_s] * 5 for _ in range(5)]
    for node, (i, j) in NODE_IJ.items():
        field[j][i] = T[node - 1]
    for node, (i, j) in MIRROR_IJ.items():
        field[j][i] = T[node - 1]
    return field


def schematic(W, T_s, T_inf, h, k):
    """Cross-section of the column with its boundary conditions."""
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    ax.set_xlim(-0.55, 2.4)
    ax.set_ylim(-0.52, 1.32)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, W, fc=BRICK, ec="none"))
    for (x0, y0), (x1, y1) in (((0, 1), (1, 1)), ((0, 0), (0, 1)), ((1, 0), (1, 1))):
        ax.plot([x0, x1], [y0, y1], color=RED, lw=5, solid_capstyle="butt")
    ax.plot([0, 1], [0, 0], color=BLUE, lw=2.5, solid_capstyle="butt")
    ax.text(0.5, 1.07, f"$T_s$ = {T_s:g} K", ha="center", va="bottom", fontsize=10)
    ax.text(-0.07, 0.5, f"$T_s$ = {T_s:g} K", ha="right", va="center", fontsize=10)
    ax.text(1.07, 0.5, f"$T_s$ = {T_s:g} K", ha="left", va="center", fontsize=10)
    ax.text(0.5, 0.55, "fireclay brick", ha="center", va="center", fontsize=10.5, fontweight="semibold")
    ax.text(0.5, 0.42, f"$k$ = {k:g} W/(m·K)", ha="center", va="center", fontsize=9.5, color=INK2)
    for yy in (-0.13, -0.23):
        _arrow(ax, (0.05, yy), (0.95, yy), color=BLUE, lw=1.4)
    ax.text(0.5, -0.31, f"air:  $T_\\infty$ = {T_inf:g} K,  $h$ = {h:g} W/(m²·K)", ha="center",
            va="top", fontsize=9.5)
    _arrow(ax, (0, 1.24), (1, 1.24), style="<->", lw=1.0, scale=8)
    ax.text(0.5, 1.25, f"{W:g} m", ha="center", va="bottom", fontsize=9, color=INK2,
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
    ax.text(1.93, 0.78, "cross-section of a\nlong column", ha="center", va="center", fontsize=9.5,
            fontweight="semibold")
    ax.text(1.93, 0.42, "the temperature does not\nchange along the column\n→ a 2D problem in x and y",
            ha="center", va="center", fontsize=8.8, color=INK2)
    ax.text(1.93, 0.02, "three sides hot (500 K),\nbottom cooled by air", ha="center", va="center",
            fontsize=8.8, color=INK2)
    plt.show()


def grid(W, dx):
    """The 5 x 5 grid, the node numbers and the symmetry line."""
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    ax.set_xlim(-0.3, 2.0)
    ax.set_ylim(-0.25, 1.22)
    ax.set_aspect("equal")
    ax.axis("off")
    n = round(W / dx)
    ax.add_patch(Rectangle((0, 0), W, W, fc=BRICK, ec="none", alpha=0.6))
    for v in range(n + 1):
        ax.plot([v * dx, v * dx], [0, W], color="#c9b3a3", lw=0.8, zorder=1)
        ax.plot([0, W], [v * dx, v * dx], color="#c9b3a3", lw=0.8, zorder=1)
    ax.plot([0.5 * W] * 2, [-0.08, W + 0.08], color=VIOLET, lw=1.4, ls=(0, (6, 2, 1, 2)), zorder=2)
    ax.text(0.5 * W, W + 0.1, "symmetry line", ha="center", va="bottom", fontsize=8.5, color=VIOLET)
    known = [(i, n) for i in range(n + 1)] + [(0, j) for j in range(n)] + [(n, j) for j in range(n)]
    ax.scatter([i * dx for i, _ in known], [j * dx for _, j in known], marker="s", s=34, color=RED,
               ec="white", lw=1, zorder=4)
    for node, (i, j) in NODE_IJ.items():
        color = AQUA if j == 0 else BLUE
        ax.scatter(i * dx, j * dx, s=90, color=color, ec="white", lw=1.4, zorder=5)
        ax.text(i * dx + 0.035, j * dx + 0.035, str(node), fontsize=10, fontweight="bold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    for node, (i, j) in MIRROR_IJ.items():
        color = AQUA if j == 0 else BLUE
        ax.scatter(i * dx, j * dx, s=90, fc="white", ec=color, lw=1.6, zorder=5)
        ax.text(i * dx + 0.035, j * dx + 0.035, str(node), fontsize=10, color=MUTED, zorder=6,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    _arrow(ax, (0, -0.1), (dx, -0.1), style="<->", lw=1.0, scale=7)
    ax.text(dx / 2, -0.13, r"$\Delta x$ = 0.25 m", ha="center", va="top", fontsize=9)
    _arrow(ax, (-0.1, W - dx), (-0.1, W), style="<->", lw=1.0, scale=7)
    ax.text(-0.13, W - dx / 2, r"$\Delta y$", ha="right", va="center", fontsize=9)
    handles = [
        Line2D([], [], ls="", marker="o", ms=9, color=BLUE, mec="white", label="unknown interior node"),
        Line2D([], [], ls="", marker="o", ms=9, color=AQUA, mec="white", label="unknown surface node\n(convection)"),
        Line2D([], [], ls="", marker="o", ms=9, mfc="white", mec=BLUE, mew=1.6,
               label="mirror image of a node\n(same temperature)"),
        Line2D([], [], ls="", marker="s", ms=7, color=RED, mec="white", label="known temperature, 500 K"),
        Line2D([], [], color=VIOLET, lw=1.4, ls=(0, (6, 2, 1, 2)), label="symmetry line"),
    ]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(0.57, 0.5), fontsize=9,
              labelspacing=1.0, handletextpad=0.6)
    plt.show()


def control_volumes():
    """Energy balances on the three kinds of control volume used in this problem."""
    fig, axes = plt.subplots(1, 3, figsize=(7.8, 3.6))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.17, top=0.88, wspace=0.08)
    titles = ["Interior node", "Surface node (convection)", "Node on the symmetry line"]
    equations = [r"$T_W+T_E+T_N+T_S-4\,T_P=0$",
                 r"$T_W+T_E+2\,T_N+2\,Bi\,T_\infty-2\,(Bi+2)\,T_P=0$",
                 r"$T_E=T_W$  (mirror node)"]
    for ax, title, eq in zip(axes, titles, equations):
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.35)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, loc="center", fontsize=10)
        fig.text(ax.get_position().x0 + ax.get_position().width / 2, 0.08, eq, ha="center",
                 va="center", fontsize=9.5)

    def node(ax, x, y, color, label, hollow=False, dx=0.1, dy=0.12):
        if hollow:
            ax.scatter(x, y, s=80, fc="white", ec=color, lw=1.6, zorder=5)
        else:
            ax.scatter(x, y, s=80, color=color, ec="white", lw=1.3, zorder=5)
        ax.text(x + dx, y + dy, label, fontsize=9.5, zorder=6)

    # interior node
    ax = axes[0]
    ax.add_patch(Rectangle((-0.5, -0.5), 1, 1, fc=ORANGE, alpha=0.15, ec=ORANGE, lw=1.2, ls=(0, (4, 2))))
    node(ax, 0, 0, ORANGE, "P")
    for (x, y, lab) in ((1, 0, "E"), (-1, 0, "W"), (0, 1, "N"), (0, -1, "S")):
        node(ax, x, y, BLUE, lab)
        _arrow(ax, (0.75 * x, 0.75 * y), (0.3 * x, 0.3 * y), color=INK2, lw=1.4, scale=10)
    ax.text(0.55, -0.62, r"$k\,(T_E-T_P)$", fontsize=8.5, color=INK2, ha="center", va="top")

    # surface node with convection
    ax = axes[1]
    ax.add_patch(Rectangle((-1.3, -0.55), 2.6, 0.55, fc="#e3eefc", ec="none"))
    ax.plot([-1.3, 1.3], [0, 0], color=BLUE, lw=2)
    ax.add_patch(Rectangle((-0.5, 0), 1, 0.5, fc=ORANGE, alpha=0.15, ec=ORANGE, lw=1.2, ls=(0, (4, 2))))
    node(ax, 0, 0, ORANGE, "P", dy=0.1)
    node(ax, 1, 0, AQUA, "E", dy=0.1)
    node(ax, -1, 0, AQUA, "W", dy=0.1)
    node(ax, 0, 1, BLUE, "N")
    _arrow(ax, (-0.78, 0.22), (-0.32, 0.22), lw=1.4, scale=10)
    _arrow(ax, (0.78, 0.22), (0.32, 0.22), lw=1.4, scale=10)
    _arrow(ax, (0, 0.78), (0, 0.32), lw=1.4, scale=10)
    _arrow(ax, (0.22, -0.05), (0.22, -0.48), color=BLUE, lw=1.6, scale=10)
    ax.text(0.32, -0.3, r"$h\,\Delta x\,(T_P-T_\infty)$", fontsize=8.5, color=INK2, va="center")
    ax.text(-0.55, 0.62, r"$\frac{k}{2}(T_W-T_P)$", fontsize=8.5, color=INK2, ha="center")
    ax.text(0, -0.75, r"air, $T_\infty$", fontsize=9, color=BLUE, ha="center", va="top")
    ax.text(0, -1.0, "half cell: side faces only Δy/2 high", fontsize=8, color=INK2, ha="center", va="top")

    # node on the symmetry line
    ax = axes[2]
    ax.plot([0, 0], [-1.25, 1.25], color=VIOLET, lw=1.4, ls=(0, (6, 2, 1, 2)))
    ax.add_patch(Rectangle((-0.5, -0.5), 1, 1, fc=ORANGE, alpha=0.15, ec=ORANGE, lw=1.2, ls=(0, (4, 2))))
    node(ax, 0, 0, ORANGE, "P")
    node(ax, -1, 0, BLUE, "W")
    node(ax, 1, 0, BLUE, "E = W", hollow=True, dx=-0.3, dy=0.16)
    node(ax, 0, 1, BLUE, "N")
    node(ax, 0, -1, BLUE, "S")
    ax.text(0.08, -1.3, "symmetry", fontsize=8.5, color=VIOLET, va="bottom")
    ax.text(1.0, -0.32, "mirror\nimage", fontsize=8, color=MUTED, ha="center", va="top")
    plt.show()


def iterations(history, changes, tol):
    """Gauss-Seidel: node temperatures and the largest change per iteration."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.2, 1]})
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.17, top=0.88, wspace=0.42)
    its = list(range(len(history)))
    for node, color in zip((2, 4, 6, 8), (BLUE, ORANGE, AQUA, VIOLET)):
        ax1.plot(its, [T[node - 1] for T in history], color=color, lw=1.8, marker="o", ms=3)
        ax1.text(its[-1] + 0.6, history[-1][node - 1], f"node {node}", va="center", fontsize=8.5)
    ax1.set_xlim(0, its[-1] + 4)
    ax1.set_xlabel("iteration")
    ax1.set_ylabel("T [K]")
    ax1.set_title("Nodes on the symmetry line")
    ax2.semilogy(range(1, len(changes) + 1), changes, color=BLUE, lw=1.8, marker="o", ms=3)
    ax2.axhline(tol, color=MUTED, lw=1)
    ax2.text(len(changes) * 0.5, tol * 1.8, "tolerance", ha="center", fontsize=8.5, color=INK2)
    ax2.set_xlabel("iteration")
    ax2.set_ylabel("largest change [K]")
    ax2.set_title("Convergence")
    plt.show()


def temperature_map(T, T_s, T_inf, W, dx):
    """Full cross-section: interpolated colour map with the nodal temperatures written on it."""
    field = _full_field(T, T_s)
    xs = [i * dx for i in range(5)]
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    fig.subplots_adjust(left=0.1, right=0.9, bottom=0.12, top=0.9)
    cf = ax.contourf(xs, xs, field, levels=[T_inf + 10 * v for v in range(21)], cmap=HEAT)
    for v in range(5):
        ax.plot([v * dx] * 2, [0, W], color="white", lw=0.6, alpha=0.6)
        ax.plot([0, W], [v * dx] * 2, color="white", lw=0.6, alpha=0.6)
    for node, (i, j) in list(NODE_IJ.items()) + list(MIRROR_IJ.items()):
        ax.text(i * dx, j * dx + (0.035 if j > 0 else 0.045), f"{field[j][i]:.1f}", ha="center",
                va="bottom", fontsize=8.5, color=INK, bbox=dict(boxstyle="round,pad=0.15", fc="white",
                                                                ec="none", alpha=0.85))
        ax.scatter(i * dx, j * dx, s=22, color=INK, zorder=4)
    ax.plot([0, W], [0, 0], color=BLUE, lw=3, clip_on=False)
    ax.set_aspect("equal")
    ax.set_xlim(0, W)
    ax.set_ylim(0, W)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Temperature in the whole cross-section [K]")
    cb = fig.colorbar(cf, ax=ax, fraction=0.05, pad=0.04, ticks=[300, 350, 400, 450, 500])
    cb.outline.set_visible(False)
    cb.set_label("T [K]", color=INK2)
    ax.text(W / 2, -0.17, "cooled by air", ha="center", va="top", fontsize=8.5, color=BLUE)
    plt.show()


def refinement(dxs, qs, T_centre):
    """Grid-refinement study: heat rate and bottom-centre temperature against grid spacing."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.3))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.18, top=0.86, wspace=0.38)
    for ax, values, color, title, unit in ((ax1, qs, ORANGE, "Heat rate to the air, q′", "W/m"),
                                           (ax2, T_centre, BLUE, "Temperature at the bottom centre", "K")):
        ax.semilogx(dxs, values, color=color, lw=1.8, marker="o", ms=6, mec="white")
        ax.set_xticks(dxs, [f"1/{round(1 / v)}" for v in dxs], fontsize=8.5)
        ax.minorticks_off()
        ax.invert_xaxis()
        ax.set_xlabel("grid spacing Δx [m]   (finer →)")
        ax.set_ylabel(f"[{unit}]")
        ax.set_title(title)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.annotate(f"{values[0]:.1f}", (dxs[0], values[0]), xytext=(8, -4), textcoords="offset points",
                    fontsize=8.5, va="top")
        ax.annotate(f"{values[-1]:.1f}", (dxs[-1], values[-1]), xytext=(-8, 8), textcoords="offset points",
                    fontsize=8.5, ha="right")
    plt.show()


def fine_solution(T_fine, W, T_inf, T_s, bottoms):
    """Fine-grid temperature field and the bottom-surface temperature on several grids."""
    n = len(T_fine) - 1
    xs = [W * i / n for i in range(n + 1)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.6), gridspec_kw={"width_ratios": [1, 1.1]})
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.86, wspace=0.35)
    cf = ax1.contourf(xs, xs, T_fine, levels=[T_inf + 10 * v for v in range(21)], cmap=HEAT)
    cs = ax1.contour(xs, xs, T_fine, levels=[340, 380, 420, 460, 490], colors=INK, linewidths=0.6)
    ax1.clabel(cs, fmt="%d K", fontsize=7.5)
    ax1.set_aspect("equal")
    ax1.set_xlabel("x [m]")
    ax1.set_ylabel("y [m]")
    ax1.set_title(f"Fine grid ({n} × {n} intervals)")
    cb = fig.colorbar(cf, ax=ax1, fraction=0.046, pad=0.04, ticks=[300, 400, 500])
    cb.outline.set_visible(False)
    for (n_c, Tb), color in zip(bottoms.items(), (ORANGE, AQUA, BLUE)):
        xb = [W * i / n_c for i in range(n_c + 1)]
        ax2.plot(xb, Tb, color=color, lw=1.8, marker="o" if n_c <= 16 else None, ms=4,
                 label=f"Δx = {W / n_c:g} m")
    ax2.axhline(T_inf, color=MUTED, lw=1)
    ax2.text(0.5, T_inf + 4, "air temperature", ha="center", fontsize=8, color=INK2)
    ax2.set_xlim(0, W)
    ax2.set_ylim(T_inf - 10, T_s + 10)
    ax2.set_xlabel("x [m]")
    ax2.set_ylabel("T at the bottom surface [K]")
    ax2.set_title("Bottom-surface temperature")
    ax2.grid(axis="y", color=GRID, lw=0.6)
    ax2.set_axisbelow(True)
    ax2.legend(loc="upper center", fontsize=8.5)
    plt.show()
