<p align="center">
  <img src="docs/figures/schematic.png" alt="A closed loop of pipe in which water carries a pulse of dye at speed c, and the same loop unrolled into a periodic domain from x = 0 to x = L" width="85%">
</p>

# Problem 9 · Advection of a pulse

**1D · unsteady · pure advection (hyperbolic) · periodic domain · Courant number and CFL condition · von Neumann analysis · numerical diffusion vs dispersion**

> Water carries a pulse of dye round a closed loop of pipe ($`L = 1`$ m, plug flow $`c = 1`$ m/s) without letting it diffuse, so after one lap ($`t = 1`$ s) the pulse should be back unchanged. Solve $`\partial u/\partial t + c\,\partial u/\partial x = 0`$ on the periodic domain with the Finite Difference Method, for a smooth Gaussian pulse and a sharp square pulse, using FTCS, first-order upwind and Lax–Wendroff at Courant numbers 0.5, 1.0 and 1.1, and compare with the exact solution.

## 📦 What's in this folder

| File | What's inside |
|---|---|
| 📄 [`01_problem_statement.pdf`](01_problem_statement.pdf) | the problem, equation, exact solution, data, a box with everything a simulation package needs, and the tasks |
| 📘 [`02_solution.pdf`](02_solution.pdf) | the step-by-step solution: characteristics, Courant number, three schemes, CFL condition, von Neumann analysis, one lap at three Courant numbers, modified equation, conservation, error study |
| 💻 [`03_fdm_solver.ipynb`](03_fdm_solver.ipynb) | the complete solver in **plain Python**, explained cell by cell, with plots |
| 🧮 [`04_whiteboard_guide.pdf`](04_whiteboard_guide.pdf) | **for instructors:** two time steps of upwind, Lax–Wendroff and FTCS by hand on 8 nodes, and the von Neumann analysis on the board, with every intermediate number |
| 🎨 [`plots.py`](plots.py) | drawing helpers used by the notebook (matplotlib only, no numerics) |
| 🛠️ [`docs/`](docs) | Markdown sources of the PDFs and their figures |

## 🎯 What you will learn

- What a **hyperbolic** equation is: $`u`$ is carried unchanged along the **characteristics** $`x - ct = \text{const}`$, at a finite speed and in one direction.
- What the **Courant number** $`C = c\,\Delta t/\Delta x`$ means, and why explicit schemes need the **CFL condition** $`C \le 1`$.
- How a **von Neumann analysis** decides stability, and why **FTCS** blows up at every time step.
- Why **upwind** smears a pulse: its **modified equation** contains a **numerical diffusion** $`D_{num} = \tfrac12 c\,\Delta x\,(1 - C)`$, the false diffusion of Problem 5, which predicts the peak loss to within 0.0005.
- Why **Lax–Wendroff** is 2nd order but leaves wiggles behind sharp fronts (**numerical dispersion**), and why both schemes are exact at $`C = 1`$ and unstable above it.

## 📊 Result

<p align="center">
  <img src="docs/figures/lap.png" alt="After one lap on 100 intervals at Courant number 0.5: upwind returns both pulses smooth and positive but smeared to 58 percent and 86 percent of their height; Lax-Wendroff keeps the Gaussian almost unchanged but leaves wiggles behind the edges of the square pulse" width="85%">
</p>

Peak after one lap on 100 intervals (exact: 1):

| | Gaussian, $`C = 0.5`$ | square, $`C = 0.5`$ | both pulses, $`C = 1.0`$ | $`C = 1.1`$ |
|---|:-:|:-:|:-:|:-:|
| FTCS | blows up (70) | blows up ($`4 \times 10^8`$) | unstable ($`\lvert G\rvert > 1`$) | unstable |
| upwind | **0.577** (modified equation: 0.577) | 0.863 | **1.000** (exact) | unstable (square: $`1.2 \times 10^6`$) |
| Lax–Wendroff | **0.964** | 1.223 (wiggles down to −0.22) | **1.000** (exact) | unstable (square: $`3 \times 10^{12}`$) |

Refining the grid at $`C = 0.5`$ (Gaussian, 25 to 1600 intervals), Lax–Wendroff converges at **2nd order**, upwind at only **1st order**: on 1600 intervals upwind keeps 94 % of the peak, less than Lax–Wendroff on 100 intervals.

## ▶️ Run it

```bash
pip install -r ../../requirements.txt
jupyter lab 03_fdm_solver.ipynb
```

The whole notebook, including the error study up to 1600 intervals, runs in about 10 seconds in plain Python.

---

<p align="center"><a href="../../README.md#-course-problems">⬅ Back to the course home page</a></p>
