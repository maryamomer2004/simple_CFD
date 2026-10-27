---
title: Temperatures at four interior points of a square plate
subtitle: Two-dimensional steady heat conduction, solved with the Finite Difference Method
problem: 3
kind: Problem statement
---

## The problem

::: given
In the figure below, **calculate the temperatures at points 1, 2, 3 and 4** using the numerical method (the **Finite Difference Method**). The square is divided into $3 \times 3$ equal squares. Its edges are held at **700 °C** (top), **100 °C** (left), **400 °C** (right) and **500 °C** (bottom).
:::

![The square plate with its four edge temperatures and the four interior points. The grid spacing is the same in both directions, $\Delta x = \Delta y$.](figures/schematic.png)

## Data

| Edge | Temperature |
|---|:-:|
| top | 700 °C |
| left | 100 °C |
| right | 400 °C |
| bottom | 500 °C |

The size of the plate and its thermal conductivity are not given: they are not needed.

## Assumptions

- Steady state: the temperatures no longer change with time.
- Two-dimensional conduction: no temperature change through the thickness of the plate.
- No heat generated inside the plate.
- Constant thermal conductivity $k$.

## Tasks

1. **Physics.** Write the governing equation for steady two-dimensional conduction without heat generation, and its boundary conditions.
2. **Grid.** Number the nodes of the $4 \times 4$ grid with two indices $(i, j)$. Which nodes are known and which are unknown? Are the corner temperatures needed?
3. **Discretization.** Replace the second derivatives by central differences and show that, for $\Delta x = \Delta y$, each interior temperature is the average of its four neighbours. Write the four equations for $T_1$, $T_2$, $T_3$ and $T_4$.
4. **Solution.** Solve the four equations
   a. by **Gaussian elimination** (forward elimination and back substitution);
   b. by **Gauss–Seidel iteration**, recording the temperatures after each iteration.
5. **Post-processing.** Show the result on the plate, and check that the heat entering through the hot edges equals the heat leaving through the cold edges.
6. **Grid study.** Solve the same plate on finer grids. How close is the four-node answer to the exact temperatures?

## What you will learn

- How the two-dimensional Laplace equation becomes the **five-point formula**: each node is the average of its neighbours.
- How to number a 2D grid and **assemble** a linear system $A\,\mathbf{T} = \mathbf{b}$.
- How **Gaussian elimination** and **Gauss–Seidel** iteration solve the same system in different ways.
- Why the finite difference solution **conserves energy** exactly.
- How refining the grid shows the accuracy of a coarse solution.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell.
:::
