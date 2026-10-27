import math, json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = r"C:\Users\marya\Downloads\phosphorus_comsol"
D = 6.5e-13 * 1e-4          # m^2/s
cs_atoms = 2.5e20           # atoms/cm^3
NA = 6.02214e23
cs = cs_atoms * 1e6 / NA    # mol/m^3
t_end = 3600.0
zmax = 5e-6


def erfcinv(y):
    lo, hi = 0.0, 6.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if math.erfc(mid) > y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def exact(z, t):
    return cs * np.vectorize(math.erfc)(z / (2 * math.sqrt(D * t)))


def depth(z, c, level):
    # first crossing of c = level going from surface (c decreasing)
    for i in range(len(z) - 1):
        if c[i] >= level >= c[i + 1] and c[i] != c[i + 1]:
            return z[i] + (level - c[i]) * (z[i + 1] - z[i]) / (c[i + 1] - c[i])
    return float("nan")


z_exact_depth = 2 * math.sqrt(D * t_end) * erfcinv(0.01)
print("sqrt(D t) = %.4e m ; 2 sqrt(D t) = %.4e m" % (math.sqrt(D * t_end), 2 * math.sqrt(D * t_end)))
print("erfc^-1(0.01) = %.5f" % erfcinv(0.01))
print("EXACT film depth at 1 h = %.4f um" % (z_exact_depth * 1e6))
print("cs = %.4f mol/m3 ; c_edge = %.4f" % (cs, 0.01 * cs))

# ---------- COMSOL export ----------
rows = [l.split() for l in open(OUT + r"\profiles_N50.txt") if not l.startswith("%") and l.strip()]
x = np.array([float(r[0]) for r in rows])
c = np.array([float(r[1]) for r in rows])
starts = [0] + [i for i in range(1, len(x)) if x[i] < x[i - 1]] + [len(x)]
curves = []
for a, b in zip(starts[:-1], starts[1:]):
    curves.append((x[a:b], c[a:b]))
times = [600 * (k + 1) for k in range(len(curves))]
print("COMSOL curves:", len(curves), "points each:", [len(cx) for cx, _ in curves])
res = {}
for (cx, cc), t in zip(curves, times):
    ce = exact(cx, t)
    err = np.max(np.abs(cc - ce))
    dpt = depth(cx, cc, 0.01 * cs)
    dex = 2 * math.sqrt(D * t) * erfcinv(0.01)
    print("t=%5d s  COMSOL depth %.4f um  exact %.4f um  max|c-c_exact| = %.3f mol/m3 (%.3f %% of cs)"
          % (t, dpt * 1e6, dex * 1e6, err, 100 * err / cs))
    res[t] = dict(comsol_depth_um=dpt * 1e6, exact_depth_um=dex * 1e6, max_abs_err=err)

# ---------- FTCS ----------

def ftcs(dz, dt, zmax=zmax, tend=t_end):
    n = int(round(zmax / dz))
    z = np.linspace(0, zmax, n + 1)
    u = np.zeros(n + 1)
    u[0] = cs
    steps = int(round(tend / dt))
    Fo = D * dt / dz**2
    for _ in range(steps):
        un = u.copy()
        un[1:-1] = u[1:-1] + Fo * (u[2:] - 2 * u[1:-1] + u[:-2])
        un[0] = cs
        un[-1] = 0.0
        u = un
    return z, u, Fo, steps


dzs = 0.1e-6
dt_max = dzs**2 / (2 * D)
print("\nFTCS stability: dt <= dz^2/(2D) = %.2f s  (dz = 0.1 um)" % dt_max)
z1, u1, Fo1, n1 = ftcs(dzs, 50.0)
d1 = depth(z1, u1, 0.01 * cs)
print("FTCS dz=0.1um dt=50 s (Fo=%.3f, %d steps): depth %.4f um, max err vs exact %.3f mol/m3 (%.3f %% cs)"
      % (Fo1, n1, d1 * 1e6, np.max(np.abs(u1 - exact(z1, t_end))), 100 * np.max(np.abs(u1 - exact(z1, t_end))) / cs))
conv = []
for dz in [0.2e-6, 0.1e-6, 0.05e-6, 0.025e-6]:
    dt = 0.4 * dz**2 / D
    # make dt divide 3600 evenly
    steps = math.ceil(t_end / dt)
    dt = t_end / steps
    z, u, Fo, st = ftcs(dz, dt)
    dd = depth(z, u, 0.01 * cs)
    e = np.max(np.abs(u - exact(z, t_end)))
    conv.append((dz * 1e6, dt, Fo, st, dd * 1e6, abs(dd - z_exact_depth) * 1e6, e / cs * 100))
    print("dz=%.3f um dt=%.2f s Fo=%.3f steps=%d  depth=%.4f um  depth err=%.4f um  max profile err=%.4f %% of cs"
          % conv[-1])
# unstable run
zu, uu, Fou, nu = ftcs(dzs, 100.0)
print("FTCS unstable dt=100 s (Fo=%.3f): max |c| = %.3e mol/m3 (cs = %.1f)" % (Fou, np.max(np.abs(uu)), cs))
zu2, uu2, Fou2, nu2 = ftcs(dzs, 80.0, tend=3600.0)
print("FTCS dt=80 s (Fo=%.3f): max |c| = %.3e" % (Fou2, np.max(np.abs(uu2))))

json.dump(dict(exact_depth_um=z_exact_depth * 1e6, comsol=res, ftcs50=dict(depth_um=d1 * 1e6, Fo=Fo1),
               conv=conv, dt_max=dt_max, cs=cs), open(OUT + r"\p2_numbers.json", "w"), indent=1)

# ---------- figure ----------
fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.6))
cols = plt.cm.viridis(np.linspace(0, 0.9, len(curves)))
zz = np.linspace(0, 4e-6, 400)
for (cx, cc), t, col in zip(curves, times, cols):
    ax[0].plot(cx * 1e6, cc / cs, color=col, lw=2.2, label="COMSOL, t = %d min" % (t // 60))
    ax[0].plot(zz * 1e6, exact(zz, t) / cs, "k--", lw=0.9)
ax[0].plot([], [], "k--", lw=0.9, label="exact erfc")
ax[0].axhline(0.01, color="crimson", lw=1)
ax[0].text(3.0, 0.03, "film edge  c = 1 % c$_s$", color="crimson", fontsize=9)
ax[0].set_xlim(0, 4)
ax[0].set_ylim(0, 1.02)
ax[0].set_xlabel("depth z ($\\mu$m)")
ax[0].set_ylabel("c / c$_s$")
ax[0].set_title("Phosphorus profiles in silicon (1100 C)")
ax[0].legend(fontsize=8)
ax[0].grid(alpha=0.3)
cx, cc = curves[-1]
ax[1].semilogy(cx * 1e6, np.maximum(cc / cs, 1e-12), color="tab:blue", lw=2.4, label="COMSOL (50 elements)")
ax[1].semilogy(z1 * 1e6, np.maximum(u1 / cs, 1e-12), "o", ms=4, color="tab:orange", label="FTCS dz=0.1 um, dt=50 s")
ax[1].semilogy(zz * 1e6, exact(zz, t_end) / cs, "k--", lw=1, label="exact")
ax[1].axhline(0.01, color="crimson", lw=1)
ax[1].axvline(z_exact_depth * 1e6, color="crimson", lw=1, ls=":")
ax[1].text(z_exact_depth * 1e6 + 0.05, 0.02, "%.3f um" % (z_exact_depth * 1e6), color="crimson", fontsize=9)
ax[1].set_xlim(0, 4)
ax[1].set_ylim(1e-6, 1.5)
ax[1].set_xlabel("depth z ($\\mu$m)")
ax[1].set_ylabel("c / c$_s$  (log scale)")
ax[1].set_title("After 1 h: COMSOL vs FTCS vs exact")
ax[1].legend(fontsize=8)
ax[1].grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(OUT + r"\p2_comparison.png", dpi=170)
print("figure saved")
