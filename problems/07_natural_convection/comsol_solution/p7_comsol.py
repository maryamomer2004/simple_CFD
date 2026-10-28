"""Problem 7: read the COMSOL exports (centre-line cuts, wall Nusselt numbers),
compute |psi| at the centre, u_max, v_max and Nu, and compare them with the
FDM notebook results (repo problems/07_natural_convection) and de Vahl Davis (1983)."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [(32, 1e3), (32, 1e4), (64, 1e3), (64, 1e4), (128, 1e3), (128, 1e4)]

# de Vahl Davis (1983), Pr = 0.71 (values from the problem statement)
BENCH = {1e3: dict(psi=1.174, umax=3.649, yu=0.813, vmax=3.697, xv=0.178, nu=1.118),
         1e4: dict(psi=5.071, umax=16.178, yu=0.823, vmax=19.617, xv=0.119, nu=2.243)}
# FDM results printed by 03_fdm_solver.ipynb (grid study, N = intervals per side)
FDM = {1e3: {8: (1.3321, 3.418, 0.750, 3.411, 0.125, 1.1365),
             16: (1.2160, 3.649, 0.812, 3.686, 0.188, 1.1209),
             32: (1.1851, 3.649, 0.812, 3.690, 0.188, 1.1181),
             64: (1.1773, 3.649, 0.812, 3.694, 0.172, 1.1178)},
       1e4: {8: (5.8428, 15.080, 0.875, 18.935, 0.125, 2.8088),
             16: (5.2880, 16.209, 0.812, 19.394, 0.125, 2.3794),
             32: (5.1288, 16.165, 0.812, 19.544, 0.125, 2.2681),
             64: (5.0876, 16.180, 0.828, 19.583, 0.125, 2.2487)}}
FDM_RICH = {1e3: dict(psi=1.1747, nu=1.1177), 1e4: dict(psi=5.0738, nu=2.2423)}


def load_cut(path):
    d = np.loadtxt(path, comments='%')
    return d  # x y u v T


def peak(s, f):
    """largest value of f(s) on nodes, refined by a parabola through the 3 nodes around it"""
    i = int(np.argmax(f))
    if 0 < i < len(f) - 1:
        s0, s1, s2 = s[i - 1:i + 2]
        f0, f1, f2 = f[i - 1:i + 2]
        A = np.array([[s0 * s0, s0, 1], [s1 * s1, s1, 1], [s2 * s2, s2, 1]])
        a, b, c = np.linalg.solve(A, [f0, f1, f2])
        if a < 0:
            sp = -b / (2 * a)
            return f[i], s[i], c - b * b / (4 * a), sp
    return f[i], s[i], f[i], s[i]


def nu_table(path):
    d = np.loadtxt(path, comments='%')
    return {(int(r[0]), r[1]): r[2] for r in d}


def main():
    nu_h = nu_table(os.path.join(HERE, 'nu_hot.txt'))
    nu_c = nu_table(os.path.join(HERE, 'nu_cold.txt'))
    out = {}
    for k, (n, ra) in enumerate(RUNS, 1):
        cx = load_cut(os.path.join(HERE, f'cutx_{k}.txt'))
        cy = load_cut(os.path.join(HERE, f'cuty_{k}.txt'))
        cx = cx[np.argsort(cx[:, 1])]
        cy = cy[np.argsort(cy[:, 0])]
        y, u = cx[:, 1], cx[:, 2]
        x, v = cy[:, 0], cy[:, 3]
        half = y <= 0.5 + 1e-12
        psi_mid = np.trapezoid(u[half], y[half])       # psi(0.5,0.5) = int_0^0.5 u dy (exact for P1)
        umax_n, yu_n, umax_p, yu_p = peak(y, u)
        vmax_n, xv_n, vmax_p, xv_p = peak(x, v)
        out[f'{n}_{int(ra)}'] = dict(nel=n, Ra=ra, psi_mid=abs(psi_mid),
                                    umax_node=umax_n, yu_node=yu_n, umax=umax_p, yu=yu_p,
                                    vmax_node=vmax_n, xv_node=xv_n, vmax=vmax_p, xv=xv_p,
                                    nu_hot=nu_h[(n, ra)], nu_cold=nu_c[(n, ra)],
                                    T_centre=float(np.interp(0.5, y, cx[:, 4])))
    # Richardson on COMSOL 64/128 and observed order 32/64/128
    rich = {}
    for ra in (1e3, 1e4):
        r = {}
        for q in ('psi_mid', 'nu_hot', 'umax', 'vmax'):
            f1, f2, f3 = (out[f'{n}_{int(ra)}'][q] for n in (32, 64, 128))
            p = np.log2(abs((f1 - f2) / (f2 - f3))) if f2 != f3 else float('nan')
            r[q] = dict(extrap=f3 + (f3 - f2) / 3, order=p)
        rich[str(int(ra))] = r
    res = dict(comsol=out, comsol_richardson=rich, bench={str(int(k)): v for k, v in BENCH.items()},
               fdm={str(int(k)): {str(n): dict(zip(('psi', 'umax', 'yu', 'vmax', 'xv', 'nu'), t))
                                  for n, t in v.items()} for k, v in FDM.items()},
               fdm_richardson={str(int(k)): v for k, v in FDM_RICH.items()})
    with open(os.path.join(HERE, 'p7_comsol_numbers.json'), 'w') as f:
        json.dump(res, f, indent=1)

    print(f"{'run':>10} {'|psi|':>8} {'umax':>8} {'(y)':>6} {'vmax':>8} {'(x)':>6} {'Nu hot':>8} {'Nu cold':>8}")
    for key, o in out.items():
        print(f"{key:>10} {o['psi_mid']:8.4f} {o['umax']:8.3f} {o['yu']:6.3f} {o['vmax']:8.3f} {o['xv']:6.3f}"
              f" {o['nu_hot']:8.4f} {o['nu_cold']:8.4f}")
    for ra, r in rich.items():
        print(ra, {q: (round(v['extrap'], 4), round(v['order'], 2)) for q, v in r.items()})


if __name__ == '__main__':
    main()
