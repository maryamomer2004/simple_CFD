---
title: Lid-driven cavity flow
subtitle: The steady two-dimensional Navier–Stokes equations in stream function–vorticity form, solved with the Finite Difference Method
problem: 6
kind: Problem statement
---

## The problem

::: given
A **square cavity** of side $L$ is filled with an incompressible viscous fluid. Its **lid** slides to the right at a constant speed $U$; the other three walls are at rest. Find the **steady flow** inside the cavity at Reynolds number $Re = UL/\nu = 100$ with the **Finite Difference Method**, using the **stream function–vorticity** formulation, and compare your results with the benchmark solution of **Ghia, Ghia & Shin (1982)**.
:::

![A square cavity with a lid sliding to the right. The walls are at rest; the fluid inside turns in a large clockwise vortex.](figures/schematic.png)

## Governing equations

Steady, incompressible, two-dimensional flow with velocity $(u, v)$:

$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0, \qquad
u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial x} + \nu\,\nabla^2 u, \qquad
u\frac{\partial v}{\partial x} + v\frac{\partial v}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial y} + \nu\,\nabla^2 v.$$

With the **stream function** $\psi$ ($u = \partial\psi/\partial y$, $v = -\partial\psi/\partial x$) and the **vorticity** $\omega = \partial v/\partial x - \partial u/\partial y$ they become

$$\nabla^2\psi = -\,\omega, \qquad u\,\frac{\partial\omega}{\partial x} + v\,\frac{\partial\omega}{\partial y} = \nu\,\nabla^2\omega.$$

**Boundary conditions.** No slip: $u = U$, $v = 0$ on the lid ($y = L$); $u = v = 0$ on the other three walls. In terms of $\psi$: $\psi = 0$ on all four walls.

## Data

| Quantity | Symbol | Value |
|---|:-:|---|
| side of the square cavity | $L$ | 1 m |
| speed of the lid (to the right) | $U$ | 1 m/s |
| kinematic viscosity | $\nu$ | 0.01 m²/s |
| Reynolds number | $Re = UL/\nu$ | 100 |
| main grid | $N$, $h$ | 32 × 32 intervals, $h = 1/32$ m (33 × 33 nodes) |
| grids for the grid study | $N$ | 4, 8, 16, 32, 64, 128 intervals per side |
| hand calculation (whiteboard) | $N$, $h$ | 4 × 4 intervals, $h = 0.25$ m (9 interior nodes) |

**Benchmark** (Ghia, Ghia & Shin, *J. Comput. Phys.* 48, 1982, 387–411, $Re = 100$): the primary vortex has $\psi_{min} = -0.103423$ m²/s at $(x, y) = (0.6172, 0.7344)$ m. Their tables of $u$ along the vertical centre line $x = 0.5$ and of $v$ along the horizontal centre line $y = 0.5$ are given in the notebook.

::: note
**Data for simulation software** (for example COMSOL Multiphysics, *Laminar Flow*, 2D, stationary study):

- geometry: a square from $(0, 0)$ to $(1, 1)$ m;
- fluid: density $\rho = 1$ kg/m³, dynamic viscosity $\mu = \rho\,\nu = 0.01$ Pa·s (so that $Re = \rho U L/\mu = 100$);
- top boundary: wall, **moving wall** with velocity $(u, v) = (1, 0)$ m/s; other three boundaries: wall, no slip;
- the cavity is closed, so the pressure is fixed only up to a constant: add a **pressure point constraint** $p = 0$ at one corner, e.g. $(0, 0)$;
- mesh: a mapped (structured) mesh of 32 × 32 square elements ($h = 1/32$ m); for a grid study also 8 × 8 to 128 × 128;
- results to compare: $u$ along the line $x = 0.5$, $v$ along the line $y = 0.5$ (with the Ghia et al. tables), and the position of the vortex centre.
:::

## Assumptions

- Steady state.
- Two-dimensional flow (the cavity is very long in the third direction).
- Incompressible Newtonian fluid with constant density and viscosity.
- No gravity or temperature effects.

## Tasks

1. **Physics.** Starting from the continuity and Navier–Stokes equations, show that the stream function satisfies continuity automatically, derive $\nabla^2\psi = -\omega$, and derive the vorticity transport equation (eliminate the pressure). Explain why $\psi = 0$ on all four walls.
2. **Wall vorticity.** Use a Taylor series of $\psi$ from the wall into the fluid to derive **Thom's formula** for the vorticity on the moving lid and on the walls at rest.
3. **Grid.** Cover the cavity with $N \times N$ intervals ($N = 32$). Compute the **cell Reynolds number** $Uh/\nu$ and compare it with the limit 2 of Problem 5.
4. **Discretization.** Write the five-point formula for $\nabla^2\psi = -\omega$ (as in Problem 3) and the central-difference equation for the vorticity (as in Problem 5, now in 2D). Give the velocities from $\psi$.
5. **Solution.** Starting from rest, solve the two coupled equations with one **Gauss–Seidel** iteration: wall vorticity, vorticity sweep, stream-function sweep, repeated until the largest changes are below $10^{-6}$.
6. **Results.** Plot the streamlines and the vorticity. Find the centre and the strength ($\psi_{min}$) of the primary vortex. Do you see the small corner eddies?
7. **Verification.** Repeat on grids from $N = 4$ to $N = 128$. Show the order of convergence of $\psi_{min}$, and compare the centre-line velocities with the Ghia et al. benchmark.
8. *Hand calculation (whiteboard).* With $N = 4$, carry out the first iteration by hand, starting from rest.

## What you will learn

- How the **stream function and vorticity** turn the 2D Navier–Stokes equations into a Poisson equation and a convection–diffusion equation.
- How the **no-slip condition** becomes a boundary condition for the vorticity (**Thom's formula**).
- How to solve two **coupled** equations with one iteration, and how a flow "spins up" from rest.
- How to **verify** a flow solver without an exact solution: a grid study and a published **benchmark**.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell. `04_whiteboard_guide.pdf` guides the first iteration by hand, for the board.
:::
