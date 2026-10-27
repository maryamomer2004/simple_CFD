"""Drawing helpers for Problem 5 (steady convection and diffusion in 1D).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging

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

SCHEME = {"CDS": (ORANGE, "o", "central (CDS)"), "UDS": (BLUE, "s", "upwind (UDS)")}


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def schematic(L, phi_0, phi_L):
    """The channel between two reservoirs, with the flow and the two transport mechanisms."""
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    ax.set_xlim(-0.36, 1.36)
    ax.set_ylim(-0.5, 0.38)
    ax.axis("off")
    # reservoirs, coloured by their value of phi
    ax.add_patch(Rectangle((-0.3, -0.34), 0.3, 0.68, fc=HEAT(0.75), ec=INK2, lw=1.0))
    ax.add_patch(Rectangle((1.0, -0.34), 0.3, 0.68, fc=HEAT(0.02), ec=INK2, lw=1.0))
    ax.text(-0.15, 0.2, "reservoir", ha="center", fontsize=8.5, color="white")
    ax.text(-0.15, -0.02, f"$\\phi_0$ = {phi_0:g}", ha="center", fontsize=11, color="white")
    ax.text(1.15, 0.2, "reservoir", ha="center", fontsize=8.5, color=INK2)
    ax.text(1.15, -0.02, f"$\\phi_L$ = {phi_L:g}", ha="center", fontsize=11, color=INK)
    # the channel, coloured by a typical profile
    xx = [j / 200 for j in range(201)]
    ax.imshow([[1 - (2.718281828 ** (3 * v) - 1) / (2.718281828 ** 3 - 1) for v in xx]], cmap=HEAT,
              vmin=0, vmax=1.33, aspect="auto", extent=(0, 1, -0.1, 0.1), zorder=1)
    ax.plot([0, 1], [0.1, 0.1], color=INK2, lw=1.2)
    ax.plot([0, 1], [-0.1, -0.1], color=INK2, lw=1.2)
    # flow and transport mechanisms
    _arrow(ax, (0.3, 0.0), (0.7, 0.0), color=INK, lw=1.8, scale=14)
    ax.text(0.5, 0.025, "flow, velocity $u$", ha="center", va="bottom", fontsize=9, color=INK)
    _arrow(ax, (0.12, 0.2), (0.42, 0.2), color=ORANGE, lw=1.4)
    ax.text(0.27, 0.24, "convection: carried\ndownstream by the flow", ha="center", va="bottom",
            fontsize=8.5, color=INK2)
    _arrow(ax, (0.6, 0.2), (0.88, 0.2), color=BLUE, style="<|-|>", lw=1.4)
    ax.text(0.74, 0.24, "diffusion: spreads\nin both directions", ha="center", va="bottom",
            fontsize=8.5, color=INK2)
    # x axis and length
    _arrow(ax, (0, -0.24), (1, -0.24), style="<->", lw=1.0, scale=8)
    ax.text(0.5, -0.27, f"$L$ = {L:g} m", ha="center", va="top", fontsize=9.5)
    ax.text(0.015, -0.12, "x = 0", ha="left", va="top", fontsize=8, color=INK2)
    ax.text(0.985, -0.12, "x = L", ha="right", va="top", fontsize=8, color=INK2)
    ax.text(0.5, -0.42, r"steady:  $\dfrac{d(\rho u\phi)}{dx} = \dfrac{d}{dx}\left(\Gamma\dfrac{d\phi}{dx}\right)$",
            ha="center", va="center", fontsize=10.5, color=INK)
    plt.show()


def grid(x):
    """Nodes of the 1D grid: two known boundary nodes and the unknowns in between."""
    fig, ax = plt.subplots(figsize=(7.2, 1.9))
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.05, top=0.95)
    ax.axis("off")
    L, dx, N = x[-1], x[1] - x[0], len(x) - 1
    ax.add_patch(Rectangle((0, -0.02), L, 0.04, fc="#e3eefc", ec=INK2, lw=1))
    ax.scatter(x[1:-1], [0] * (N - 1), s=60, color=BLUE, ec="white", lw=1.2, zorder=3)
    ax.scatter([x[0], x[-1]], [0, 0], s=70, color=RED, ec="white", lw=1.2, zorder=4)
    for i, xi in enumerate(x):
        ax.text(xi, -0.075, str(i), ha="center", va="top", fontsize=9, color=INK)
    ax.text(-0.025 * L, -0.075, "i =", ha="right", va="top", fontsize=9, color=INK2)
    ax.text(x[0], 0.05, "$\\phi_0$ = 1\n(known)", ha="center", va="bottom", fontsize=8, color=INK2)
    ax.text(x[-1], 0.05, "$\\phi_N$ = 0\n(known)", ha="center", va="bottom", fontsize=8, color=INK2)
    for lab, k in (("W", 1), ("P", 2), ("E", 3)):
        ax.text(x[k], 0.05, lab, ha="center", va="bottom", fontsize=9, color=VIOLET, weight="bold")
    _arrow(ax, (x[3], -0.035), (x[4], -0.035), style="<->", lw=0.9, scale=7)
    ax.text((x[3] + x[4]) / 2, -0.045, f"$\\Delta x$ = {dx:g} m", ha="center", va="top", fontsize=9)
    _arrow(ax, (x[0] + 0.25 * dx, 0.1), (x[0] + 0.75 * dx, 0.1), color=INK, lw=1.3)
    ax.text(x[0] + 0.8 * dx, 0.1, "flow", va="center", fontsize=8.5, color=INK)
    ax.set_xlim(-0.08 * L, 1.06 * L)
    ax.set_ylim(-0.13, 0.15)
    plt.show()


def exact_family(L, phi_exact, rho, Gamma):
    """Exact profiles for several velocities: convection pushes the profile downstream."""
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.15, top=0.9)
    xx = [L * j / 400 for j in range(401)]
    ax.plot(xx, [1 - v / L for v in xx], color=MUTED, lw=1.6, ls="--", label="u = 0  (pure diffusion)")
    for color, u in zip((STEPS[2], STEPS[4], STEPS[6]), (0.1, 0.5, 2.5)):
        ax.plot(xx, [phi_exact(v, u) for v in xx], color=color, lw=2,
                label=f"u = {u:g} m/s  ($Pe_L$ = {rho * u * L / Gamma:g})")
    ax.set_xlabel("x [m]")
    ax.set_ylabel(r"$\phi$")
    ax.set_xlim(0, L)
    ax.set_ylim(0, 1.05)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title("Exact solution: the faster the flow, the further downstream the drop")
    plt.show()


def profiles(x, phi_cds, phi_uds, phi_exact, title, bounds=False, show_error=False):
    """CDS and UDS node values against the exact solution (and, optionally, their errors)."""
    if show_error:
        fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={"width_ratios": [1.5, 1]})
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.86, wspace=0.34)
    else:
        fig, ax = plt.subplots(figsize=(6.6, 3.5))
        fig.subplots_adjust(left=0.11, right=0.97, bottom=0.15, top=0.9)
    L = x[-1]
    xx = [L * j / 400 for j in range(401)]
    if bounds:
        ax.axhspan(1, 1.6, color="#fde4d8", lw=0, zorder=0)
        ax.text(0.02 * L, 1.52, r"$\phi > 1$: impossible in the real problem", fontsize=8.5,
                color=RED, va="top")
    ax.plot(xx, [phi_exact(v) for v in xx], color=INK, lw=1.6, label="exact solution", zorder=2)
    for name, values, ls in (("CDS", phi_cds, "-"), ("UDS", phi_uds, "--")):
        color, marker, label = SCHEME[name]
        ax.plot(x, values, color=color, lw=1.4, ls=ls, marker=marker, ms=6, mec="white",
                label=label, zorder=3)
    ax.set_xlabel("x [m]")
    ax.set_ylabel(r"$\phi$")
    ax.set_xlim(-0.02 * L, 1.02 * L)
    ax.set_ylim(-0.05, 1.6 if bounds else 1.08)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=9)
    if show_error:
        fig.suptitle(title, x=0.09, ha="left", fontsize=11, fontweight="semibold", color=INK)
        ax.set_title("node values", fontsize=9.5, color=INK2, fontweight="normal")
        ax2.axhline(0, color=INK, lw=1)
        for name, values in (("CDS", phi_cds), ("UDS", phi_uds)):
            color, marker, label = SCHEME[name]
            ax2.plot(x, [v - phi_exact(xi) for xi, v in zip(x, values)], color=color, lw=1.4,
                     marker=marker, ms=6, mec="white", label=label)
        ax2.set_xlabel("x [m]")
        ax2.set_ylabel("FDM − exact")
        ax2.grid(color=GRID, lw=0.6)
        ax2.set_axisbelow(True)
        ax2.set_title("error at the nodes", fontsize=9.5, color=INK2, fontweight="normal")
    else:
        ax.set_title(title)
    plt.show()


def false_diffusion(x, phi_uds, phi_exact, phi_exact_uds, Gamma, Gamma_uds):
    """The upwind points follow the exact solution of a much more diffusive fluid."""
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.15, top=0.9)
    L = x[-1]
    xx = [L * j / 400 for j in range(401)]
    ax.plot(xx, [phi_exact(v) for v in xx], color=INK, lw=1.6, label=f"exact, real $\\Gamma$ = {Gamma:g}")
    ax.plot(xx, [phi_exact_uds(v) for v in xx], color=BLUE, lw=1.4, ls=":",
            label=f"exact, $\\Gamma$ + false diffusion = {Gamma_uds:g}")
    color, marker, label = SCHEME["UDS"]
    ax.plot(x, phi_uds, color=color, lw=0, marker=marker, ms=7, mec="white", label=label, zorder=3)
    ax.set_xlabel("x [m]")
    ax.set_ylabel(r"$\phi$")
    ax.set_xlim(-0.02 * L, 1.02 * L)
    ax.set_ylim(-0.05, 1.08)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_title("False diffusion: upwind behaves like a more diffusive fluid")
    plt.show()


def refined_profiles(L, solutions, phi_exact, peclets):
    """CDS and UDS on finer and finer grids, zoomed on the boundary layer near the outlet."""
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.5), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.3, top=0.9, wspace=0.08)
    x0 = 0.5 * L
    xx = [x0 + (L - x0) * j / 300 for j in range(301)]
    shades = STEPS[2::2]
    for ax, name in zip(axes, ("CDS", "UDS")):
        ax.axhspan(1, 1.25, color="#fde4d8", lw=0, zorder=0)
        ax.plot(xx, [phi_exact(v) for v in xx], color=INK, lw=1.6, label="exact", zorder=2)
        for color, n in zip(shades, peclets):
            xs = [L * i / n for i in range(n + 1)]
            keep = [i for i in range(n + 1) if xs[i] >= x0 - 1e-12]
            ax.plot([xs[i] for i in keep], [solutions[name][n][i] for i in keep], color=color, lw=1.4,
                    marker=SCHEME[name][1], ms=4, mec="white", mew=0.6,
                    label=f"N = {n}  ($Pe_\\Delta$ = {peclets[n]:g})")
        ax.set_title(SCHEME[name][2])
        ax.set_xlabel("x [m]")
        ax.set_xlim(x0, L * 1.01)
        ax.set_ylim(-0.05, 1.25)
        ax.grid(color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel(r"$\phi$")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0), columnspacing=1.2, handlelength=1.8)
    plt.show()


def convergence(dxs, errors, dx_critical):
    """Grid-refinement study: largest error versus grid spacing on log-log axes."""
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.27, top=0.92)
    ax.axvspan(dx_critical, max(dxs) * 1.3, color="#fde4d8", lw=0, zorder=0)
    ax.text(max(dxs) * 1.2, 1.0e-4, "$Pe_\\Delta > 2$:\nCDS wiggles", ha="right", fontsize=8.5,
            color=RED)
    for name in ("CDS", "UDS"):
        color, marker, label = SCHEME[name]
        ax.loglog(dxs, errors[name], color=color, lw=1.8, marker=marker, ms=6, mec="white", label=label)
    fine = dxs[-4:]
    ax.loglog(fine, [errors["UDS"][-1] * 1.8 * (v / dxs[-1]) for v in fine], color=MUTED, lw=1.1,
              ls="--", label=r"slope 1  ($\propto\Delta x$)")
    ax.loglog(fine, [errors["CDS"][-1] * 0.45 * (v / dxs[-1]) ** 2 for v in fine], color=MUTED, lw=1.1,
              label=r"slope 2  ($\propto\Delta x^2$)")
    ax.set_xticks(dxs, [f"{v:g}" for v in dxs], fontsize=8.5)
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(min(dxs) * 0.8, max(dxs) * 1.3)
    ax.set_ylim(5e-5, 1.0)
    ax.set_xlabel(r"grid spacing $\Delta x$ [m]")
    ax.set_ylabel("largest error")
    ax.set_title("Verification, u = 2.5 m/s: CDS 2nd order, UDS only 1st order")
    ax.grid(color=GRID, lw=0.6, which="major")
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=2, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0), columnspacing=2.0, handlelength=2.2)
    plt.show()


def gauss_seidel(runs, tol):
    """Largest change per Gauss-Seidel sweep for several schemes and grids."""
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.15, top=0.9)
    colors = (AQUA, BLUE, RED, VIOLET)
    for color, ((scheme, Pe), changes) in zip(colors, runs.items()):
        ax.semilogy(range(1, len(changes) + 1), changes, color=color, lw=1.8,
                    label=f"{scheme}, $Pe_\\Delta$ = {Pe:g}")
    ax.axhline(tol, color=MUTED, lw=1)
    ax.text(1, tol * 2, "tolerance", fontsize=8.5, color=INK2)
    ax.set_xlabel("sweep")
    ax.set_ylabel("largest change")
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("Gauss–Seidel: CDS at $Pe_\\Delta$ = 5 diverges")
    plt.show()
