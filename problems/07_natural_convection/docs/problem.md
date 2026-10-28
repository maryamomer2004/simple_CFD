---
title: Natural convection in a heated square cavity
subtitle: Buoyancy-driven flow and heat transfer, stream function–vorticity–temperature, solved with the Finite Difference Method
problem: 7
kind: Problem statement
---

## The problem

::: given
A **square cavity** of side $L$ is filled with **air**. The **left wall is hot** ($T_h$), the **right wall is cold** ($T_c$), and the **top and bottom walls are insulated**. Gravity points down. Buoyancy sets the air in motion: it rises along the hot wall and sinks along the cold wall. Find the **steady flow, the temperature field and the heat transferred** across the cavity (the average **Nusselt number**) with the **Finite Difference Method**, for **Rayleigh numbers $10^3$ and $10^4$**, and compare with the benchmark solution of **de Vahl Davis (1983)**.
:::

![The cavity: hot left wall, cold right wall, insulated top and bottom; warm air rises, cool air sinks, and a clockwise circulation forms.](figures/schematic.png)

## Governing equations

Boussinesq approximation (the density varies with temperature only in the buoyancy force). In dimensionless form, with lengths in units of $L$, velocities in units of $\alpha/L$ and $T = (T_{dim} - T_c)/(T_h - T_c)$:

$$\nabla^2\psi = -\,\omega, \qquad
u\,\frac{\partial\omega}{\partial x} + v\,\frac{\partial\omega}{\partial y} = Pr\,\nabla^2\omega + Ra\,Pr\,\frac{\partial T}{\partial x}, \qquad
u\,\frac{\partial T}{\partial x} + v\,\frac{\partial T}{\partial y} = \nabla^2 T,$$

with $u = \partial\psi/\partial y$, $v = -\partial\psi/\partial x$, $\omega = \partial v/\partial x - \partial u/\partial y$, and

$$Ra = \frac{g\,\beta\,(T_h - T_c)\,L^3}{\nu\,\alpha}, \qquad Pr = \frac{\nu}{\alpha}.$$

**Boundary conditions.** All four walls: no slip ($u = v = 0$, so $\psi = 0$). Left wall $T = 1$; right wall $T = 0$; top and bottom $\partial T/\partial y = 0$.

**Heat transfer.** Local Nusselt number on the hot wall $Nu(y) = -\,\partial T/\partial x\,|_{x=0}$; average $\overline{Nu} = \int_0^1 Nu\,dy$ (equal to 1 for pure conduction).

## Data

| Quantity | Symbol | Value |
|---|:-:|---|
| Rayleigh number | $Ra$ | $10^3$ and $10^4$ |
| Prandtl number (air) | $Pr$ | 0.71 |
| dimensionless wall temperatures | $T$ | 1 (left, hot), 0 (right, cold) |
| main grid | $N$, $h$ | 32 × 32 intervals, $h = 1/32$ (33 × 33 nodes) |
| grids for the grid study | $N$ | 8, 16, 32, 64 intervals per side |
| hand calculation (whiteboard) | $N$, $h$ | 4 × 4 intervals, $h = 0.25$, $Ra = 10^3$ |

A real example: the air gap of a double-glazed window with 10 K between the panes has $Ra \approx 10^3$ for a 1 cm gap and $Ra \approx 10^4$ for a 2.2 cm gap.

**Benchmark** (de Vahl Davis, *Int. J. Numer. Methods Fluids* 3, 1983, 249–264, $Pr = 0.71$):

| | $\lvert\psi\rvert$ at the centre | largest $u$ on $x = 0.5$ (at $y$) | largest $v$ on $y = 0.5$ (at $x$) | $\overline{Nu}$ |
|---|:-:|:-:|:-:|:-:|
| $Ra = 10^3$ | 1.174 | 3.649 (0.813) | 3.697 (0.178) | 1.118 |
| $Ra = 10^4$ | 5.071 | 16.178 (0.823) | 19.617 (0.119) | 2.243 |

::: note
**Data for simulation software** (for example COMSOL Multiphysics, *Laminar Flow* + *Heat Transfer in Fluids*, 2D, stationary study):

- geometry: a square from $(0, 0)$ to $(L, L)$; any $L$ works if the properties give the right $Ra$. A convenient dimensionless choice: $L = 1$ m, $\rho = 1$ kg/m³, $c_p = 1$ J/(kg·K), thermal conductivity $k = 1$ W/(m·K) (so $\alpha = 1$ m²/s), dynamic viscosity $\mu = Pr = 0.71$ Pa·s, $T_h = 1$ K, $T_c = 0$ K;
- buoyancy: a volume force in the $y$ direction $F_y = Ra\,Pr\,\rho\,(T - T_0)$ with $T_0 = 0.5$ K (this is $\rho\,g\,\beta\,(T - T_0)$ in the units above), with $\rho$ constant elsewhere (Boussinesq);
- walls: no slip everywhere; temperature $T_h$ on the left, $T_c$ on the right, thermal insulation on top and bottom;
- the cavity is closed: add a **pressure point constraint** $p = 0$ at one corner;
- mesh: mapped, 32 × 32 square elements (also 64 × 64 and finer for a grid study);
- results to compare: average Nusselt number on the hot wall ($-\partial T/\partial x$ integrated over the wall), the largest $u$ on $x = 0.5$ and $v$ on $y = 0.5$.
:::

## Assumptions

- Steady, two-dimensional, laminar flow.
- Newtonian fluid with constant properties, except for the density in the buoyancy force (Boussinesq approximation).
- No heat generation, no radiation, no viscous heating.

## Tasks

1. **Physics.** Starting from Problem 6, explain where the buoyancy term $Ra\,Pr\,\partial T/\partial x$ in the vorticity equation comes from, and why the energy equation is a convection–diffusion equation. Compute $Ra$ for the window gap example.
2. **Boundary conditions.** Write Thom's formula for the four walls at rest, and use a **ghost node** to derive the temperature equation on the insulated walls.
3. **Discretization.** On an $N \times N$ grid ($N = 32$), write the five-point formula for $\psi$ and the central-difference equations for $\omega$ (with the buoyancy source) and for $T$.
4. **Solution.** Starting from pure conduction ($T = 1 - x$, $\psi = \omega = 0$), solve the three coupled equations with one **Gauss–Seidel** iteration until all changes are below $10^{-6}$.
5. **Results.** Plot the streamlines and the isotherms for both $Ra$. Compute the local and average **Nusselt numbers** on the hot and the cold wall, and check the energy balance.
6. **Verification.** Repeat on grids $N = 8$ to $64$. Use **Richardson extrapolation** to estimate the grid-independent values of $\lvert\psi\rvert$ at the centre and $\overline{Nu}$, and compare with de Vahl Davis.
7. *Hand calculation (whiteboard).* With $N = 4$ and $Ra = 10^3$, carry out the first iteration by hand, starting from pure conduction.

## What you will learn

- How **buoyancy** couples the temperature to the flow (the Boussinesq approximation), and how the flow carries the heat.
- How to solve **three coupled equations** in one iteration, and how a flow is born from a sideways temperature difference.
- How to apply an **insulated wall** with a ghost node on a 2D grid.
- What the **Rayleigh, Prandtl and Nusselt numbers** mean.
- How **Richardson extrapolation** turns two grids into an estimate of the exact answer.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell. `04_whiteboard_guide.pdf` guides the first iterations by hand, for the board.
:::
