"""Problem 4: fireclay brick column, 3 sides 500 K, bottom convection. FDM, 8 unknowns + grid study."""
import numpy as np, json
Ts, Tinf, h, k, W = 500., 300., 10., 1., 1.
dx = 0.25; Bi = h * dx / k
print("Bi =", Bi)
A = np.zeros((8, 8)); b = np.zeros(8)
def row(i, coeffs, rhs):
    for j, v in coeffs.items(): A[i - 1, j - 1] = v
    b[i - 1] = rhs
row(1, {1: 4, 2: -1, 3: -1}, 2 * Ts)
row(2, {2: 4, 1: -2, 4: -1}, Ts)
row(3, {3: 4, 1: -1, 4: -1, 5: -1}, Ts)
row(4, {4: 4, 3: -2, 2: -1, 6: -1}, 0)
row(5, {5: 4, 3: -1, 6: -1, 7: -1}, Ts)
row(6, {6: 4, 5: -2, 4: -1, 8: -1}, 0)
row(7, {7: 2 * (Bi + 2), 8: -1, 5: -2}, Ts + 2 * Bi * Tinf)
row(8, {8: 2 * (Bi + 2), 7: -2, 6: -2}, 2 * Bi * Tinf)
T = np.linalg.solve(A, b)
print("A|b\n", np.hstack([A, b[:, None]]))
print("T =", T)
# Gauss elimination with log of pivots
M = np.hstack([A, b[:, None]]); piv = []
for kk in range(7):
    for i in range(kk + 1, 8):
        f = M[i, kk] / M[kk, kk]; M[i, kk:] -= f * M[kk, kk:]
    piv.append(M[kk, kk])
print("upper\n", np.round(M, 4))
# Gauss-Seidel from 400 K
def gs(T0, tol=0.01, maxit=500):
    t = np.array(T0, float); hist = [t.copy()]
    for it in range(maxit):
        t[0] = (4*0 + t[1] + t[2] + 2*Ts) / 4
        t[1] = (2*t[0] + t[3] + Ts) / 4
        t[2] = (t[0] + t[3] + t[4] + Ts) / 4
        t[3] = (2*t[2] + t[1] + t[5]) / 4
        t[4] = (t[2] + t[5] + t[6] + Ts) / 4
        t[5] = (2*t[4] + t[3] + t[7]) / 4
        t[6] = (t[7] + 2*t[4] + Ts + 2*Bi*Tinf) / (2*(Bi + 2))
        t[7] = (2*t[6] + 2*t[5] + 2*Bi*Tinf) / (2*(Bi + 2))
        hist.append(t.copy())
        if np.max(np.abs(hist[-1] - hist[-2])) < tol: break
    return np.array(hist)
g = gs([400]*8); print("GS iterations from 400:", len(g) - 1); print(np.round(g[:6], 3)); print(g[-1])
g2 = gs([300]*8); print("GS from 300:", len(g2)-1)
# heat rate (trapezoid) and conduction balance
T7, T8 = T[6], T[7]
qconv = h * dx * ((Ts - Tinf)/2 + (T7 - Tinf) + (T8 - Tinf) + (T7 - Tinf) + (Ts - Tinf)/2)
print("q' trapezoid = %.3f W/m" % qconv)
T1,T2,T3,T4,T5,T6 = T[:6]
top = (Ts-T1)+(Ts-T2)+(Ts-T1)
left = (Ts-T1)+(Ts-T3)+(Ts-T5)
cond_in = top + 2*left + 2*0.5*(Ts-T7)    # k=1, weights per CV, corners at bottom: half
corner_conv = 2 * h*dx/2*(Ts-Tinf)
print("cond in (to interior CVs) = %.3f ; conv out of nodes 7,8,7' = %.3f" % (cond_in, h*dx*(2*(T7-Tinf)+(T8-Tinf))))
print("plus corner convection supplied by wall: %.3f -> total %.3f" % (corner_conv, cond_in + corner_conv))

# ---- full grid study: N x N cells, unknown all non-fixed nodes ----
import scipy.sparse as sp, scipy.sparse.linalg as spl
def solve(N):
    d = W / N; Bi_ = h * d / k
    # nodes (i,j) i=0..N x, j=0..N y (j=0 bottom). unknown: 1<=i<=N-1, 0<=j<=N-1
    idx = {}; 
    for j in range(0, N):
        for i in range(1, N): idx[(i, j)] = len(idx)
    n = len(idx); Am = sp.lil_matrix((n, n)); bm = np.zeros(n)
    for (i, j), r in idx.items():
        if j == 0:
            # surface node, half control volume (nodes i=1..N-1 at j=0)
            diag = 2 * (Bi_ + 2); bm[r] = 2 * Bi_ * Tinf
            for ii in (i - 1, i + 1):
                if ii in (0, N): bm[r] += Ts
                else: Am[r, idx[(ii, 0)]] -= 1
            Am[r, idx[(i, 1)]] -= 2
            Am[r, r] = diag
        else:
            Am[r, r] = 4
            for ii, jj in ((i-1, j), (i+1, j), (i, j-1), (i, j+1)):
                if ii in (0, N) or jj == N: bm[r] += Ts
                else: Am[r, idx[(ii, jj)]] -= 1
    t = spl.spsolve(Am.tocsr(), bm)
    bottom = [Ts] + [t[idx[(i, 0)]] for i in range(1, N)] + [Ts]
    q = h * d * (sum(bottom) - sum(bottom[0:1]) - sum(bottom[-1:]) - (N - 1) * Tinf + 0.5 * (bottom[0] - Tinf) + 0.5 * (bottom[-1] - Tinf))
    T_at = lambda x, y: t[idx[(int(round(x / d)), int(round(y / d)))]]
    return d, t, q, T_at
study = {}
for N in (4, 8, 16, 32, 64, 128, 256):
    d, t, q, Tat = solve(N)
    study[N] = dict(q=q, nodes=[Tat(.25,.75), Tat(.5,.75), Tat(.25,.5), Tat(.5,.5), Tat(.25,.25), Tat(.5,.25), Tat(.25,0), Tat(.5,0)])
    print(N, "q' = %.3f" % q, np.round(study[N]["nodes"], 3))
json.dump(dict(T=T.tolist(), Bi=Bi, qconv=qconv, cond_in=cond_in, corner_conv=corner_conv, gs_hist=g[:7].tolist(), gs_iters=len(g)-1,
               gs_iters_300=len(g2)-1, pivots=[float(x) for x in M.diagonal()],
               study={str(n): v for n, v in study.items()}), open(r"C:\Users\marya\Downloads\brick_comsol\p4_numbers.json", "w"), indent=1)
