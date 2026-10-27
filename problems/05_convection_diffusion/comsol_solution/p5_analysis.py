"""Problem 5: steady 1D convection-diffusion, CDS vs UDS, Thomas algorithm, grid study."""
import numpy as np, json
rho, Gam, L, phi0, phiL = 1.0, 0.1, 1.0, 1.0, 0.0
def exact(x, u):
    return phi0 + (phiL - phi0) * (np.exp(rho*u*x/Gam) - 1) / (np.exp(rho*u*L/Gam) - 1)
def coeffs(u, N, scheme):
    dx = L / N; F = rho*u; D = Gam/dx
    if scheme == "CDS": aW, aE = D + F/2, D - F/2
    else: aW, aE = D + F, D
    return aW, aE, aW + aE, dx, F, D
def thomas(a, b, c, d):
    n = len(d); cp = np.zeros(n); dp = np.zeros(n)
    cp[0] = c[0]/b[0]; dp[0] = d[0]/b[0]
    for i in range(1, n):
        m = b[i] - a[i]*cp[i-1]
        cp[i] = c[i]/m if i < n-1 else 0
        dp[i] = (d[i] - a[i]*dp[i-1]) / m
    x = np.zeros(n); x[-1] = dp[-1]
    for i in range(n-2, -1, -1): x[i] = dp[i] - cp[i]*x[i+1]
    return x
def solve(u, N, scheme):
    aW, aE, aP, dx, F, D = coeffs(u, N, scheme)
    n = N - 1
    a = np.full(n, -aW); b = np.full(n, aP); c = np.full(n, -aE); d = np.zeros(n)
    d[0] += aW*phi0; d[-1] += aE*phiL
    phi = thomas(a, b, c, d)
    return np.concatenate([[phi0], phi, [phiL]]), dx
out = {}
for u in (0.1, 2.5):
    PeL = rho*u*L/Gam
    for N in (5,):
        dx = L/N; Pd = rho*u*dx/Gam
        print("u=%.1f Pe_L=%.1f Pe_dx=%.2f" % (u, PeL, Pd))
        x = np.linspace(0, L, N+1); ex = exact(x, u)
        res = {"x": x.tolist(), "exact": ex.tolist(), "PeL": PeL, "Pe_dx": Pd}
        for sch in ("CDS", "UDS"):
            ph, _ = solve(u, N, sch); aW, aE, aP, *_ = coeffs(u, N, sch)
            res[sch] = ph.tolist(); res[sch+"_coef"] = [aW, aE, aP]
            print(sch, np.round(ph, 4), "aW,aE,aP=", np.round([aW, aE, aP], 3), "max err %.4f" % np.max(np.abs(ph-ex)))
        out["u%.1f" % u] = res
# false diffusion
for u in (0.1, 2.5):
    dx = 0.2; fd = rho*u*dx/2
    print("u=%.1f false diffusion = %.3f = %.0f%% of Gamma" % (u, fd, 100*fd/Gam))
    ph_c, _ = solve(u, 5, "CDS")
    # UDS == CDS with Gamma+fd:
    G2 = Gam + fd; D2 = G2/dx; F = rho*u
    aW, aE = D2 + F/2, D2 - F/2; n = 4
    a = np.full(n, -aW); b = np.full(n, aW+aE); c = np.full(n, -aE); d = np.zeros(n); d[0] += aW; 
    chk = thomas(a, b, c, d); ph_u, _ = solve(u, 5, "UDS")
    print("  UDS vs CDS(Gamma+fd) max diff", np.max(np.abs(np.concatenate([[1], chk, [0]]) - ph_u)))
# grid study
Ns = [5, 10, 20, 40, 80, 160, 320]
study = {"N": Ns, "dx": [L/n for n in Ns], "Pe_dx": [rho*2.5*L/n/Gam for n in Ns]}
for sch in ("CDS", "UDS"):
    errs = []
    for N in Ns:
        ph, dx = solve(2.5, N, sch); x = np.linspace(0, L, N+1)
        errs.append(float(np.max(np.abs(ph - exact(x, 2.5)))))
    study[sch] = errs
    print(sch, ["%.2e" % e for e in errs])
    print("  orders:", [round(float(np.log2(errs[i]/errs[i+1])), 2) for i in range(len(errs)-1)])
out["study"] = study
# Gauss-Seidel on case 2
def gs(u, N, scheme, iters=60):
    aW, aE, aP, *_ = coeffs(u, N, scheme)
    p = np.zeros(N+1); p[0] = phi0; hist = [p.copy()]
    for it in range(iters):
        for i in range(1, N):
            p[i] = (aW*p[i-1] + aE*p[i+1]) / aP
        hist.append(p.copy())
    return np.array(hist)
for sch in ("CDS", "UDS"):
    h = gs(2.5, 5, sch, 200)
    ex = exact(np.linspace(0, 1, 6), 2.5); ph, _ = solve(2.5, 5, sch)
    d = [float(np.max(np.abs(h[k]-ph))) for k in (0, 1, 2, 5, 10, 20, 50, 100, 200)]
    print(sch, "GS dist to direct solution at it 0,1,2,5,10,20,50,100,200:", ["%.2e" % v for v in d])
    out["gs_"+sch] = dict(hist=h[:11].tolist(), dist=d)
# spectral radius of GS iteration matrices
for sch in ("CDS", "UDS"):
    aW, aE, aP, *_ = coeffs(2.5, 5, sch); n = 4
    A = np.diag([aP]*n) - np.diag([aW]*(n-1), -1) - np.diag([aE]*(n-1), 1)
    Lo = np.tril(A); U = A - Lo
    G = -np.linalg.solve(Lo, U); print(sch, "GS spectral radius", max(abs(np.linalg.eigvals(G))))
    out["rho_gs_"+sch] = float(max(abs(np.linalg.eigvals(G))))
json.dump(out, open(r"C:\Users\marya\Downloads\convdiff_comsol\p5_numbers.json", "w"), indent=1)
