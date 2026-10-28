"""Lid-driven cavity, stream function - vorticity, FDM, Gauss-Seidel (Problem 6)."""
import numpy as np
from numba import njit

U, L, NU = 1.0, 1.0, 0.01


@njit(cache=True)
def solve(N, relax_w, relax_p, tol, maxit, psi, w):
    h = 1.0 / N
    hist = np.zeros(maxit)
    it = 0
    for it in range(1, maxit + 1):
        # 1) wall vorticity (Thom)
        for k in range(N + 1):
            w[k, 0] = -2.0 * (psi[k, 1] - psi[k, 0]) / h**2                    # bottom (i=x index, j=y index)
            w[k, N] = -2.0 * (psi[k, N - 1] - psi[k, N]) / h**2 - 2.0 * U / h  # lid
            w[0, k] = -2.0 * (psi[1, k] - psi[0, k]) / h**2                    # left
            w[N, k] = -2.0 * (psi[N - 1, k] - psi[N, k]) / h**2                # right
        w[0, N] = 0.5 * (w[0, N - 1] + w[1, N]); w[N, N] = 0.5 * (w[N, N - 1] + w[N - 1, N])
        w[0, 0] = 0.5 * (w[0, 1] + w[1, 0]); w[N, 0] = 0.5 * (w[N, 1] + w[N - 1, 0])
        dw = 0.0
        # 2) vorticity sweep (central differences)
        for j in range(1, N):
            for i in range(1, N):
                u = (psi[i, j + 1] - psi[i, j - 1]) / (2 * h)
                v = -(psi[i + 1, j] - psi[i - 1, j]) / (2 * h)
                aE = NU / h**2 - u / (2 * h)
                aW = NU / h**2 + u / (2 * h)
                aN = NU / h**2 - v / (2 * h)
                aS = NU / h**2 + v / (2 * h)
                new = (aE * w[i + 1, j] + aW * w[i - 1, j] + aN * w[i, j + 1] + aS * w[i, j - 1]) / (4 * NU / h**2)
                new = w[i, j] + relax_w * (new - w[i, j])
                d = abs(new - w[i, j])
                if d > dw: dw = d
                w[i, j] = new
        dp = 0.0
        # 3) stream function sweep
        for j in range(1, N):
            for i in range(1, N):
                new = 0.25 * (psi[i + 1, j] + psi[i - 1, j] + psi[i, j + 1] + psi[i, j - 1] + h**2 * w[i, j])
                new = psi[i, j] + relax_p * (new - psi[i, j])
                d = abs(new - psi[i, j])
                if d > dp: dp = d
                psi[i, j] = new
        hist[it - 1] = max(dw, dp)
        if max(dw, dp) < tol:
            break
        if not np.isfinite(dw):
            break
    return it, hist[:it]


def run(N, relax_w=1.0, relax_p=1.0, tol=1e-8, maxit=200000):
    psi = np.zeros((N + 1, N + 1)); w = np.zeros((N + 1, N + 1))
    it, hist = solve(N, relax_w, relax_p, tol, maxit, psi, w)
    return psi, w, it, hist


def centre(psi, N):
    """parabolic refinement of the extremum of psi (closest to the minimum)."""
    h = 1.0 / N
    i, j = np.unravel_index(np.argmin(psi), psi.shape)
    # fit quadratic through 3x3 block
    xs = np.array([-1, 0, 1]); X, Y = np.meshgrid(xs, xs, indexing="ij")
    blk = psi[i - 1:i + 2, j - 1:j + 2]
    A = np.c_[np.ones(9), X.ravel(), Y.ravel(), X.ravel()**2, (X * Y).ravel(), Y.ravel()**2]
    c = np.linalg.lstsq(A, blk.ravel(), rcond=None)[0]
    M = np.array([[2 * c[3], c[4]], [c[4], 2 * c[5]]]); b = -np.array([c[1], c[2]])
    s = np.linalg.solve(M, b)
    val = c[0] + c[1] * s[0] + c[2] * s[1] + c[3] * s[0]**2 + c[4] * s[0] * s[1] + c[5] * s[1]**2
    return (i + s[0]) * h, (j + s[1]) * h, val, psi[i, j], i * h, j * h


GHIA_Y = np.array([1.0, .9766, .9688, .9609, .9531, .8516, .7344, .6172, .5, .4531, .2813, .1719, .1016, .0703, .0625, .0547, 0.0])
GHIA_U = np.array([1.0, .84123, .78871, .73722, .68717, .23151, .00332, -.13641, -.20581, -.21090, -.15662, -.10150, -.06434, -.04775, -.04192, -.03717, 0.0])
GHIA_X = np.array([1.0, .9688, .9609, .9531, .9453, .9063, .8594, .8047, .5, .2344, .2266, .1563, .0938, .0781, .0703, .0625, 0.0])
GHIA_V = np.array([0.0, -.05906, -.07391, -.08864, -.10313, -.16914, -.22445, -.24533, .05454, .17527, .17507, .16077, .12317, .1089, .10091, .09233, 0.0])
GHIA_PSI = -0.103423; GHIA_XC, GHIA_YC = 0.6172, 0.7344


def velocities(psi, N):
    h = 1.0 / N
    u = np.zeros_like(psi); v = np.zeros_like(psi)
    u[:, 1:-1] = (psi[:, 2:] - psi[:, :-2]) / (2 * h)
    v[1:-1, :] = -(psi[2:, :] - psi[:-2, :]) / (2 * h)
    u[:, N] = U
    return u, v


def centreline(psi, N):
    """u(0.5, y) and v(x, 0.5) with interpolation at the Ghia stations"""
    h = 1.0 / N
    u, v = velocities(psi, N)
    xs = np.linspace(0, 1, N + 1)
    # vertical centreline x = 0.5: average the two columns if N odd (never here)
    uc = u[N // 2, :]; vc = v[:, N // 2]
    ug = np.interp(GHIA_Y, xs, uc); vg = np.interp(GHIA_X, xs, vc)
    return ug, vg
