"""Problem 7: figures for the COMSOL guide - centre-line profiles and grid convergence
(COMSOL against the FDM notebook and de Vahl Davis 1983)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "p7_comsol_numbers.json")))
C, B, F = R["comsol"], R["bench"], R["fdm"]
RUN = {(32, 1000): 1, (32, 10000): 2, (64, 1000): 3, (64, 10000): 4, (128, 1000): 5, (128, 10000): 6}
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 10})
COL = {32: "#93c5fd", 128: "#2563eb"}


def cut(name, k):
    d = np.loadtxt(os.path.join(HERE, f"{name}_{k}.txt"), comments="%")
    return d[np.argsort(d[:, 1] if name == "cutx" else d[:, 0])]


def profiles():
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.1))
    for j, ra in enumerate((1000, 10000)):
        a = ax[j]
        for n in (32, 128):
            k = RUN[(n, ra)]
            cx, cy = cut("cutx", k), cut("cuty", k)
            a.plot(cx[:, 1], cx[:, 2], color=COL[n], lw=1.6 if n == 128 else 1.2,
                   ls="-" if n == 128 else "--", label=f"u(0.5, y), COMSOL {n}x{n}")
            a.plot(cy[:, 0], cy[:, 3], color="#16a34a" if n == 128 else "#86efac", lw=1.6 if n == 128 else 1.2,
                   ls="-" if n == 128 else "--", label=f"v(x, 0.5), COMSOL {n}x{n}")
        b = B[str(ra)]
        a.plot([b["yu"]], [b["umax"]], "s", ms=8, mfc="none", mec="k", mew=1.5, label="de Vahl Davis maxima")
        a.plot([b["xv"]], [b["vmax"]], "s", ms=8, mfc="none", mec="k", mew=1.5)
        a.axhline(0, color="0.6", lw=0.6)
        a.set_xlabel("position along the centre line (y for u, x for v)")
        a.set_ylabel("velocity  [alpha/L]")
        a.set_title(f"Ra = {ra:g}")
        a.grid(alpha=0.25)
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(os.path.join(HERE, "p7_profiles.png"), dpi=170)
    plt.close(fig)


def convergence():
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.0))
    for j, (q, qf, lab) in enumerate((("psi_mid", "psi", "|psi| at the centre"), ("nu_hot", "nu", "average Nusselt number"))):
        a = ax[j]
        for ra, mk in ((1000, "o"), (10000, "s")):
            bq = B[str(ra)][qf]
            hs = [1 / n for n in (8, 16, 32, 64)]
            fv = [F[str(ra)][str(n)][qf] / bq for n in (8, 16, 32, 64)]
            a.plot(hs, fv, mk + "-", color="#ea580c", ms=6, label=f"FDM, Ra = {ra:g}")
            hc = [1 / n for n in (32, 64, 128)]
            cv = [C[f"{n}_{ra}"][q] / bq for n in (32, 64, 128)]
            a.plot(hc, cv, mk + "-", color="#2563eb", ms=6, mfc="white", label=f"COMSOL, Ra = {ra:g}")
        a.axhline(1, color="k", lw=0.8)
        a.set_xscale("log", base=2)
        a.set_xticks([1 / 128, 1 / 64, 1 / 32, 1 / 16, 1 / 8])
        a.set_xticklabels(["1/128", "1/64", "1/32", "1/16", "1/8"])
        a.set_xlabel("grid spacing h")
        a.set_ylabel(lab + " / de Vahl Davis")
        a.grid(alpha=0.25)
        a.set_ylim(0.97, 1.06 if q == "nu_hot" else 1.16)
        if q == "nu_hot":
            a.annotate("FDM, N = 8, Ra = 1e4: 1.25 (off scale)", xy=(1 / 8, 1.06), xytext=(1 / 125, 1.045),
                       fontsize=8, arrowprops=dict(arrowstyle="->", color="0.4"))
        if j == 0:
            a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "p7_convergence.png"), dpi=170)
    plt.close(fig)


profiles()
convergence()
print("ok")
