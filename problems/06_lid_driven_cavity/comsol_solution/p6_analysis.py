import json, numpy as np
from p6_solver import *

out = {}
# ---- hand calc 4x4, first iteration from rest (row by row, bottom to top, left to right)
N = 4; h = 0.25
psi = np.zeros((5, 5)); w = np.zeros((5, 5))
it, hist = solve(N, 1.0, 1.0, 0.0, 1, psi, w)   # one iteration (tol 0 => runs exactly maxit=1)
out["hand_it1_w"] = w.tolist(); out["hand_it1_psi"] = psi.tolist()
print("iteration 1, N=4:"); print("w (rows j=4..0, cols i=0..4)"); print(np.round(w.T[::-1], 5)); print("psi"); print(np.round(psi.T[::-1], 6))
psi2 = psi.copy(); w2 = w.copy()
solve(N, 1.0, 1.0, 0.0, 1, psi2, w2)   # second iteration continuing
out["hand_it2_w"] = w2.tolist(); out["hand_it2_psi"] = psi2.tolist()
print("iteration 2:"); print(np.round(w2.T[::-1], 5)); print(np.round(psi2.T[::-1], 6))

# ---- all grids
res = {}
fields = {}
for N in [4, 8, 16, 32, 64, 128]:
    psi, w, it, hist = run(N, 1.0, 1.0, 1e-8, 400000)
    xc, yc, pmin, pmin_node, xn, yn = centre(psi, N)
    ug, vg = centreline(psi, N)
    eu = np.max(np.abs(ug - GHIA_U)); ev = np.max(np.abs(vg - GHIA_V))
    ru = np.sqrt(np.mean((ug - GHIA_U)**2)); rv = np.sqrt(np.mean((vg - GHIA_V)**2))
    res[N] = dict(it=int(it), res=float(hist[-1]), psi_min_node=float(pmin_node), psi_min=float(pmin), xc=float(xc), yc=float(yc),
                  max_err_u=float(eu), max_err_v=float(ev), rms_u=float(ru), rms_v=float(rv),
                  w_lid_mid=float(w[N // 2, N]), recell=U * (1.0 / N) / NU)
    print(N, res[N])
    fields[N] = (psi, w)
    np.save("p6_psi_%d.npy" % N, psi); np.save("p6_w_%d.npy" % N, w)
out["grid"] = res
Ns = [4, 8, 16, 32, 64, 128]
pm = [res[n]["psi_min"] for n in Ns]
# order from three finest grids
d = [pm[k + 1] - pm[k] for k in range(5)]
ratios = [d[k] / d[k + 1] for k in range(4)]
print("psi_min", pm); print("diff", d); print("ratio", ratios, "orders", [np.log2(r) for r in ratios])
out["pm"] = pm; out["orders"] = [float(np.log2(r)) for r in ratios]
p = np.log2(ratios[-1]); extrap = pm[-1] + d[-1] / (2**p - 1)
print("Richardson psi_min", extrap, "p", p)
out["richardson"] = float(extrap)
# errors vs Ghia psi
errs = [abs(res[n]["psi_min"] - GHIA_PSI) for n in Ns]
out["psi_err_ghia"] = errs
print("err vs ghia", errs, [np.log2(errs[k] / errs[k + 1]) for k in range(5)])
# max errors in centreline
print("u err", [res[n]["max_err_u"] for n in Ns]); print("v err", [res[n]["max_err_v"] for n in Ns])
# 32 grid comparison table
psi, w = fields[32]; ug, vg = centreline(psi, 32)
out["tab32"] = dict(y=GHIA_Y.tolist(), ug=GHIA_U.tolist(), u32=ug.tolist(), x=GHIA_X.tolist(), vg=GHIA_V.tolist(), v32=vg.tolist())
psi, w = fields[128]; ug, vg = centreline(psi, 128)
out["tab128"] = dict(u=ug.tolist(), v=vg.tolist())
# corner eddies on 128 grid
psi = fields[128][0]
sub = psi[int(0.5 * 128):, :int(0.5 * 128)]  # bottom right
iB, jB = np.unravel_index(np.argmax(sub), sub.shape); print("BR eddy psi max", sub.max(), (iB + 64) / 128, jB / 128)
sub = psi[:int(0.5 * 128), :int(0.5 * 128)]
iL, jL = np.unravel_index(np.argmax(sub), sub.shape); print("BL eddy psi max", sub.max(), iL / 128, jL / 128)
out["eddy_br"] = [float(psi[int(.5*128):, :64].max()), (iB + 64) / 128, jB / 128]
out["eddy_bl"] = [float(sub.max()), iL / 128, jL / 128]
# Does the 32 grid see the eddies?
p32 = fields[32][0]; print("32 grid max psi", p32.max(), "128 grid max psi", psi.max())
out["psi_max32"] = float(p32.max()); out["psi_max128"] = float(psi.max())
# convergence history N=32
_, _, it, hist = run(32, 1.0, 1.0, 1e-8, 400000)
np.save("p6_hist32.npy", hist)
# spin-up: Residual after k iterations N=32 psi_min vs iteration
spin = []
psi = np.zeros((33, 33)); w = np.zeros((33, 33))
for k in [1, 2, 5, 10, 20, 50, 100, 200, 400, 800, 1299]:
    psi = np.zeros((33, 33)); w = np.zeros((33, 33)); solve(32, 1.0, 1.0, 0.0, k, psi, w)
    spin.append((k, float(psi.min())))
out["spin"] = spin; print(spin)
# vorticity stats
w = fields[32][1]
out["w32_lid_max"] = float(w[:, 32].max()); out["w32_lid_min"] = float(w[:, 32].min())
# tolerance study N=32
tt = {}
for tol in [1e-4, 1e-6, 1e-8, 1e-10]:
    psi, w, it, hist = run(32, 1.0, 1.0, tol, 400000); tt[tol] = (int(it), float(psi.min()))
out["tol32"] = {str(k): v for k, v in tt.items()}; print(tt)
json.dump(out, open("p6_numbers.json", "w"), indent=1)
