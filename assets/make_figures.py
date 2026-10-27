#!/usr/bin/env python3
"""Generate every figure used in the README.

Each figure is drawn twice, once for GitHub's light theme and once for its dark
theme, and saved as ``assets/images/<name>_<theme>.svg`` (or ``.gif``). The
README picks the matching file with a ``<picture>`` element.

Every field shown in the figures is computed here with the finite difference
method, so this script doubles as a collection of small worked examples.

Usage (from the repository root)::

    pip install -r requirements.txt
    python assets/make_figures.py
"""

from pathlib import Path

import numpy as np
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.tri as mtri  # noqa: E402
import scipy.sparse as sp  # noqa: E402
import scipy.sparse.linalg as spla  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgb  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Patch, Rectangle  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402
from PIL import Image  # noqa: E402

OUT = Path(__file__).resolve().parent / "images"

# --------------------------------------------------------------------------- #
#  Themes: GitHub canvas colours + a colour-blind-safe categorical palette     #
# --------------------------------------------------------------------------- #
THEMES = {
    "light": {
        "page": "#ffffff", "surface": "#f6f8fa", "border": "#d1d9e0",
        "ink": "#1f2328", "ink2": "#59636e", "muted": "#818b98",
        "grid": "#d8dee4", "axis": "#afb8c1", "solid": "#d1d9e0",
        "blue": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "violet": "#6250d6",
        "good": "#0ca30c", "bad": "#d03b3b",
        "speed": ["#f6f8fa", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"],
        "heat": ["#fff4eb", "#fdd5b5", "#f7a26f", "#eb6834", "#c0441a", "#7a2a0e"],
        "time": ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"],
    },
    "dark": {
        "page": "#0d1117", "surface": "#161b22", "border": "#30363d",
        "ink": "#f0f6fc", "ink2": "#9198a1", "muted": "#6e7681",
        "grid": "#262c36", "axis": "#3d444d", "solid": "#3d444d",
        "blue": "#3987e5", "orange": "#d95926", "aqua": "#199e70", "violet": "#9085e9",
        "good": "#0ca30c", "bad": "#e66767",
        "speed": ["#161b22", "#123a6b", "#1c5cab", "#3987e5", "#86b6ef", "#cde2fb"],
        "heat": ["#1f1610", "#552510", "#983c16", "#d95926", "#f49a5e", "#ffdcbf"],
        "time": ["#1c5cab", "#2a78d6", "#3987e5", "#86b6ef", "#cde2fb"],
    },
}


def use_theme(t):
    mpl.rcParams.update({
        "font.family": ["Inter", "DejaVu Sans"],
        "font.size": 10.5,
        "mathtext.fontset": "cm",
        "text.color": t["ink"],
        "axes.labelcolor": t["ink2"],
        "axes.edgecolor": t["axis"],
        "axes.linewidth": 0.8,
        "axes.facecolor": "none",
        "axes.labelsize": 10,
        "xtick.color": t["axis"], "ytick.color": t["axis"],
        "xtick.labelcolor": t["ink2"], "ytick.labelcolor": t["ink2"],
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "legend.frameon": False, "legend.fontsize": 9.5,
        "hatch.linewidth": 0.7,
        "contour.negative_linestyle": "solid",
        "svg.hashsalt": "simple_CFD",
        "savefig.dpi": 200,
    })


def cmap(t, key):
    return LinearSegmentedColormap.from_list(key, t[key])


def new_figure(t, w, h):
    """A figure drawn as a rounded 'card' so it sits nicely on the GitHub page."""
    fig = plt.figure(figsize=(w, h))
    card = FancyBboxPatch((0.02, 0.02), w - 0.04, h - 0.04,
                          boxstyle="round,pad=0,rounding_size=0.16",
                          transform=fig.dpi_scale_trans, facecolor=t["surface"],
                          edgecolor=t["border"], linewidth=0.8, zorder=-10)
    fig.add_artist(card)
    return fig, card


def heading(fig, t, x, y, title, subtitle=None, size=13, badge=None):
    if badge is not None:
        fig.text(x, y, str(badge), fontsize=size - 2, fontweight="bold", color="white",
                 ha="left", va="center",
                 bbox=dict(boxstyle="circle,pad=0.32", fc=t["blue"], ec="none"))
        x += 0.032
    fig.text(x, y, title, fontsize=size, fontweight="semibold", color=t["ink"], va="center")
    if subtitle:
        fig.text(x, y - 0.052 * 4.4 / fig.get_figheight(), subtitle,
                 fontsize=size - 3, color=t["ink2"], va="center")


def save(fig, name, theme):
    fig.savefig(OUT / f"{name}_{theme}.svg", format="svg", transparent=True,
                metadata={"Date": None})
    plt.close(fig)


def arrow(ax, start, end, t, color=None, lw=1.4, style="-|>", scale=12, **kw):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=scale,
                                 color=color or t["ink2"], lw=lw, shrinkA=0, shrinkB=0, **kw))


# --------------------------------------------------------------------------- #
#  Small FDM solvers used to make the pictures                                 #
# --------------------------------------------------------------------------- #
def solve_laplace(fixed, value):
    """Solve the 5-point Laplace equation on a uniform grid.

    ``fixed`` marks nodes with a prescribed value (Dirichlet nodes, taken from
    ``value``); every other node satisfies 4 u_P - u_E - u_W - u_N - u_S = 0.
    The resulting sparse linear system A u = b is solved directly.
    """
    unknown = ~fixed
    n = int(unknown.sum())
    index = -np.ones(fixed.shape, dtype=int)
    index[unknown] = np.arange(n)
    jj, ii = np.nonzero(unknown)
    rows, cols, vals = [np.arange(n)], [np.arange(n)], [np.full(n, 4.0)]
    b = np.zeros(n)
    for dj, di in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nj, ni = jj + dj, ii + di
        inside = unknown[nj, ni]
        rows.append(np.arange(n)[inside])
        cols.append(index[nj[inside], ni[inside]])
        vals.append(-np.ones(inside.sum()))
        np.add.at(b, np.arange(n)[~inside], value[nj[~inside], ni[~inside]])
    A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(n, n))
    u = value.astype(float).copy()
    u[unknown] = spla.spsolve(A, b)
    return u


def cylinder_flow(x0, x1, half_height, xc, radius, h):
    """Ideal (potential) flow past a cylinder in a channel.

    Solves the stream-function equation  d2psi/dx2 + d2psi/dy2 = 0  with
    psi = U*y on the outer boundary (U = 1) and psi = 0 on the cylinder.
    """
    nx = int(round((x1 - x0) / h)) + 1
    ny = int(round(2 * half_height / h)) + 1
    X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(-half_height, half_height, ny))
    solid = (X - xc) ** 2 + Y ** 2 <= radius ** 2
    fixed = solid.copy()
    fixed[[0, -1], :] = True
    fixed[:, [0, -1]] = True
    psi = solve_laplace(fixed, np.where(solid, 0.0, Y))
    dpsi_dy, dpsi_dx = np.gradient(psi, h)
    speed = np.hypot(dpsi_dy, dpsi_dx)
    speed[solid] = 0.0
    return X, Y, psi, speed, solid


def plate_temperature(N):
    """Steady heat conduction in a unit square: T = sin(pi x) on top, 0 elsewhere."""
    x = np.linspace(0, 1, N + 1)
    X, Y = np.meshgrid(x, x)
    fixed = np.zeros_like(X, dtype=bool)
    fixed[[0, -1], :] = True
    fixed[:, [0, -1]] = True
    value = np.zeros_like(X)
    value[-1, :] = np.sin(np.pi * x)
    T = solve_laplace(fixed, value)
    exact = np.sin(np.pi * X) * np.sinh(np.pi * Y) / np.sinh(np.pi)
    return X, Y, T, exact


def ftcs(T0, r, steps):
    """Explicit FTCS time marching for dT/dt = alpha d2T/dx2 (fixed end values)."""
    T = T0.copy()
    history = [T.copy()]
    for _ in range(steps):
        T[1:-1] = T[1:-1] + r * (T[2:] - 2 * T[1:-1] + T[:-2])
        history.append(T.copy())
    return history


# --------------------------------------------------------------------------- #
#  Figures                                                                     #
# --------------------------------------------------------------------------- #
def fig_banner(t, theme):
    W, H = 12.0, 3.4
    fig, card = new_figure(t, W, H)
    x0, x1, yh, xc, R = -6.4, 3.5, 1.4, 1.2, 0.42
    X, Y, psi, speed, solid = cylinder_flow(x0, x1, yh, xc, R, h=0.02)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(x0, x1)
    ax.set_ylim(-yh, yh)
    ax.axis("off")
    field = ax.pcolormesh(X, Y, speed, cmap=cmap(t, "speed"), vmin=0.55, vmax=2.4,
                          shading="gouraud", rasterized=True)
    lines = ax.contour(X, Y, np.ma.masked_where(solid, psi),
                       levels=np.linspace(-yh, yh, 25)[1:-1], colors=t["ink"],
                       linewidths=0.7, alpha=0.4)
    cyl = ax.add_patch(Circle((xc, 0), R, fc=t["solid"], ec=t["ink2"], lw=1.1, zorder=2))

    # fade the field into the card on the left, where the title sits
    xf = np.linspace(0, 1, 800)
    s = np.clip((0.70 - xf) / (0.70 - 0.40), 0, 1)
    rgba = np.zeros((1, xf.size, 4))
    rgba[..., :3] = to_rgb(t["surface"])
    rgba[..., 3] = s * s * (3 - 2 * s)
    fade = ax.imshow(rgba, extent=(x0, x1, -yh, yh), aspect="auto", zorder=3,
                     interpolation="bilinear")

    # grid nodes appear where the field fades in: "grid -> solution"
    d = 0.2
    gx, gy = np.meshgrid(np.arange(-3.0, -0.2, d), np.arange(-yh + d, yh - d / 2, d))
    xfig = (gx - x0) / (x1 - x0)
    alpha = np.clip(np.sin(np.pi * (xfig - 0.40) / 0.32), 0, 1) ** 1.5 * 0.85
    colors = np.zeros(gx.shape + (4,))
    colors[..., :3] = to_rgb(t["ink2"])
    colors[..., 3] = alpha
    nodes = ax.scatter(gx.ravel(), gy.ravel(), s=5, c=colors.reshape(-1, 4), lw=0, zorder=4)

    for artist in (field, lines, cyl, fade, nodes):
        artist.set_clip_path(card)

    fig.text(0.045, 0.62, "simple_CFD", fontsize=44, fontweight="bold", color=t["ink"])
    for k, c in enumerate(("blue", "orange", "aqua")):
        fig.add_artist(Rectangle((0.048 + k * 0.032, 0.565), 0.028, 0.012,
                                 transform=fig.transFigure, color=t[c], lw=0))
    fig.text(0.047, 0.41, "A visual, hands-on introduction to", fontsize=15.5, color=t["ink2"])
    fig.text(0.047, 0.28, "Computational Fluid Dynamics", fontsize=21, fontweight="semibold",
             color=t["ink"])
    fig.text(0.047, 0.13, "Finite Difference Method   ·   1D & 2D problems   ·   Python",
             fontsize=11, color=t["ink2"])
    fig.text(0.982, 0.065, r"ideal flow past a cylinder  ·  $\nabla^2\psi = 0$ solved with finite differences",
             fontsize=8.5, color=t["ink2"], ha="right",
             bbox=dict(boxstyle="round,pad=0.35", fc=t["surface"], ec="none", alpha=0.85))
    save(fig, "banner", theme)


def fig_cfd_problem(t, theme):
    W, H = 10.5, 7.0
    fig, _ = new_figure(t, W, H)
    xc, R = 0.0, 0.4
    X, Y, psi, speed, solid = cylinder_flow(-3, 3, 1, xc, R, h=0.025)
    psi_m = np.ma.masked_where(solid, psi)

    w, h = 0.43, 0.315
    pos = {1: (0.045, 0.555), 2: (0.53, 0.555), 3: (0.045, 0.075), 4: (0.53, 0.075)}
    titles = {
        1: ("Physical problem", "air flows through a duct, past a cylinder"),
        2: ("Geometry  →  domain Ω", "the region where the physics happens, and its boundaries"),
        3: ("Physics  →  governing equations", "conservation laws written as PDEs + boundary conditions"),
        4: ("Numerical solution", "the PDE solved on a grid with finite differences"),
    }
    axes = {}
    for k, (x, y) in pos.items():
        heading(fig, t, x, y + h + 0.075, *titles[k], size=12.5, badge=k)
        ax = fig.add_axes([x, y, w, h])
        ax.axis("off")
        if k != 3:
            ax.set_xlim(-3.35, 3.35)
            ax.set_ylim(-1.55, 1.55)
            ax.set_aspect("equal")
        axes[k] = ax

    # 1 - the physical problem, as a sketch
    ax = axes[1]
    for s in (1, -1):
        ax.add_patch(Rectangle((-3, s), 6, 0.16 * s, hatch="////", fc="none", ec=t["muted"], lw=0))
        ax.plot([-3, 3], [s, s], color=t["ink2"], lw=2, solid_capstyle="butt")
    ax.contour(X, Y, psi_m, levels=np.linspace(-1, 1, 11)[1:-1], colors=t["blue"],
               linewidths=1.0, alpha=0.45)
    for yy in (-0.6, -0.2, 0.2, 0.6):
        arrow(ax, (-3.1, yy), (-2.3, yy), t, color=t["blue"], lw=1.8, scale=13)
    ax.add_patch(Circle((xc, 0), R, fc=t["solid"], ec=t["ink2"], lw=1.2, zorder=3))
    ax.text(0, 1.3, "duct wall", ha="center", va="center", fontsize=9, color=t["ink2"])
    ax.text(-2.7, -1.3, "air in", ha="center", va="center", fontsize=9, color=t["ink2"])
    ax.text(2.7, -1.3, "air out", ha="center", va="center", fontsize=9, color=t["ink2"])
    ax.text(0, -0.62, "cylinder", ha="center", va="center", fontsize=9, color=t["ink"],
            bbox=dict(boxstyle="round,pad=0.2", fc=t["surface"], ec="none"))

    # 2 - the computational domain and its boundaries
    ax = axes[2]
    ax.add_patch(Rectangle((-3, -1), 6, 2, fc=t["blue"], alpha=0.08, ec="none"))
    ax.plot([-3, 3], [1, 1], color=t["ink2"], lw=3, solid_capstyle="butt")
    ax.plot([-3, 3], [-1, -1], color=t["ink2"], lw=3, solid_capstyle="butt")
    ax.plot([-3, -3], [-1, 1], color=t["blue"], lw=3.5, solid_capstyle="butt")
    ax.plot([3, 3], [-1, 1], color=t["orange"], lw=3.5, solid_capstyle="butt")
    ax.add_patch(Circle((xc, 0), R, fc=t["surface"], ec=t["violet"], lw=2.5, zorder=3))
    ax.text(-3.22, 0, r"inlet  $\Gamma_{\mathrm{in}}$", rotation=90, ha="center", va="center", fontsize=9.5)
    ax.text(3.24, 0, r"outlet  $\Gamma_{\mathrm{out}}$", rotation=270, ha="center", va="center", fontsize=9.5)
    ax.text(0, 1.2, r"wall  $\Gamma_{\mathrm{w}}$", ha="center", va="center", fontsize=9.5)
    ax.text(0, -1.22, r"wall  $\Gamma_{\mathrm{w}}$", ha="center", va="center", fontsize=9.5)
    ax.text(0, 0, r"$\Gamma_{\mathrm{c}}$", ha="center", va="center", fontsize=11, zorder=4)
    ax.text(-1.85, -0.35, r"$\Omega$", ha="center", va="center", fontsize=28, color=t["ink2"])
    ax.add_patch(Rectangle((1.3, -0.05), 0.85, 0.65, fc="none", ec=t["ink"], lw=1.2, ls=(0, (3, 2))))
    arrow(ax, (0.85, 0.275), (1.3, 0.275), t, lw=1.3)
    arrow(ax, (2.15, 0.275), (2.6, 0.275), t, lw=1.3)
    ax.text(1.725, 0.72, "control volume", ha="center", va="center", fontsize=8.5, color=t["ink2"])
    ax.text(1.725, -0.28, "in − out = change", ha="center", va="center", fontsize=8.5, color=t["ink2"])

    # 3 - the governing equations
    ax = axes[3]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    rows = [
        (0.97, "Conservation laws (Navier–Stokes)", None),
        (0.84, "mass", r"$\dfrac{\partial\rho}{\partial t}+\nabla\cdot(\rho\,\mathbf{u})=0$"),
        (0.66, "momentum", r"$\rho\,\dfrac{D\mathbf{u}}{Dt}=-\nabla p+\mu\,\nabla^{2}\mathbf{u}+\rho\,\mathbf{g}$"),
        (0.49, "Simplest model: ideal (potential) flow", None),
        (0.36, "stream function", r"$\dfrac{\partial^{2}\psi}{\partial x^{2}}+\dfrac{\partial^{2}\psi}{\partial y^{2}}=0,"
                                   r"\quad u=\dfrac{\partial\psi}{\partial y},\ \ v=-\dfrac{\partial\psi}{\partial x}$"),
        (0.18, "Boundary conditions", None),
        (0.06, None, r"$\psi=U\,y$ on $\Gamma_{\mathrm{in}},\Gamma_{\mathrm{out}}$;   $\psi=\pm\,U\,H$ on $\Gamma_{\mathrm{w}}$;"
                     r"   $\psi=0$ on $\Gamma_{\mathrm{c}}$"),
    ]
    for y, label, eq in rows:
        if eq is None:
            ax.text(0.0, y, label, fontsize=10.5, fontweight="semibold", va="center")
        else:
            if label:
                ax.text(0.03, y, label, fontsize=9.5, color=t["ink2"], va="center")
            ax.text(0.27 if label else 0.03, y, eq, fontsize=12, va="center")

    # 4 - the numerical solution
    ax = axes[4]
    pc = ax.pcolormesh(X, Y, speed, cmap=cmap(t, "speed"), vmin=0.5, vmax=2.5,
                       shading="gouraud", rasterized=True)
    ax.contour(X, Y, psi_m, levels=np.linspace(-1, 1, 15)[1:-1], colors=t["ink"],
               linewidths=0.6, alpha=0.45)
    ax.add_patch(Circle((xc, 0), R, fc=t["solid"], ec=t["ink2"], lw=1.0, zorder=3))
    ax.plot([-3, 3], [1, 1], color=t["ink2"], lw=1.5)
    ax.plot([-3, 3], [-1, -1], color=t["ink2"], lw=1.5)
    cax = ax.inset_axes([0.2, -1.45, 2.8, 0.13], transform=ax.transData)
    cb = fig.colorbar(pc, cax=cax, orientation="horizontal", extend="both", ticks=[0.5, 1, 1.5, 2, 2.5])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, length=2, pad=1.5)
    ax.text(0.05, -1.385, r"speed $|\mathbf{u}|/U$", ha="right", va="center", fontsize=9, color=t["ink2"])
    ax.text(0, 1.3, f"grid: {X.shape[1]} × {X.shape[0]} nodes,  lines = streamlines (ψ = const)",
            ha="center", va="center", fontsize=8.5, color=t["ink2"])

    # arrows that connect the four steps: 1 -> 2, then down to 3, then 3 -> 4
    fa = dict(transform=fig.transFigure, arrowstyle="-|>", mutation_scale=15, color=t["muted"], lw=1.6)
    fig.add_artist(FancyArrowPatch((0.478, 0.715), (0.522, 0.715), **fa))
    fig.add_artist(FancyArrowPatch((0.478, 0.235), (0.522, 0.235), **fa))
    zig = MplPath([(0.745, 0.545), (0.745, 0.508), (0.26, 0.508), (0.26, 0.478)],
                  [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO, MplPath.LINETO])
    fig.add_artist(FancyArrowPatch(path=zig, **fa))
    save(fig, "cfd_problem", theme)


def fig_grid_methods(t, theme):
    W, H = 11.0, 3.8
    fig, _ = new_figure(t, W, H)
    L, D = 4.0, 2.0
    xc, yc, R = 1.3, 1.0, 0.55
    lefts, w = (0.035, 0.36, 0.685), 0.285
    specs = [
        ("Finite Difference (FDM)", "unknowns live on grid points",
         "derivatives  →  differences of nodal values"),
        ("Finite Element (FEM)", "unknowns live on element nodes",
         "simple shape functions on every element"),
        ("Finite Volume (FVM)", "unknowns are cell averages",
         "fluxes balanced across every cell face"),
    ]
    outside = lambda x, y, pad=0.0: (x - xc) ** 2 + (y - yc) ** 2 > (R + pad) ** 2  # noqa: E731
    label_box = dict(boxstyle="round,pad=0.15", fc=t["surface"], ec="none")

    for k, (title, sub, idea) in enumerate(specs):
        heading(fig, t, lefts[k], 0.87, title, sub, size=12.5)
        fig.text(lefts[k] + w / 2, 0.12, idea, ha="center", va="center", fontsize=9.5, color=t["ink"])
        ax = fig.add_axes([lefts[k], 0.17, w, 0.56])
        ax.set_xlim(-0.08, L + 0.08)
        ax.set_ylim(-0.08, D + 0.08)
        ax.set_aspect("equal")
        ax.axis("off")
        cyl = Circle((xc, yc), R, fc=t["solid"], ec=t["ink2"], lw=1.1, zorder=3)

        if k == 0:  # FDM: structured grid, values at the nodes
            xs, ys = np.linspace(0, L, 13), np.linspace(0, D, 7)
            d = xs[1] - xs[0]
            for x in xs:
                ax.plot([x, x], [0, D], color=t["grid"], lw=0.9, zorder=1)
            for y in ys:
                ax.plot([0, L], [y, y], color=t["grid"], lw=0.9, zorder=1)
            ax.add_patch(cyl)
            gx, gy = np.meshgrid(xs, ys)
            keep = outside(gx, gy)
            ax.scatter(gx[keep], gy[keep], s=13, color=t["ink2"], lw=0, zorder=4)
            c = (xs[8], ys[3])
            for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
                ax.plot([c[0], c[0] + dx], [c[1], c[1] + dy], color=t["blue"], lw=2.4, zorder=5)
                ax.scatter(c[0] + dx, c[1] + dy, s=60, color=t["blue"], ec=t["surface"], lw=1.5, zorder=6)
            ax.scatter(*c, s=80, color=t["orange"], ec=t["surface"], lw=1.5, zorder=7)
            ax.text(c[0] + 0.07, c[1] + 0.08, r"$(i,j)$", fontsize=10.5, zorder=8, bbox=label_box)
            arrow(ax, (c[0] + 0.02, c[1] - d / 2), (c[0] + d, c[1] - d / 2), t, style="<->", scale=7,
                  lw=1.0, zorder=6)
            ax.text(c[0] + d / 2 + 0.25, c[1] - d / 2, r"$\Delta x$", va="center", fontsize=10.5,
                    zorder=8, bbox=label_box)
            fig.text(lefts[k] + w, 0.87, "THIS COURSE", ha="right", va="center", fontsize=8.5,
                     fontweight="bold", color="#1f2328",
                     bbox=dict(boxstyle="round,pad=0.35", fc=t["orange"], ec="none"))

        elif k == 1:  # FEM: unstructured triangles that follow the curved boundary
            rng = np.random.default_rng(7)
            d = 1 / 3
            edge = np.linspace(0, L, 13)
            side = np.linspace(0, D, 7)[1:-1]
            pts = [(x, 0) for x in edge] + [(x, D) for x in edge] + [(0, y) for y in side] + [(L, y) for y in side]
            th = np.linspace(0, 2 * np.pi, 18, endpoint=False)
            pts += list(zip(xc + R * np.cos(th), yc + R * np.sin(th)))
            th2 = th + np.pi / 18
            pts += list(zip(xc + (R + 0.24) * np.cos(th2), yc + (R + 0.24) * np.sin(th2)))
            for row, y in enumerate(np.arange(d * 0.9, D - 0.12, d * 0.87)):
                for x in np.arange(d * (0.5 + 0.5 * (row % 2)), L - 0.12, d):
                    px, py = x + rng.uniform(-0.05, 0.05), y + rng.uniform(-0.05, 0.05)
                    if outside(px, py, 0.42) and 0.14 < px < L - 0.14 and 0.14 < py < D - 0.14:
                        pts.append((px, py))
            px, py = np.array(pts).T
            tri = mtri.Triangulation(px, py)
            cx, cy = px[tri.triangles].mean(axis=1), py[tri.triangles].mean(axis=1)
            tri.set_mask(~outside(cx, cy))
            ax.triplot(tri, color=t["ink2"], lw=0.7, zorder=2)
            ax.add_patch(cyl)
            ax.scatter(px, py, s=9, color=t["ink2"], lw=0, zorder=4)
            e = np.argmin(np.where(tri.mask, np.inf, (cx - 2.9) ** 2 + (cy - 0.95) ** 2))
            v = tri.triangles[e]
            ax.fill(px[v], py[v], color=t["orange"], alpha=0.35, lw=0, zorder=3)
            ax.plot(np.append(px[v], px[v[0]]), np.append(py[v], py[v[0]]), color=t["orange"], lw=2, zorder=5)
            ax.scatter(px[v], py[v], s=40, color=t["orange"], ec=t["surface"], lw=1.3, zorder=6)
            ax.annotate("one element", xy=(cx[e], cy[e]), xytext=(3.35, 1.78), fontsize=9.5,
                        ha="center", va="center", zorder=8, bbox=label_box,
                        arrowprops=dict(arrowstyle="-", color=t["ink"], lw=1.0))

        else:  # FVM: cells (control volumes) and the fluxes through their faces
            d = 0.5
            xs, ys = np.arange(0, L + d / 2, d), np.arange(0, D + d / 2, d)
            for x in xs:
                ax.plot([x, x], [0, D], color=t["ink2"], lw=0.8, zorder=1)
            for y in ys:
                ax.plot([0, L], [y, y], color=t["ink2"], lw=0.8, zorder=1)
            ax.add_patch(cyl)
            gx, gy = np.meshgrid(xs[:-1] + d / 2, ys[:-1] + d / 2)
            keep = outside(gx, gy, 0.05)
            ax.scatter(gx[keep], gy[keep], s=9, color=t["muted"], lw=0, zorder=4)
            x0, y0 = 2.5, 0.5
            ax.add_patch(Rectangle((x0, y0), d, d, fc=t["orange"], alpha=0.35, lw=0, zorder=2))
            ax.add_patch(Rectangle((x0, y0), d, d, fc="none", ec=t["orange"], lw=2, zorder=5))
            ax.scatter(x0 + d / 2, y0 + d / 2, s=40, color=t["orange"], ec=t["surface"], lw=1.3, zorder=6)
            ax.text(x0 + d / 2 + 0.06, y0 + d / 2 + 0.06, "P", fontsize=10, fontweight="bold", zorder=7)
            m, a = 0.14, 0.24
            for s, e in (((x0 - a, y0 + d / 2), (x0 + m, y0 + d / 2)),
                         ((x0 + d - m, y0 + d / 2), (x0 + d + a, y0 + d / 2)),
                         ((x0 + d / 2, y0 - a), (x0 + d / 2, y0 + m)),
                         ((x0 + d / 2, y0 + d - m), (x0 + d / 2, y0 + d + a))):
                arrow(ax, s, e, t, color=t["blue"], lw=2, scale=11, zorder=8)
            ax.text(x0 + d + 0.3, y0 + d / 2, "flux", fontsize=9.5, va="center", zorder=8, bbox=label_box)
            ax.annotate("control volume", xy=(x0 + d, y0 + d), xytext=(3.4, 1.75), fontsize=9.5,
                        ha="center", va="center", zorder=8, bbox=label_box,
                        arrowprops=dict(arrowstyle="-", color=t["ink"], lw=1.0))
    save(fig, "grid_methods", theme)


def fig_finite_differences(t, theme):
    W, H = 11.0, 4.6
    fig, _ = new_figure(t, W, H)
    heading(fig, t, 0.045, 0.9, "From derivative to difference",
            "three ways to estimate the slope f′(xᵢ) from neighbouring grid values", size=12.5)
    heading(fig, t, 0.6, 0.9, "The five-point stencil",
            "the 2D Laplacian at node (i, j) uses its four neighbours", size=12.5)
    box = dict(boxstyle="round,pad=0.1", fc=t["surface"], ec="none")

    # left: forward / backward / central differences
    ax = fig.add_axes([0.05, 0.13, 0.48, 0.64])
    f = lambda x: 1.1 + 0.7 * np.sin(1.3 * x - 0.4) + 0.12 * x  # noqa: E731
    df = lambda x: 0.91 * np.cos(1.3 * x - 0.4) + 0.12  # noqa: E731
    xi, dx = 1.9, 0.75
    xm, xp = xi - dx, xi + dx
    xx = np.linspace(0, 3.9, 300)
    ax.plot(xx, f(xx), color=t["ink2"], lw=2.4, zorder=2)
    ax.text(3.72, f(3.72) + 0.16, r"$f(x)$", fontsize=12, ha="center", color=t["ink2"])

    def line(x0, slope, xa, xb, **kw):
        xs = np.array([xa, xb])
        return ax.plot(xs, f(x0) + slope * (xs - x0), lw=2, **kw)

    line(xi, df(xi), xi - 1.0, xi + 1.0, color=t["ink"], zorder=4,
         label=r"exact slope  $f'(x_i)$")
    line(xi, (f(xp) - f(xi)) / dx, xi - 0.35, xp + 0.35, color=t["blue"], zorder=3,
         label=r"forward   $(f_{i+1}-f_i)\,/\,\Delta x$     error $\mathcal{O}(\Delta x)$")
    line(xi, (f(xi) - f(xm)) / dx, xm - 0.35, xi + 0.35, color=t["orange"], zorder=3,
         label=r"backward  $(f_{i}-f_{i-1})\,/\,\Delta x$     error $\mathcal{O}(\Delta x)$")
    line(xm, (f(xp) - f(xm)) / (2 * dx), xm - 0.25, xp + 0.25, color=t["aqua"], zorder=3,
         label=r"central    $(f_{i+1}-f_{i-1})\,/\,2\Delta x$   error $\mathcal{O}(\Delta x^2)$")
    for x, lab, (ox, oy, ha) in ((xm, r"$f_{i-1}$", (0.04, -0.3, "left")),
                                 (xi, r"$f_i$", (0.0, 0.2, "center")),
                                 (xp, r"$f_{i+1}$", (-0.04, -0.3, "right"))):
        ax.plot([x, x], [0, f(x)], color=t["grid"], lw=1, zorder=1)
        ax.scatter(x, f(x), s=60, color=t["ink"], ec=t["surface"], lw=1.6, zorder=6)
        ax.text(x + ox, f(x) + oy, lab, fontsize=11.5, ha=ha, zorder=7, bbox=box)
    for a, b in ((xm, xi), (xi, xp)):
        arrow(ax, (a, 0.18), (b, 0.18), t, style="<->", scale=8, lw=1.0)
        ax.text((a + b) / 2, 0.3, r"$\Delta x$", ha="center", fontsize=10.5, color=t["ink2"])
    ax.set_xlim(0, 3.95)
    ax.set_ylim(0, 3.45)
    ax.set_xticks([xm, xi, xp], [r"$x_{i-1}$", r"$x_i$", r"$x_{i+1}$"], fontsize=12)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper left", fontsize=9.5, handlelength=1.6, borderaxespad=0.2, labelcolor=t["ink"])

    # right: the five-point stencil
    ax = fig.add_axes([0.6, 0.15, 0.36, 0.62])
    ax.set_xlim(-2.3, 2.3)
    ax.set_ylim(-2.05, 1.85)
    ax.set_aspect("equal")
    ax.axis("off")
    for v in range(-2, 3):
        ax.plot([v, v], [-1.6, 1.6], color=t["grid"], lw=0.9, zorder=1)
        ax.plot([-2.1, 2.1], [v * 0.8, v * 0.8], color=t["grid"], lw=0.9, zorder=1)
    gx, gy = np.meshgrid(range(-2, 3), np.arange(-2, 3) * 0.8)
    ax.scatter(gx, gy, s=12, color=t["muted"], lw=0, zorder=2)
    neighbours = {(1, 0): (r"$(i{+}1,\,j)$", (1, 0.26, "center")),
                  (-1, 0): (r"$(i{-}1,\,j)$", (-1, 0.26, "center")),
                  (0, 1): (r"$(i,\,j{+}1)$", (-0.18, 0.8, "right")),
                  (0, -1): (r"$(i,\,j{-}1)$", (-0.18, -0.8, "right"))}
    for (i, j), (lab, (lx, ly, ha)) in neighbours.items():
        ax.plot([0, i], [0, 0.8 * j], color=t["blue"], lw=2.6, zorder=3)
        ax.scatter(i, 0.8 * j, s=120, color=t["blue"], ec=t["surface"], lw=2, zorder=4)
        ax.text(lx, ly, lab, ha=ha, va="center", fontsize=11, zorder=5, bbox=box)
    ax.scatter(0, 0, s=150, color=t["orange"], ec=t["surface"], lw=2, zorder=4)
    ax.text(-0.16, -0.32, r"$(i,\,j)$", ha="right", va="center", fontsize=11.5, zorder=5, bbox=box)
    arrow(ax, (0.1, -0.3), (1, -0.3), t, style="<->", scale=8, lw=1.0, zorder=5)
    ax.text(0.55, -0.5, r"$\Delta x$", ha="center", va="center", fontsize=10.5, color=t["ink2"])
    arrow(ax, (0.3, 0.1), (0.3, 0.8), t, style="<->", scale=8, lw=1.0, zorder=5)
    ax.text(0.5, 0.45, r"$\Delta y$", ha="left", va="center", fontsize=10.5, color=t["ink2"])
    ax.text(0, -1.95, r"$\nabla^2 u\;\approx\;\dfrac{u_{i+1,j}-2u_{i,j}+u_{i-1,j}}{\Delta x^2}"
                      r"+\dfrac{u_{i,j+1}-2u_{i,j}+u_{i,j-1}}{\Delta y^2}$",
            ha="center", va="center", fontsize=12)
    save(fig, "finite_differences", theme)


def fig_explicit_implicit(t, theme):
    W, H = 11.0, 4.0
    fig, _ = new_figure(t, W, H)
    panels = [
        ("Explicit scheme (FTCS)", "Forward in Time, Centred in Space",
         r"$T_i^{\,n+1}=T_i^{\,n}+r\left(T_{i+1}^{\,n}-2T_i^{\,n}+T_{i-1}^{\,n}\right)$",
         "one unknown per equation  →  update it directly"),
        ("Implicit scheme (BTCS)", "Backward in Time, Centred in Space",
         r"$-r\,T_{i-1}^{\,n+1}+(1+2r)\,T_i^{\,n+1}-r\,T_{i+1}^{\,n+1}=T_i^{\,n}$",
         "unknowns are coupled  →  solve a linear system"),
    ]
    for k, (title, sub, eq, note) in enumerate(panels):
        x0 = 0.045 + 0.49 * k
        heading(fig, t, x0, 0.885, title, sub, size=12.5)
        ax = fig.add_axes([x0 + 0.02, 0.25, 0.41, 0.47])
        ax.set_xlim(-2.75, 2.6)
        ax.set_ylim(-0.5, 1.55)
        ax.axis("off")
        for lvl in (0, 1):
            ax.plot([-2.4, 2.4], [lvl, lvl], color=t["grid"], lw=1.2, zorder=1)
        for i in range(-2, 3):
            ax.plot([i, i], [0, 1], color=t["grid"], lw=0.8, zorder=1)
            ax.text(i, -0.3, [r"$i-2$", r"$i-1$", r"$i$", r"$i+1$", r"$i+2$"][i + 2], ha="center",
                    va="center", fontsize=11, color=t["ink"] if abs(i) < 2 else t["muted"])
        ax.text(-2.62, 1, r"$n+1$", ha="right", va="center", fontsize=11)
        ax.text(-2.62, 0, r"$n$", ha="right", va="center", fontsize=11)
        known = [(-1, 0), (0, 0), (1, 0)] if k == 0 else [(0, 0)]
        unknown = [(0, 1)] if k == 0 else [(-1, 1), (0, 1), (1, 1)]
        if k == 1:
            ax.plot([-1, 1], [1, 1], color=t["orange"], lw=4, zorder=2, solid_capstyle="round")
        for (i, n) in known:
            tgt = unknown if k == 0 else [(0, 1)]
            for (ui, un) in tgt:
                ax.add_patch(FancyArrowPatch((i, n), (ui, un), arrowstyle="-|>", mutation_scale=12,
                                             color=t["ink2"], lw=1.3, shrinkA=9, shrinkB=10, zorder=2))
        rest = [(i, n) for i in range(-2, 3) for n in (0, 1) if (i, n) not in known + unknown]
        ax.scatter(*zip(*rest), s=55, fc=t["surface"], ec=t["muted"], lw=1.2, zorder=3)
        ax.scatter(*zip(*known), s=130, color=t["blue"], ec=t["surface"], lw=2, zorder=4)
        ax.scatter(*zip(*unknown), s=130, color=t["orange"], ec=t["surface"], lw=2, zorder=4)
        ax.text(0, 1.38, note, ha="center", va="center", fontsize=9.5, color=t["ink2"])
        fig.text(x0 + 0.225, 0.13, eq, ha="center", va="center", fontsize=12.5)
    fig.text(0.045, 0.05, r"$r=\alpha\,\Delta t/\Delta x^{2}$  (stability number)", va="center",
             fontsize=11, color=t["ink2"])
    for i, (color, label) in enumerate(((t["blue"], "known value (time level n)"),
                                        (t["orange"], "unknown value (time level n+1)"))):
        x = 0.45 + 0.22 * i
        fig.add_artist(plt.Line2D([x], [0.05], transform=fig.transFigure, ls="", marker="o", ms=9,
                                  color=color))
        fig.text(x + 0.012, 0.05, label, va="center", fontsize=9.5, color=t["ink"])
    save(fig, "explicit_implicit", theme)


def fig_stability(t, theme):
    W, H = 11.0, 4.3
    fig, _ = new_figure(t, W, H)
    N = 40
    x = np.linspace(0, 1, N + 1)
    T0 = np.where((x > 0.3) & (x < 0.7), 1.0, 0.0)
    steps = [0, 12, 24, 36, 48]
    cases = [(0.45, True, "r ≤ ½: errors are damped, the profile smooths out"),
             (0.52, False, "r just above ½: errors grow every step, the solution blows up")]
    for k, (r, stable, sub) in enumerate(cases):
        x0 = 0.045 + 0.49 * k
        hist = ftcs(T0, r, steps[-1])
        fig.text(x0, 0.89, "✓" if stable else "✗", fontsize=15, fontweight="bold",
                 color=t["good"] if stable else t["bad"], va="center")
        heading(fig, t, x0 + 0.022, 0.89, f"r = {r:.2f}  —  " + ("stable" if stable else "unstable"),
                sub, size=12.5)
        ax = fig.add_axes([x0 + 0.03, 0.25, 0.41, 0.5])
        lines = [ax.plot(x, hist[n], color=c, lw=1.8)[0] for c, n in zip(t["time"], steps)]
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.8, 1.8)
        ax.set_xlabel("x / L", labelpad=2)
        ax.set_ylabel("T", labelpad=2)
        ax.grid(axis="y", color=t["grid"], lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.text(0.33, 0.06, "time step", ha="right", va="center", fontsize=9.5, color=t["ink2"])
    fig.legend(lines, [f"n = {n}" for n in steps], loc="center left", bbox_to_anchor=(0.335, 0.06),
               ncol=len(steps), fontsize=9.5, labelcolor=t["ink"], handlelength=1.8, columnspacing=1.4,
               borderaxespad=0)
    save(fig, "stability", theme)


def fig_solvers(t, theme):
    W, H = 11.0, 4.3
    fig, _ = new_figure(t, W, H)
    heading(fig, t, 0.045, 0.9, "The algebraic system  A u = b",
            "5 × 5 grid: 25 unknowns, ≤ 5 non-zeros per row", size=12.5)
    heading(fig, t, 0.43, 0.9, "Iterative solvers: same answer, very different speed",
            "residual history for a 2D Laplace problem on a 33 × 33 grid", size=12.5)

    # left: sparsity pattern of A
    n = 5
    T1 = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(n, n))
    A = (sp.kron(sp.eye(n), T1) + sp.kron(T1, sp.eye(n))).toarray()
    M = np.where(np.eye(n * n, dtype=bool), 2, np.where(A != 0, 1, 0)).astype(float)
    ax = fig.add_axes([0.06, 0.2, 0.27, 0.56])
    ax.pcolormesh(np.ma.masked_equal(M, 0), cmap=ListedColormap([t["blue"], t["orange"]]),
                  vmin=0.5, vmax=2.5, edgecolors=t["surface"], linewidth=0.8)
    ax.add_patch(Rectangle((0, 0), n * n, n * n, fc="none", ec=t["axis"], lw=0.8))
    ax.set_xlim(-0.5, n * n + 0.5)
    ax.set_ylim(n * n + 0.5, -0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.legend(handles=[Patch(color=t["orange"], label="diagonal (4)"),
                        Patch(color=t["blue"], label="neighbour (−1)")],
               loc="center", bbox_to_anchor=(0.195, 0.11), ncol=2, fontsize=9.5, handlelength=1.0,
               handleheight=1.0, labelcolor=t["ink"], columnspacing=1.2)

    # right: Jacobi vs Gauss-Seidel vs SOR
    N, iters, tol = 32, 1500, 1e-6
    xg = np.linspace(0, 1, N + 1)
    I, J = np.meshgrid(np.arange(1, N), np.arange(1, N))
    red = (I + J) % 2 == 0
    omega = 2 / (1 + np.sin(np.pi / N))

    def run(method):
        u = np.zeros((N + 1, N + 1))
        u[-1, :] = np.sin(np.pi * xg)
        res = lambda: np.linalg.norm(u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2] - 4 * u[1:-1, 1:-1])  # noqa: E731
        r0, hist = res(), [1.0]
        for _ in range(iters):
            if method == "jacobi":
                u[1:-1, 1:-1] = 0.25 * (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2])
            else:  # red-black ordering, vectorised
                w = 1.0 if method == "gs" else omega
                for mask in (red, ~red):
                    gs = 0.25 * (u[2:, 1:-1] + u[:-2, 1:-1] + u[1:-1, 2:] + u[1:-1, :-2])
                    inner = u[1:-1, 1:-1]
                    inner[mask] = (1 - w) * inner[mask] + w * gs[mask]
            hist.append(res() / r0)
        return np.array(hist)

    ax = fig.add_axes([0.45, 0.17, 0.4, 0.58])
    for method, label, color in (("jacobi", "Jacobi", t["blue"]),
                                 ("gs", "Gauss–Seidel", t["orange"]),
                                 ("sor", f"SOR (ω = {omega:.2f})", t["aqua"])):
        h = run(method)
        hit = int(np.argmax(h < tol)) if (h < tol).any() else None
        if hit is None:  # still not converged at the right edge: label the line end
            ax.semilogy(h, color=color, lw=2)
            ax.text(iters * 1.02, h[-1], f"{label}\n> {iters} iterations", fontsize=9.5, va="center")
        else:  # iterate until the residual drops below the tolerance
            ax.semilogy(h[:hit + 1], color=color, lw=2)
            ax.scatter(hit, h[hit], s=36, color=color, ec=t["surface"], lw=1.2, zorder=4)
            ax.text(hit + 20, tol / 2.5, f"{label}\n{hit} iterations", fontsize=9.5, va="top")
    ax.axhline(tol, color=t["muted"], lw=1, zorder=0)
    ax.text(iters, tol * 1.7, "tolerance  10⁻⁶", fontsize=8.5, color=t["ink2"], ha="right")
    ax.set_xlim(0, iters)
    ax.set_ylim(1e-8, 2)
    ax.set_xlabel("iteration", labelpad=2)
    ax.set_ylabel("relative residual", labelpad=2)
    ax.grid(axis="y", color=t["grid"], lw=0.6, which="major")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "solvers", theme)


def fig_postprocessing(t, theme):
    W, H = 10.5, 9.0
    fig, _ = new_figure(t, W, H)
    fig.text(0.045, 0.955, "Post-processing example: steady heat conduction in a square plate",
             fontsize=13.5, fontweight="semibold", va="center")
    fig.text(0.045, 0.927, r"$\nabla^2T=0$,  top edge $T=T_0\sin(\pi x)$,  other edges $T=0$  —  "
                           r"solved with FDM on a $41\times41$ grid", fontsize=10.5, color=t["ink2"], va="center")
    X, Y, T, exact = plate_temperature(40)
    heat = cmap(t, "heat")
    style = lambda ax: [ax.spines[s].set_visible(False) for s in ("top", "right")]  # noqa: E731

    # (a) contour plot
    ax = fig.add_axes([0.07, 0.525, 0.33, 0.33])
    fig.text(0.045, 0.885, "Contour map", fontsize=12, fontweight="semibold", va="center")
    cf = ax.contourf(X, Y, T, levels=np.linspace(0, 1, 11), cmap=heat)
    ax.contour(X, Y, T, levels=np.linspace(0.1, 0.9, 9), colors=t["ink"], linewidths=0.5, alpha=0.5)
    cb = fig.colorbar(cf, ax=ax, fraction=0.05, pad=0.03, ticks=[0, 0.5, 1])
    cb.outline.set_visible(False)
    cb.set_label(r"$T\,/\,T_0$", color=t["ink2"])
    ax.set_aspect("equal")
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # (b) heat-flux lines
    ax = fig.add_axes([0.57, 0.525, 0.33, 0.33])
    fig.text(0.545, 0.885, r"Streamlines of the heat flux  $\mathbf{q}=-k\,\nabla T$",
             fontsize=12, fontweight="semibold", va="center")
    dTdy, dTdx = np.gradient(T, X[0, 1] - X[0, 0])
    ax.contour(X, Y, T, levels=np.linspace(0.1, 0.9, 9), colors=t["grid"], linewidths=0.8)
    ax.streamplot(X, Y, -dTdx, -dTdy, color=t["blue"], density=0.7, linewidth=1.1, arrowsize=1.0)
    ax.plot([0, 1], [1, 1], color=t["orange"], lw=3, solid_capstyle="butt", clip_on=False)
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([0, 0.5, 1])
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # (c) line plot along the centre line, numerical vs analytical
    ax = fig.add_axes([0.08, 0.08, 0.36, 0.3])
    fig.text(0.045, 0.43, "Line plot along x = 0.5", fontsize=12, fontweight="semibold", va="center")
    mid = T.shape[1] // 2
    yy = np.linspace(0, 1, 200)
    ax.plot(yy, np.sinh(np.pi * yy) / np.sinh(np.pi), color=t["ink"], lw=1.8, label="analytical")
    ax.scatter(Y[::2, mid], T[::2, mid], s=34, color=t["blue"], ec=t["surface"], lw=1.2, zorder=3,
               label="FDM (every 2nd node)")
    ax.set_xlabel("y")
    ax.set_ylabel(r"$T\,/\,T_0$")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.grid(color=t["grid"], lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", labelcolor=t["ink"])
    style(ax)

    # (d) grid convergence
    ax = fig.add_axes([0.585, 0.08, 0.36, 0.3])
    fig.text(0.545, 0.43, "Verification: grid-convergence study", fontsize=12, fontweight="semibold",
             va="center")
    Ns = np.array([8, 16, 32, 64, 128])
    err = np.array([np.abs(Tn - En).max() for Tn, En in (plate_temperature(n)[2:] for n in Ns)])
    hs = 1 / Ns
    ax.loglog(hs, err, color=t["blue"], lw=2, marker="o", ms=7, mec=t["surface"], mew=1.2, label="max error")
    ref = err[0] * (hs / hs[0]) ** 2
    ax.loglog(hs, ref * 0.45, color=t["muted"], lw=1.2, label=r"slope 2  ($\propto\Delta x^2$)")
    ax.set_xlabel(r"grid spacing $\Delta x$")
    ax.set_ylabel(r"$\max\,|T_{\mathrm{FDM}}-T_{\mathrm{exact}}|$")
    ax.grid(color=t["grid"], lw=0.6, which="major")
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", labelcolor=t["ink"])
    ax.text(hs[2], err[2] * 2.4, "halve Δx  →  error ÷ 4", fontsize=9, color=t["ink2"], ha="center")
    style(ax)
    save(fig, "postprocessing", theme)


def gif_heat_rod(t, theme):
    """Animated running example: the heated rod, explicit FTCS vs the exact solution."""
    use_theme(t)
    W, H, dpi = 8.4, 3.7, 110
    fig = plt.figure(figsize=(W, H), dpi=dpi, facecolor=t["page"])
    fig.add_artist(FancyBboxPatch((0.03, 0.03), W - 0.06, H - 0.06, boxstyle="round,pad=0,rounding_size=0.16",
                                  transform=fig.dpi_scale_trans, fc=t["surface"], ec=t["border"], lw=0.8,
                                  zorder=-10))
    N, r = 20, 0.4
    x = np.linspace(0, 1, N + 1)
    dfo = r * (1 / N) ** 2
    T0 = np.full(N + 1, 20.0)
    T0[0] = 100.0
    total = 600
    hist = ftcs(T0, r, total)
    frames = np.unique(np.r_[0, np.round(np.geomspace(1, total, 70)).astype(int)])
    xx = np.linspace(0, 1, 400)
    nmode = np.arange(1, 400)

    def exact(fo):
        if fo == 0:
            return np.where(xx == 0, 100.0, 20.0)
        s = (2 / (nmode * np.pi))[:, None] * np.sin(np.outer(nmode, np.pi * xx)) \
            * np.exp(-(nmode * np.pi) ** 2 * fo)[:, None]
        return 20 + 80 * (1 - xx - s.sum(axis=0))

    ax = fig.add_axes([0.085, 0.38, 0.55, 0.47])
    ax.set_xlim(0, 1)
    ax.set_ylim(10, 108)
    ax.set_xlabel("position  x / L", labelpad=1)
    ax.set_ylabel("T  [°C]", labelpad=2)
    ax.grid(color=t["grid"], lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    (line_exact,) = ax.plot(xx, exact(0), color=t["ink"], lw=1.8, label="exact solution")
    pts = ax.scatter(x, hist[0], s=34, color=t["blue"], ec=t["surface"], lw=1.1, zorder=3,
                     label="FTCS, 21 nodes")
    ax.legend(loc="upper right", fontsize=9, labelcolor=t["ink"])
    fig.text(0.05, 0.92, "Running example: heating a rod", fontsize=12.5, fontweight="semibold", va="center")

    rod = fig.add_axes([0.085, 0.09, 0.55, 0.07])
    rod.axis("off")
    img = rod.imshow(np.interp(xx, x, hist[0])[None, :], cmap=cmap(t, "heat"), vmin=20, vmax=100,
                     aspect="auto", extent=(0, 1, 0, 1))
    fig.text(0.075, 0.125, "100 °C", ha="right", va="center", fontsize=9, color=t["ink2"])
    fig.text(0.645, 0.125, "20 °C", ha="left", va="center", fontsize=9, color=t["ink2"])

    info = [
        (0.80, r"$\dfrac{\partial T}{\partial t}=\alpha\,\dfrac{\partial^2 T}{\partial x^2}$", 13, t["ink"]),
        (0.63, "left end held at 100 °C", 9.5, t["ink2"]),
        (0.555, "right end held at 20 °C", 9.5, t["ink2"]),
        (0.48, "rod starts at 20 °C", 9.5, t["ink2"]),
        (0.36, rf"explicit FTCS,  $r=\alpha\Delta t/\Delta x^2={r}$", 9.5, t["ink2"]),
    ]
    for y, s, size, c in info:
        fig.text(0.715, y, s, fontsize=size, color=c, va="center")
    clock = fig.text(0.715, 0.2, "", fontsize=11, fontweight="semibold", va="center")

    images = []
    for n in frames:
        fo = n * dfo
        line_exact.set_ydata(exact(fo))
        pts.set_offsets(np.c_[x, hist[n]])
        img.set_data(np.interp(xx, x, hist[n])[None, :])
        clock.set_text(f"time step n = {n:3d}\n" + r"$\alpha t/L^2$" + f" = {fo:.3f}")
        fig.canvas.draw()
        images.append(Image.frombuffer("RGBA", fig.canvas.get_width_height(),
                                       fig.canvas.buffer_rgba(), "raw", "RGBA", 0, 1).convert("RGB"))
    plt.close(fig)

    w_, h_ = images[0].size
    sheet = Image.new("RGB", (w_, h_ * 3))
    for k, im in enumerate((images[0], images[len(images) // 2], images[-1])):
        sheet.paste(im, (0, k * h_))
    palette = sheet.quantize(colors=224, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames_p = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = [900] + [70] * (len(frames_p) - 2) + [2200]
    frames_p[0].save(OUT / f"heat_rod_{theme}.gif", save_all=True, append_images=frames_p[1:],
                     duration=durations, loop=0, optimize=True, disposal=1)


FIGURES = [fig_banner, fig_cfd_problem, fig_grid_methods, fig_finite_differences,
           fig_explicit_implicit, fig_stability, fig_solvers, fig_postprocessing]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, t in THEMES.items():
        for make in FIGURES:
            use_theme(t)
            make(t, theme)
            print(f"  ✓ {make.__name__.removeprefix('fig_')}_{theme}.svg")
        gif_heat_rod(t, theme)
        print(f"  ✓ heat_rod_{theme}.gif")


if __name__ == "__main__":
    main()
