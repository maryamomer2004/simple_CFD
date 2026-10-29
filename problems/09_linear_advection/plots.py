"""Drawing helpers for Problem 9 (advection of a pulse, 1D, unsteady).

Only pictures are made here (with matplotlib). All the numerical work lives in
the notebook and uses plain Python, so you never need this file to follow the
finite difference method.
"""

import logging
import math

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.ticker import NullFormatter

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # quiet font fallback notes

BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#d03b3b"
INK, INK2, MUTED, GRID, SURFACE = "#1f2328", "#59636e", "#818b98", "#d8dee4", "#f6f8fa"
STEPS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
DYE = "#6250d6"

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

SCHEME = {"FTCS": (RED, "^", "FTCS"), "upwind": (BLUE, "s", "upwind"),
          "Lax-Wendroff": (ORANGE, "o", "Lax–Wendroff")}


def _arrow(ax, a, b, color=INK2, style="-|>", lw=1.3, scale=11):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=color, lw=lw,
                                 shrinkA=0, shrinkB=0))


def _style(ax, xlabel="x [m]", ylabel="u"):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def schematic(L, c, u0):
    """A closed flow loop with a dye pulse, and the same loop unrolled into the periodic domain."""
    fig = plt.figure(figsize=(7.6, 2.9))
    ax = fig.add_axes([0.0, 0.0, 0.34, 1.0])
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.25, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    # the loop: a ring of pipe, the dye pulse drawn as a dark arc
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec=INK2, lw=9, alpha=0.25))
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec=INK2, lw=0.8))
    for k in range(121):
        s = k / 120                        # position along the loop, as a fraction of L
        a = math.pi / 2 - 2 * math.pi * s  # clockwise from the top
        v = u0(s * L)
        if v > 0.02:
            ax.plot([0.93 * math.cos(a), 1.07 * math.cos(a)], [0.93 * math.sin(a), 1.07 * math.sin(a)],
                    color=DYE, alpha=min(1.0, v), lw=2.2, solid_capstyle="butt")
    ax.plot([0, 0], [0.86, 1.14], color=RED, lw=1.6)
    ax.text(0.0, 1.18, "x = 0 = L", ha="center", va="bottom", fontsize=8, color=RED)
    _arrow(ax, (0.62, 0.62), (0.80, 0.40), color=INK, lw=1.6, scale=12)
    ax.text(0.0, 0.08, "closed loop", ha="center", fontsize=9, color=INK)
    ax.text(0.0, -0.18, f"length L = {L:g} m", ha="center", fontsize=8.5, color=INK2)
    ax.text(0.0, -0.40, f"plug flow c = {c:g} m/s", ha="center", fontsize=8.5, color=INK2)
    ax.text(0.0, -1.2, "dye pulse", ha="center", fontsize=8.5, color=DYE)

    ax = fig.add_axes([0.42, 0.22, 0.56, 0.66])
    xx = [L * j / 400 for j in range(401)]
    ax.fill_between(xx, [u0(v) for v in xx], color=DYE, alpha=0.18, lw=0)
    ax.plot(xx, [u0(v) for v in xx], color=DYE, lw=2)
    ax.annotate("", xy=(0.72 * L, 0.75), xytext=(0.58 * L, 0.75),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6, mutation_scale=12))
    ax.text(0.65 * L, 0.8, "carried at speed c", ha="center", va="bottom", fontsize=8.5, color=INK)
    ax.annotate("", xy=(0.03 * L, 1.16), xytext=(0.97 * L, 1.16),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0, ls="--",
                                connectionstyle="arc3,rad=0.06", mutation_scale=9))
    ax.text(0.5 * L, 1.27, "what leaves at x = L comes back in at x = 0 (periodic)", ha="center",
            fontsize=8, color=RED)
    ax.set_xlim(0, L)
    ax.set_ylim(-0.05, 1.42)
    ax.set_yticks([0, 0.5, 1])
    _style(ax, ylabel="dye concentration u")
    ax.set_title(r"unrolled: $\partial u/\partial t + c\,\partial u/\partial x = 0$,  $0 \leq x \leq L$",
                 fontsize=10)
    plt.show()


def initial(L, pulses):
    """The two initial pulses."""
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 2.8), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.86, wspace=0.08)
    xx = [L * j / 1000 for j in range(1001)]
    for ax, (name, f) in zip(axes, pulses.items()):
        ax.fill_between(xx, [f(v) for v in xx], color=DYE, alpha=0.15, lw=0)
        ax.plot(xx, [f(v) for v in xx], color=DYE, lw=2)
        ax.set_title(name)
        ax.set_xlim(0, L)
        ax.set_ylim(-0.05, 1.15)
        _style(ax, ylabel="u(x, 0)" if ax is axes[0] else "")
    plt.show()


def exact_snapshots(L, c, u_exact, times):
    """The exact solution: the pulse moves around the loop without changing shape."""
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.88)
    xx = [L * j / 1000 for j in range(1001)]
    shades = [STEPS[2], STEPS[3], STEPS[4], STEPS[6], INK]
    for k, (color, t) in enumerate(zip(shades, times)):
        ax.plot(xx, [u_exact(v, t) for v in xx], color=color, lw=1.8, ls="--" if k == len(times) - 1 else "-",
                label=f"t = {t:g} s")
    ax.set_xlim(0, L)
    ax.set_ylim(-0.05, 1.12)
    _style(ax)
    ax.legend(loc="upper left", fontsize=8.5, ncol=5, bbox_to_anchor=(0.0, 1.02))
    ax.set_title(f"Exact solution: u(x, t) = u₀(x − ct), back at the start after t = L/c = {L / c:g} s",
                 fontsize=10.5)
    plt.show()


def grid(x, dt):
    """The periodic grid in x and t: nodes 0..N-1, node N is node 0 again."""
    N = len(x)
    dx = x[1] - x[0]
    L = N * dx
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    fig.subplots_adjust(left=0.03, right=0.97, bottom=0.04, top=0.96)
    ax.axis("off")
    for n in range(3):
        y = n * 1.0
        ax.plot([0, L], [y, y], color=GRID, lw=1, zorder=1)
        ax.scatter(x, [y] * N, s=46, color=BLUE, ec="white", lw=1.0, zorder=3)
        ax.scatter([L], [y], s=46, facecolor="white", ec=BLUE, lw=1.2, zorder=3)
        ax.text(-0.04 * L, y, ["$t^n$", "$t^{n+1}$", "$t^{n+2}$"][n], ha="right", va="center",
                fontsize=10, color=INK)
    for i, xi in enumerate(x):
        ax.text(xi, -0.3, str(i), ha="center", va="top", fontsize=9, color=INK)
    ax.text(L, -0.3, f"{N} = 0", ha="center", va="top", fontsize=9, color=BLUE)
    ax.text(-0.04 * L, -0.3, "i =", ha="right", va="top", fontsize=9, color=INK2)
    # a stencil in the middle
    k = N // 2
    for xi in (x[k - 1], x[k], x[k + 1]):
        _arrow(ax, (xi, 0.08), (x[k], 0.92), color=VIOLET, lw=1.0, scale=8)
    for lab, j in (("W", k - 1), ("P", k), ("E", k + 1)):
        ax.text(x[j] - 0.012 * L, 0.1, lab, ha="right", va="bottom", fontsize=8.5, color=VIOLET,
                weight="bold")
    _arrow(ax, (x[1], -0.15), (x[2], -0.15), style="<->", lw=0.9, scale=7)
    ax.text((x[1] + x[2]) / 2, -0.5, f"Δx = {dx:g} m", ha="center", va="top", fontsize=8.5,
            color=INK2)
    _arrow(ax, (L + 0.05 * L, 0), (L + 0.05 * L, 1), style="<->", lw=0.9, scale=7)
    ax.text(L + 0.065 * L, 0.5, f"Δt = {dt:g} s", ha="left", va="center", fontsize=8.5, color=INK2)
    ax.annotate("", xy=(x[0], 2.25), xytext=(L, 2.25),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0, ls="--",
                                connectionstyle="arc3,rad=0.06", mutation_scale=9))
    ax.text(L / 2, 2.7, "periodic: the east neighbour of node N − 1 is node 0, "
            "the west neighbour of node 0 is node N − 1", ha="center", fontsize=8, color=RED)
    ax.set_xlim(-0.12 * L, 1.2 * L)
    ax.set_ylim(-0.75, 3.0)
    plt.show()


def domain_of_dependence(courants):
    """The CFL condition: the characteristic through P at t^{n+1} must start inside the stencil."""
    fig, axes = plt.subplots(1, len(courants), figsize=(7.6, 2.8))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.84, wspace=0.12)
    for ax, C in zip(axes, courants):
        ax.axis("off")
        ax.set_xlim(-1.75, 1.5)
        ax.set_ylim(-0.45, 1.35)
        ax.plot([-1.6, 1.4], [0, 0], color=GRID, lw=1)
        ax.plot([-1.6, 1.4], [1, 1], color=GRID, lw=1)
        ax.fill_between([-1, 1], [0, 0], [-0.07, -0.07], color=AQUA, alpha=0.35, lw=0)
        ax.scatter([-1, 0, 1], [0, 0, 0], s=55, color=BLUE, ec="white", zorder=3)
        ax.scatter([0], [1], s=60, color=ORANGE, ec="white", zorder=3)
        for lab, xi in (("W", -1), ("P", 0), ("E", 1)):
            ax.text(xi, -0.14, lab, ha="center", va="top", fontsize=9, color=INK)
        ax.text(0, 1.08, "P at $t^{n+1}$", ha="center", va="bottom", fontsize=8.5, color=INK)
        ok = C <= 1
        color = AQUA if ok else RED
        ax.plot([0, -C], [1, 0], color=color, lw=2.2)
        ax.scatter([-C], [0], s=40, marker="x", color=color, zorder=4, lw=2)
        ax.text(-C - 0.08, 0.32, "characteristic\nx − ct = const", ha="right", fontsize=8, color=color)
        ax.set_title(f"C = {C:g}: " + ("starts inside the stencil" if ok else "starts OUTSIDE the stencil"),
                     fontsize=10, color=INK if ok else RED)
    plt.show()


def amplification(curves, C):
    """Von Neumann analysis: size of the amplification factor and phase speed for every wave."""
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.27, top=0.84, wspace=0.3)
    ticks = [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi]
    labels = ["0", "π/4", "π/2", "3π/4", "π"]
    ax.axhline(1, color=INK, lw=1, ls="--", label="exact")
    ax2.axhline(1, color=INK, lw=1, ls="--")
    for name, (thetas, mods, speeds) in curves.items():
        color, _, label = SCHEME[name]
        ax.plot(thetas, mods, color=color, lw=2, label=label)
        ax2.plot(thetas, speeds, color=color, lw=2, label=label)
    for a in (ax, ax2):
        a.set_xticks(ticks, labels)
        a.set_xlim(0, math.pi)
        a.grid(color=GRID, lw=0.6)
        a.set_axisbelow(True)
        a.set_xlabel(r"wave number per node $\theta = k\,\Delta x$  ($\pi$ = shortest wave, 2Δx)")
    ax.set_ylabel("|G| per time step")
    ax2.set_ylabel("numerical speed / c")
    ax.set_ylim(0, 1.25)
    ax2.set_ylim(0, 1.25)
    ax.set_title("amplitude", fontsize=10)
    ax2.set_title("phase speed", fontsize=10)
    fig.suptitle(f"Von Neumann analysis at C = {C:g}", x=0.08, ha="left", fontsize=11,
                 fontweight="semibold", color=INK)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def ftcs_blowup(x, snapshots, growth, C):
    """FTCS: the profile after a few steps, and the largest |u| against time."""
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.84, wspace=0.3)
    shades = [STEPS[2], STEPS[4], STEPS[6]]
    for color, (t, u) in zip(shades, snapshots.items()):
        ax.plot(x + [x[-1] + x[1] - x[0]], u + [u[0]], color=color, lw=1.4, label=f"t = {t:g} s")
    ax.set_xlim(0, x[-1] + x[1] - x[0])
    _style(ax)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("square pulse, FTCS", fontsize=10)
    for (label, (t, m)), color in zip(growth.items(), (DYE, INK2)):
        ax2.semilogy(t, m, color=color, lw=1.8, label=label)
    ax2.axhline(1, color=INK, lw=1)
    _style(ax2, xlabel="t [s]", ylabel="largest |u|")
    ax2.legend(loc="upper left", fontsize=8)
    ax2.set_title("growth during one lap", fontsize=10)
    fig.suptitle(f"FTCS at C = {C:g}: unstable", x=0.08, ha="left", fontsize=11,
                 fontweight="semibold", color=INK)
    plt.show()


def one_lap(x, results, u_exact, title):
    """Upwind and Lax-Wendroff after one lap against the exact solution, for both pulses."""
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.3), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.26, top=0.84, wspace=0.08)
    L = x[-1] + x[1] - x[0]
    xx = [L * j / 1000 for j in range(1001)]
    for ax, (pulse, by_scheme) in zip(axes, results.items()):
        ax.plot(xx, [u_exact[pulse](v) for v in xx], color=INK, lw=1.5, label="exact")
        for name, u in by_scheme.items():
            color, marker, label = SCHEME[name]
            ax.plot(x + [L], u + [u[0]], color=color, lw=1.6, label=label)
        ax.axhline(0, color=MUTED, lw=0.6)
        ax.set_title(pulse, fontsize=10)
        ax.set_xlim(0.2 * L, 0.8 * L)
        ax.set_ylim(-0.3, 1.3)
        _style(ax, ylabel="u" if ax is axes[0] else "")
    fig.suptitle(title, x=0.08, ha="left", fontsize=11, fontweight="semibold", color=INK)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def cfl_study(x, laps, growth, u_exact):
    """Square pulse after one lap at C = 0.5 and C = 1, and the blow-up at C > 1."""
    fig, axes = plt.subplots(1, 3, figsize=(7.8, 3.2), gridspec_kw={"width_ratios": [1, 1, 1.1]})
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.27, top=0.84, wspace=0.35)
    L = x[-1] + x[1] - x[0]
    xx = [L * j / 1000 for j in range(1001)]
    for ax, (C, by_scheme) in zip(axes, laps.items()):
        ax.plot(xx, [u_exact(v) for v in xx], color=INK, lw=1.5, label="exact")
        for name, u in by_scheme.items():
            color, marker, label = SCHEME[name]
            ax.plot(x + [L], u + [u[0]], color=color, lw=1.5, ls="-" if name == "upwind" else "--",
                    label=label)
        ax.set_title(f"C = {C:g}, one lap", fontsize=10)
        ax.set_xlim(0.25 * L, 0.75 * L)
        ax.set_ylim(-0.3, 1.3)
        _style(ax)
    ax = axes[2]
    for name, (t, m) in growth.items():
        color, _, label = SCHEME[name]
        ax.semilogy(t, m, color=color, lw=1.8, label=label)
    ax.axhline(1, color=INK, lw=1)
    _style(ax, xlabel="t [s]", ylabel="largest |u|")
    ax.set_title("C = 1.1: blow-up", fontsize=10, color=RED)
    fig.suptitle("Square pulse: the CFL limit C ≤ 1", x=0.07, ha="left", fontsize=11,
                 fontweight="semibold", color=INK)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def modified_equation(x, u_upwind, u_exact, u_diffused, D_num):
    """Upwind after one lap lies on the exact solution of a diffusion equation with D_num."""
    fig, ax = plt.subplots(figsize=(6.8, 3.3))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.15, top=0.9)
    L = x[-1] + x[1] - x[0]
    xx = [L * j / 1000 for j in range(1001)]
    ax.plot(xx, [u_exact(v) for v in xx], color=INK, lw=1.5, label="exact (no diffusion)")
    ax.plot(xx, [u_diffused(v) for v in xx], color=BLUE, lw=1.4, ls=":",
            label=f"exact with diffusion $D_{{num}}$ = {D_num:g} m²/s")
    color, marker, label = SCHEME["upwind"]
    ax.plot(x, u_upwind, color=color, lw=0, marker=marker, ms=4.5, mec="white", mew=0.6,
            label="upwind, after one lap", zorder=3)
    ax.set_xlim(0.2 * L, 0.8 * L)
    ax.set_ylim(-0.05, 1.1)
    _style(ax)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title("Upwind = advection + numerical diffusion")
    plt.show()


def convergence(dxs, errors, peaks):
    """Error study after one lap: largest error and peak against grid spacing."""
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.6), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.3, top=0.86, wspace=0.3)
    for name in errors:
        color, marker, label = SCHEME[name]
        ax.loglog(dxs, errors[name], color=color, lw=1.8, marker=marker, ms=5.5, mec="white", label=label)
        ax2.semilogx(dxs, peaks[name], color=color, lw=1.8, marker=marker, ms=5.5, mec="white")
    fine = dxs[-4:]
    ax.loglog(fine, [errors["upwind"][-1] * 1.7 * (v / dxs[-1]) for v in fine], color=MUTED, lw=1.1,
              ls="--", label=r"slope 1  ($\propto\Delta x$)")
    ax.loglog(fine, [errors["Lax-Wendroff"][-1] * 0.45 * (v / dxs[-1]) ** 2 for v in fine], color=MUTED,
              lw=1.1, label=r"slope 2  ($\propto\Delta x^2$)")
    ax2.axhline(1, color=INK, lw=1)
    for a in (ax, ax2):
        a.set_xticks(dxs, [f"{v:g}" for v in dxs], fontsize=7.5, rotation=45)
        a.xaxis.set_minor_formatter(NullFormatter())
        a.set_xlim(min(dxs) * 0.8, max(dxs) * 1.25)
        a.grid(color=GRID, lw=0.6, which="major")
        a.set_xlabel(r"grid spacing $\Delta x$ [m]")
    ax.set_ylabel("largest error after one lap")
    ax2.set_ylabel("peak after one lap")
    ax2.set_ylim(0, 1.1)
    ax.set_title("error", fontsize=10)
    ax2.set_title("peak (exact: 1)", fontsize=10)
    fig.suptitle("Gaussian pulse, C = 0.5: upwind 1st order, Lax–Wendroff 2nd order", x=0.09,
                 ha="left", fontsize=11, fontweight="semibold", color=INK)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()


def hand(levels, exact):
    """The whiteboard calculation: two time steps on the 8-node grid, for three schemes."""
    fig, axes = plt.subplots(1, len(levels), figsize=(7.8, 2.9), sharey=True)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.27, top=0.8, wspace=0.08)
    shades = [MUTED, STEPS[3], STEPS[6]]
    N = len(exact)
    width = 0.26
    for ax, (name, steps) in zip(axes, levels.items()):
        for k, (u, color) in enumerate(zip(steps, shades)):
            ax.bar([i + (k - 1) * width for i in range(N)], u, width=width, color=color,
                   label=["start", "after step 1", "after step 2"][k])
        peak = [i for i in range(N) if exact[i] != 0]
        ax.plot(peak, [exact[i] for i in peak], lw=0, marker="_", ms=14, mew=2, color=INK,
                label="exact after step 2")
        ax.axhline(0, color=INK, lw=0.8)
        ax.set_title(SCHEME[name][2], fontsize=10, color=SCHEME[name][0])
        ax.set_xticks(range(N))
        ax.set_xlabel("node i")
        ax.grid(color=GRID, lw=0.6, axis="y")
        ax.set_axisbelow(True)
    axes[0].set_ylabel("u")
    axes[0].set_ylim(-0.6, 1.1)
    fig.suptitle("By hand: 8 nodes, C = 0.5, two time steps", x=0.07, ha="left", fontsize=11,
                 fontweight="semibold", color=INK)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=8.5,
               bbox_to_anchor=(0.5, 0.0))
    plt.show()
