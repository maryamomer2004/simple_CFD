"""Problem 3: 4 interior nodes of a square plate. FDM (Gauss, Gauss-Seidel), exact series, grid study."""
import numpy as np, json
Tt, Tl, Tr, Tb = 700., 100., 400., 500.
# unknown order: 1 (top-right), 2 (bottom-left), 3 (bottom-right), 4 (top-left)
A = np.array([[4, 0, -1, -1], [0, 4, -1, -1], [-1, -1, 4, 0], [-1, -1, 0, 4]], float)
b = np.array([Tt + Tr, Tl + Tb, Tr + Tb, Tt + Tl], float)
T = np.linalg.solve(A, b)
print("direct:", T)

# Gaussian elimination, verbose
M = np.hstack([A, b[:, None]]); print("aug\n", M)
n = 4
for k in range(n - 1):
    for i in range(k + 1, n):
        f = M[i, k] / M[k, k]
        M[i, k:] -= f * M[k, k:]
print("upper\n", M)
x = np.zeros(n)
for i in range(n - 1, -1, -1):
    x[i] = (M[i, -1] - M[i, i + 1:n] @ x[i + 1:n]) / M[i, i]
print("back-subst", x)

# Gauss-Seidel from T=0 and from T=425
def gs(T0, tol=1e-3, maxit=200):
    t = np.array(T0, float); hist = [t.copy()]
    for it in range(maxit):
        t[0] = (Tt + Tr + t[3] + t[2]) / 4
        t[3] = (Tt + Tl + t[0] + t[1]) / 4
        t[1] = (Tl + Tb + t[3] + t[2]) / 4
        t[2] = (Tr + Tb + t[0] + t[1]) / 4
        hist.append(t.copy())
        if np.max(np.abs(hist[-1] - hist[-2])) < tol: break
    return np.array(hist)
h = gs([0, 0, 0, 0])
print("GS from 0: iterations", len(h) - 1)
for i, r in enumerate(h[:9]): print(i, np.round(r, 3))
print("last", h[-1])
h2 = gs([425] * 4); print("GS from 425: iterations", len(h2) - 1)

# heat balance (units of k, dy/dx=1)
top = (Tt - T[3]) + (Tt - T[0]); left = (Tl - T[3]) + (Tl - T[1])
right = (Tr - T[0]) + (Tr - T[2]); bot = (Tb - T[1]) + (Tb - T[2])
print("flux top,left,right,bot (k*dT):", top, left, right, bot, "sum", top + left + right + bot)

# exact series (unit square), corner values not needed
def exact(x, y, N=401):
    s = 0.0
    for n_ in range(1, N, 2):
        a = n_ * np.pi
        c = 4 / a
        # sinh(a*u)/sinh(a) stable
        def r(u): return np.exp(-a * (1 - u)) * (1 - np.exp(-2 * a * u)) / (1 - np.exp(-2 * a))
        s += c * (Tb * np.sin(a * x) * r(1 - y) + Tt * np.sin(a * x) * r(y)
                  + Tl * np.sin(a * y) * r(1 - x) + Tr * np.sin(a * y) * r(x))
    return s
pts = {1: (2/3, 2/3), 2: (1/3, 1/3), 3: (2/3, 1/3), 4: (1/3, 2/3)}
ex = {k: exact(*v) for k, v in pts.items()}
print("exact:", ex)

# grid study: N x N cells, FDM via Gauss-Seidel/SOR, read nodes at (1/3,1/3) etc. for N multiple of 3
def fdm(N):
    u = np.zeros((N + 1, N + 1))   # u[j,i], j = y index
    u[N, :] = Tt; u[0, :] = Tb; u[:, 0] = Tl; u[:, N] = Tr
    for _ in range(100000):
        old = u[1:-1, 1:-1].copy()
        w = 1.8 if N > 3 else 1.0
        for j in range(1, N):
            for i in range(1, N):
                g = 0.25 * (u[j, i+1] + u[j, i-1] + u[j+1, i] + u[j-1, i])
                u[j, i] += w * (g - u[j, i])
        if np.max(np.abs(u[1:-1, 1:-1] - old)) < 1e-9: break
    return u
study = {}
for N in [3, 6, 12, 24]:
    u = fdm(N); k = N // 3
    v = {1: u[2*k, 2*k], 2: u[k, k], 3: u[k, 2*k], 4: u[2*k, k]}
    study[N] = v
    print(N, {q: round(v[q], 3) for q in v}, "max err", max(abs(v[q] - ex[q]) for q in v))
json.dump(dict(direct=T.tolist(), exact=ex, study={str(k): v for k, v in study.items()},
               gs_it=len(h) - 1, gs_hist=h[:9].tolist(),
               flux=[top, left, right, bot]), open("p3_numbers.json", "w"), indent=1)
