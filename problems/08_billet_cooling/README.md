<p align="center">
  <img src="docs/figures/schematic.png" alt="The square cross-section of a steel billet, cooled by a fluid on all four sides; the two symmetry lines through the centre cut out the quarter that is modelled" width="65%">
</p>

# Problem 8 · Cooling a steel billet

**2D · unsteady · heat conduction with convection on every surface · lumped capacitance check · explicit FTCS and its stability limit · implicit ADI with the Thomas algorithm · exact product solution**

> A 100 mm × 100 mm steel billet leaves a furnace at 600 °C and is cooled by a water-mist spray (30 °C, $`h = 1000`$ W/(m²·K)) on all four sides. Find the temperature field $`T(x, y, t)`$ and the time at which the centre reaches 100 °C with the Finite Difference Method, explicit (FTCS) and implicit (ADI), and verify both with the exact solution.

## 📦 What's in this folder

| File | What's inside |
|---|---|
| 📄 [`01_problem_statement.pdf`](01_problem_statement.pdf) | the problem, data (with the source of the steel properties), equations, a box with everything a simulation package needs, and the tasks |
| 📘 [`02_solution.pdf`](02_solution.pdf) | the step-by-step solution: the Biot-number check, symmetry, energy-balance node equations, the stability limit set by the cooled corner, ADI, the exact product solution, cost against accuracy, convergence in $`\Delta x`$ and $`\Delta t`$ |
| 💻 [`03_fdm_solver.ipynb`](03_fdm_solver.ipynb) | the complete solver in **plain Python**, explained cell by cell, with plots |
| 🧮 [`04_whiteboard_guide.pdf`](04_whiteboard_guide.pdf) | **for instructors:** the quarter billet on a 3 × 3 grid by hand: two explicit steps and one ADI step with the Thomas algorithm, with every intermediate number |
| 🎨 [`plots.py`](plots.py) | drawing helpers used by the notebook (matplotlib only, no numerics) |
| 🛠️ [`docs/`](docs) | Markdown sources of the PDFs and their figures |

## 🎯 What you will learn

- How to check with the **Biot number** whether one temperature (lumped capacitance) is enough, and what goes wrong when it is not.
- How **symmetry** reduces the billet to one quarter, with **ghost nodes** on the symmetry lines (Problem 1) and **energy balances** on the cooled surfaces (Problem 4), now with a storage term.
- Why the explicit time step is limited by the **cooled corner**, $`r \le 1/[4(1 + Bi_{cell})]`$, and what happens just above the limit.
- How the **ADI method** makes an implicit 2D step cheap: two sets of tridiagonal systems per step, solved with the **Thomas algorithm** of Problem 1. And why "unconditionally stable" does not mean "accurate for any time step".
- How the **product of two plane-wall solutions** gives an exact 2D answer, and how to measure the order of a scheme in space and in time.

## 📊 Result

<p align="center">
  <img src="docs/figures/history.png" alt="Temperature against time at the centre, the middle of a face and the corner of the billet: finite difference points on the exact curves; the lumped-capacitance curve lies between the surface and the centre and reaches 100 °C much too early" width="80%">
</p>

| time for the centre to reach 100 °C | |
|---|:-:|
| exact (product of two plane walls) | 349.1 s |
| FTCS, 11 × 11 nodes, $`\Delta t = 0.5`$ s (1200 steps) | 348.6 s |
| ADI, 11 × 11 nodes, $`\Delta t = 10`$ s (60 steps) | 349.2 s |
| lumped capacitance ($`Bi = hL_c/k = 0.52`$, too large) | 230.2 s |

Lumped capacitance would send the billet on a third too early. FTCS must keep $`\Delta t \le 0.518`$ s because of the cooled corner; ADI is stable for any time step and, being second order in time, is more accurate with $`\Delta t = 5`$ s than FTCS with $`\Delta t = 0.5`$ s.

## ▶️ Run it

```bash
pip install -r ../../requirements.txt
jupyter lab 03_fdm_solver.ipynb
```

The whole notebook runs in about 15 seconds; most of it is the finest grid of the convergence study (41 × 41 nodes with FTCS).

---

<p align="center"><a href="../../README.md#-course-problems">⬅ Back to the course home page</a></p>
