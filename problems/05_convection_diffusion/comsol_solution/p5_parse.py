import numpy as np, json
OUT = r"C:\Users\marya\Downloads\convdiff_comsol"
rows = [l.split() for l in open(OUT + r"\profiles.txt") if not l.startswith("%") and l.strip()]
x = np.array([float(r[0]) for r in rows]); c = np.array([float(r[1]) for r in rows])
starts = [0] + [i for i in range(1, len(x)) if x[i] < x[i-1]] + [len(x)]
curves = [(x[a:b], c[a:b]) for a, b in zip(starts[:-1], starts[1:])]
print(len(curves), [len(k[0]) for k in curves])
us = [0.1] + [2.5]*7; hms = [0.2, 0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125]
N5 = json.load(open(OUT + r"\p5_numbers.json"))
def exact(x, u): return 1 - (np.exp(u*x/0.1) - 1) / (np.exp(u/0.1) - 1)
res = {}
for k, ((cx, cc), u, h) in enumerate(zip(curves, us, hms)):
    n = int(round(1/h)); xn = np.linspace(0, 1, n+1)
    vals = np.interp(xn, cx, cc)
    err = float(np.max(np.abs(vals - exact(xn, u))))
    res[k] = dict(u=u, hm=h, N=n, nodes=vals.tolist(), maxerr=err)
    print(k, u, h, n, "max err vs exact at nodes %.4e" % err)
cds1 = np.array(N5["u0.1"]["CDS"]); cds2 = np.array(N5["u2.5"]["CDS"]); uds2 = np.array(N5["u2.5"]["UDS"])
print("case1 COMSOL nodes", np.round(res[0]["nodes"], 4), "vs CDS", np.round(cds1, 4))
print("case2 COMSOL nodes", np.round(res[1]["nodes"], 4), "vs CDS", np.round(cds2, 4), "UDS", np.round(uds2, 4))
print("max |COMSOL - CDS| case1 %.2e case2 %.2e" % (np.max(np.abs(np.array(res[0]["nodes"]) - cds1)), np.max(np.abs(np.array(res[1]["nodes"]) - cds2))))
json.dump(res, open(OUT + r"\p5_comsol.json", "w"), indent=1)
