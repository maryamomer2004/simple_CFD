import json, numpy as np
from scipy.interpolate import CubicSpline
from p6_solver import GHIA_X, GHIA_Y, GHIA_U, GHIA_V, GHIA_PSI, centre, velocities

def load(N):
    rows = [l.split() for l in open("cav_n%d.txt" % N) if not l.startswith("%") and l.strip()]
    a = np.array(rows, dtype=float)
    x, y = a[:, 0], a[:, 1]
    ix = np.rint(x * N).astype(int); iy = np.rint(y * N).astype(int)
    out = {}
    for k, name in enumerate(["psi", "u", "v", "w"]):
        g = np.full((N + 1, N + 1), np.nan); g[ix, iy] = a[:, 2 + k]; out[name] = g
    assert not np.isnan(out["psi"]).any()
    return out

res = {}; fields = {}
for N in [4, 8, 16, 32, 64, 128]:
    d = load(N); fields[N] = d
    xc, yc, pm, pn, xn, yn = centre(d["psi"], N)
    xs = np.linspace(0, 1, N + 1)
    uc = CubicSpline(xs, d["u"][N // 2, :])(GHIA_Y); vc = CubicSpline(xs, d["v"][:, N // 2])(GHIA_X)
    res[N] = dict(psi_min_node=float(pn), psi_min=float(pm), xc=float(xc), yc=float(yc),
                  max_err_u=float(np.abs(uc - GHIA_U).max()), max_err_v=float(np.abs(vc - GHIA_V).max()),
                  rms_u=float(np.sqrt(np.mean((uc - GHIA_U)**2))), rms_v=float(np.sqrt(np.mean((vc - GHIA_V)**2))),
                  umax_all=float(d["u"].max()), u_lid_mid=float(d["u"][N // 2, N]))
    print(N, res[N])
Ns = [4, 8, 16, 32, 64, 128]
pm = [res[n]["psi_min"] for n in Ns]
dd = [pm[k + 1] - pm[k] for k in range(5)]
ordr = [float(np.log2(dd[k] / dd[k + 1])) for k in range(4)]
print("psi_min", pm, "orders", ordr)
errs = [abs(p - GHIA_PSI) for p in pm]
print("err vs Ghia", errs)
# FDM vs COMSOL on 32 grid, node by node
psi_f = np.load("p6_psi_32.npy"); w_f = np.load("p6_w_32.npy")
d = fields[32]
u_f, v_f = velocities(psi_f, 32)
print("max |psi_comsol-psi_fdm| N=32:", np.abs(d["psi"] - psi_f).max(), " at lid etc")
print("max |u diff| interior:", np.abs(d["u"][1:-1, 1:-1] - u_f[1:-1, 1:-1]).max(), "max |v diff|:", np.abs(d["v"][1:-1, 1:-1] - v_f[1:-1, 1:-1]).max())
print("rms psi diff:", np.sqrt(np.mean((d["psi"] - psi_f)**2)))
for N in [32, 64, 128]:
    pf = np.load("p6_psi_%d.npy" % N)
    print(N, "max psi diff COMSOL-FDM", np.abs(fields[N]["psi"] - pf).max(), "psi_min comsol %.5f fdm %.5f" % (res[N]["psi_min"], centre(pf, N)[2]))
# corner eddy ψ max in comsol 128
p = fields[128]["psi"]; print("comsol psi max 128", p.max(), np.unravel_index(p.argmax(), p.shape))
json.dump(dict(res={str(k): v for k, v in res.items()}, orders=ordr, pm=pm, errs=errs), open("p6_comsol_numbers.json", "w"), indent=1)
np.savez("p6_comsol_fields.npz", **{"psi%d" % N: fields[N]["psi"] for N in Ns}, **{"u%d" % N: fields[N]["u"] for N in Ns}, **{"v%d" % N: fields[N]["v"] for N in Ns}, **{"w%d" % N: fields[N]["w"] for N in Ns})
# cuts at N=32
print("u at x=.5 (COMSOL N=32):", np.round(d["u"][16, :], 4))
print("u at x=.5 (FDM N=32):", np.round(u_f[16, :], 4))
