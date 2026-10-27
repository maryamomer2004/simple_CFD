# Problem 1 · COMSOL Multiphysics solution

The same aluminium pin fin, solved with the **finite element method** in **COMSOL Multiphysics 4.3a** (Heat Transfer in Solids, 1D, stationary). It is a cross-check of the finite difference solution, and an introduction to commercial CFD software.

| File | What's inside |
|---|---|
| 📘 [`COMSOL_PinFin_Guide.pdf`](COMSOL_PinFin_Guide.pdf) | step-by-step guide for students: building the 1D fin model in COMSOL 4.3a, from geometry to results, with screenshots |
| 🧩 [`fin1d_pin_fin.mph`](fin1d_pin_fin.mph) | the finished COMSOL model, ready to open in COMSOL 4.3a or newer |

The model uses the same data as the finite difference notebook: $`L = 10`$ cm, $`d = 5`$ mm, $`k = 237`$ W/(m·K), $`h = 25`$ W/(m²·K), $`T_b = 100`$ °C, $`T_\infty = 30`$ °C, insulated tip.

| Quantity | COMSOL (FEM, 100 elements) | Notebook (FDM, 10 intervals) | Exact |
|---|:-:|:-:|:-:|
| tip temperature | 78.194 °C | 78.205 °C | 78.194 °C |
| heat removed by the fin | 2.1702 W | 2.1721 W | 2.1702 W |

---

<p align="center"><a href="../README.md">⬅ Back to Problem 1</a></p>
