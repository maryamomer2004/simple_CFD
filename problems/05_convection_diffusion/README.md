<p align="center">
  <img src="docs/figures/schematic.png" alt="A fluid flows with velocity u through a channel from a reservoir at phi = 1 to a reservoir at phi = 0; convection carries phi downstream while diffusion spreads it in both directions" width="85%">
</p>

# Problem 5 · Steady convection and diffusion in one dimension

**1D · steady · convection + diffusion · Péclet number · central vs upwind differences · false diffusion**

> A property $`\phi`$ is transported by convection and diffusion through a one-dimensional domain $`0 \le x \le L`$ between two reservoirs, with $`\phi = 1`$ at $`x = 0`$ and $`\phi = 0`$ at $`x = L`$. Find the steady distribution of $`\phi`$ with the Finite Difference Method, using central and upwind differences for the convection term, for $`u = 0.1`$ m/s and $`u = 2.5`$ m/s ($`L = 1`$ m, $`\rho = 1`$ kg/m³, $`\Gamma = 0.1`$ kg/(m·s)).
> *(Adapted from Versteeg & Malalasekera, An Introduction to Computational Fluid Dynamics, chapter 5.)*

## 📦 What's in this folder

| File | What's inside |
|---|---|
| 📄 [`01_problem_statement.pdf`](01_problem_statement.pdf) | the problem, data (including a box with everything a simulation package needs), assumptions and tasks |
| 📘 [`02_solution.pdf`](02_solution.pdf) | the step-by-step solution: Péclet numbers, CDS and UDS coefficients, Thomas algorithm, wiggles, false diffusion, grid refinement, Gauss–Seidel |
| 💻 [`03_fdm_solver.ipynb`](03_fdm_solver.ipynb) | the complete solver in **plain Python**, explained cell by cell, with plots |
| 🧮 [`04_whiteboard_guide.pdf`](04_whiteboard_guide.pdf) | **for instructors:** the problem solved by hand on the board, with 5 intervals and a pocket calculator, for the slow flow (CDS) and the fast flow (CDS and UDS), board by board with every intermediate number |
| 🎨 [`plots.py`](plots.py) | drawing helpers used by the notebook (matplotlib only, no numerics) |
| 🛠️ [`docs/`](docs) | Markdown sources of the PDFs and their figures |

## 🎯 What you will learn

- What the **convection term** $`d(\rho u\phi)/dx`$ does, and why it is what makes CFD *fluid* dynamics.
- What the **Péclet number** measures, and why the **cell Péclet number** $`Pe_\Delta = \rho u\,\Delta x/\Gamma`$ decides how a scheme behaves.
- Why **central differences** give non-physical **wiggles** when $`Pe_\Delta > 2$ (a negative neighbour coefficient, loss of diagonal dominance), and why Gauss–Seidel can then diverge.
- Why **upwind differences** are always bounded, and what they cost: **false diffusion** $`\rho u\,\Delta x/2`$ and only 1st-order accuracy.
- Why commercial CFD codes use upwind-biased or stabilised schemes.

## 📊 Result

<p align="center">
  <img src="docs/figures/case2.png" alt="Fast flow on 5 intervals: the central-difference values zig-zag and climb to 1.41, above the physical maximum of 1, while the upwind values stay between 0 and 1 but drop too early" width="85%">
</p>

Node values on 5 intervals ($`\Delta x = 0.2`$ m):

| | $`u`$ = 0.1 m/s ($`Pe_\Delta`$ = 0.2) | | | $`u`$ = 2.5 m/s ($`Pe_\Delta`$ = 5) | | |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **$`x`$ [m]** | **CDS** | **UDS** | **exact** | **CDS** | **UDS** | **exact** |
| 0.2 | 0.8714 | 0.8656 | 0.8711 | 0.9525 | 0.9994 | 1.0000 |
| 0.4 | 0.7141 | 0.7044 | 0.7138 | 1.0633 | 0.9955 | 1.0000 |
| 0.6 | 0.5220 | 0.5109 | 0.5215 | 0.8047 | 0.9723 | 1.0000 |
| 0.8 | 0.2871 | 0.2786 | 0.2868 | **1.4082** | 0.8334 | 0.9933 |

For the slow flow both schemes work. For the fast flow central differences produce values above 1, which are impossible, and upwind is bounded but smeared. Refining the grid for $`u = 2.5`$ m/s (up to 320 intervals), CDS converges at **2nd order** once $`Pe_\Delta < 2`$, UDS at only **1st order**.

## ▶️ Run it

```bash
pip install -r ../../requirements.txt
jupyter lab 03_fdm_solver.ipynb
```

---

<p align="center"><a href="../../README.md#-course-problems">⬅ Back to the course home page</a></p>
