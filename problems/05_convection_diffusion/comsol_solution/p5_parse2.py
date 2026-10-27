import numpy as np, json
OUT = r"C:\Users\marya\Downloads\convdiff_comsol"
rows = [l.split() for l in open(OUT + r"\profiles_stab.txt") if not l.startswith("%") and l.strip()]
x = np.array([float(r[0]) for r in rows]); c = np.array([float(r[1]) for r in rows])
starts = [0] + [i for i in range(1, len(x)) if x[i] < x[i-1]] + [len(x)]
curves = [(x[a:b], c[a:b]) for a, b in zip(starts[:-1], starts[1:])]
us = [0.1] + [2.5]*7; hms = [0.2, 0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125]
def exact(x, u): return 1 - (np.exp(u*x/0.1) - 1) / (np.exp(u/0.1) - 1)
N5 = json.load(open(OUT + r"\p5_numbers.json"))
res = {}
for k, ((cx, cc), u, h) in enumerate(zip(curves, us, hms)):
    n = int(round(1/h)); xn = np.linspace(0, 1, n+1); v = np.interp(xn, cx, cc)
    res[k] = dict(u=u, hm=h, N=n, nodes=v.tolist(), maxerr=float(np.max(np.abs(v-exact(xn, u)))), vmax=float(v.max()), vmin=float(v.min()))
    print(k, u, h, "max err %.4e  range [%.4f, %.4f]" % (res[k]["maxerr"], v.min(), v.max()))
print("case2 stabilised nodes", np.round(res[1]["nodes"], 4))
print("UDS                   ", np.round(N5["u2.5"]["UDS"], 4))
print("exact                 ", np.round(N5["u2.5"]["exact"], 4))
json.dump(res, open(OUT + r"\p5_comsol_stab.json", "w"), indent=1)
