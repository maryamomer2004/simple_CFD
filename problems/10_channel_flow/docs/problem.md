---
title: Developing laminar flow in a channel
subtitle: Navier–Stokes in primitive variables, the projection method on a staggered grid, solved with the Finite Difference Method
problem: 10
kind: Problem statement
---

## The problem

::: given
A fluid enters the gap between two long **parallel plates** a distance $H$ apart with a **uniform velocity** $U$. It leaves the channel at $x = L$, where the pressure is $p = 0$. The fluid sticks to both plates (no slip). Friction slows the fluid near the walls, so the fluid in the middle speeds up, until far downstream the velocity profile stops changing (**fully developed** flow). Find the **developing velocity field**, the **entrance length** and the **pressure drop** at **Reynolds numbers 50 and 100**, by solving the Navier–Stokes equations for $u$, $v$ and $p$ with the **projection method** on a **staggered grid**. Check the result against the exact fully developed solution and the entrance-length correlation of **Durst et al. (2005)**.
:::

![The channel: uniform inlet, boundary layers growing on both plates, the parabolic fully developed profile, and the outlet at p = 0.](figures/schematic.png)

## Governing equations

Incompressible, laminar, Newtonian flow. In dimensionless form, with lengths in units of $H$, velocities in units of $U$, time in units of $H/U$ and pressure in units of $\rho U^2$:

$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0,$$

$$\frac{\partial u}{\partial t} + u\,\frac{\partial u}{\partial x} + v\,\frac{\partial u}{\partial y} = -\frac{\partial p}{\partial x} + \frac{1}{Re}\,\nabla^2 u, \qquad
\frac{\partial v}{\partial t} + u\,\frac{\partial v}{\partial x} + v\,\frac{\partial v}{\partial y} = -\frac{\partial p}{\partial y} + \frac{1}{Re}\,\nabla^2 v,$$

with the Reynolds number $Re = \rho U H/\mu$. We march in time from plug flow until the flow is steady.

**Boundary conditions.**

| Boundary | Velocity | Pressure |
|---|---|---|
| inlet, $x = 0$ | $u = 1$, $v = 0$ | free ($\partial p/\partial x = 0$ in the pressure equation) |
| walls, $y = 0$ and $y = 1$ | $u = v = 0$ (no slip) | free ($\partial p/\partial y = 0$) |
| outlet, $x = L$ | free ($\partial u/\partial x = \partial v/\partial x = 0$) | $p = 0$ |

**Exact fully developed solution** (plane Poiseuille flow): far downstream $v = 0$ and

$$u = 6\,U\,\frac{y}{H}\left(1 - \frac{y}{H}\right), \qquad u_{max} = 1.5\,U, \qquad \frac{dp}{dx} = -\frac{12\,\mu\,U}{H^2}\quad\left(= -\frac{12}{Re}\ \text{dimensionless}\right).$$

**Entrance length** $L_e$: the distance from the inlet at which the centre-line velocity reaches 99 % of its fully developed value. Correlation of Durst, Ray, Ünsal and Bayoumi (*J. Fluids Eng.* 127, 2005, 1154–1160) for a plane channel with a uniform inlet, $Re$ based on $H$ and the mean velocity:

$$\frac{L_e}{H} = \left[\,0.631^{\,1.6} + (0.0442\,Re)^{1.6}\,\right]^{1/1.6} \qquad (L_e = 2.39\,H \text{ at } Re = 50, \; 4.54\,H \text{ at } Re = 100).$$

## Data

| Quantity | Symbol | Value |
|---|:-:|---|
| Reynolds number | $Re = \rho U H/\mu$ | 50 and 100 |
| channel length | $L$ | $10\,H$ |
| inlet velocity (uniform) | $U$ | 1 (dimensionless) |
| main grid | $h$ | $H/16$: 160 × 16 square cells |
| grids for the grid study ($Re = 50$, $L = 5\,H$) | $h$ | $H/8$, $H/16$, $H/32$ |
| time step | $\Delta t$ | $0.8 \times$ the FTCS stability limit |
| steady state | | largest $\lvert\partial u/\partial t\rvert < 10^{-5}$ |
| pressure equation | | SOR, $\omega = 1.7$, with a block correction; $\lvert\nabla\cdot\mathbf u\rvert < 10^{-6}$ in every cell |
| hand calculation (whiteboard) | | 2 × 3 cells, $h = 1/3$, $Re = 50$, $\Delta t = 0.01$, one time step |

A real example: water ($\rho = 998$ kg/m³, $\mu = 1.0 \times 10^{-3}$ Pa·s) in a 1 mm gap, as in a compact plate heat exchanger or a microfluidic chip, at a mean velocity of 5 cm/s ($Re = 50$) or 10 cm/s ($Re = 100$).

::: note
**Data for simulation software** (written for COMSOL Multiphysics 4.3a, *Laminar Flow* interface, 2D, *Stationary* study; the same data work in any CFD package):

- geometry: a rectangle from $(0, 0)$ to $(L, H) = (10, 1)$ m. In these units every number is dimensionless;
- fluid properties: density $\rho = 1$ kg/m³ and dynamic viscosity $\mu = 1/Re$ Pa·s (0.02 for $Re = 50$, 0.01 for $Re = 100$). Define a parameter `Re` and type `1/Re` as the viscosity, then a **parametric sweep** over `Re = 50, 100` solves both cases;
- inlet (left side): *Inlet*, boundary condition *Velocity*, normal inflow velocity $U_0 = 1$ m/s (uniform);
- outlet (right side): *Outlet*, boundary condition *Pressure, no viscous stress*, $p_0 = 0$, with *Suppress backflow* on;
- walls (top and bottom): *Wall*, *No slip* (the default);
- no pressure point constraint is needed: the outlet fixes the pressure level (unlike the closed cavities of Problems 6 and 7);
- mesh: *Mapped*, 160 × 16 square elements (the spacing of the main grid); for a grid study, refine it, or make the elements smaller towards the walls with a geometric *Distribution* (element ratio);
- results to compare: $u$ on the centre line $y = 0.5$ (entrance length: where it reaches 99 % of its value at the outlet), profiles $u(y)$ at $x = 0.5, 1, 2, 4, 10$, the flow rate $\int_0^1 u\,dy$ at several $x$, the pressure on the centre line at $x = 0$, and $dp/dx$ near the outlet.
:::

## Assumptions

- Two-dimensional (the plates are much wider than the gap), laminar, incompressible flow.
- Newtonian fluid with constant density and viscosity; gravity plays no role.
- Uniform inlet velocity; the outlet is far enough downstream for the flow there to be fully developed.

## Tasks

1. **Physics.** Write the Navier–Stokes equations in primitive variables in dimensionless form. Derive the exact fully developed solution and its pressure gradient. Why is the stream function–vorticity method of Problems 6 and 7 less convenient here?
2. **Boundary conditions.** Explain why the velocity is prescribed at the inlet and the walls but the pressure at the outlet, and what this means for the pressure equation (Neumann or Dirichlet) at each boundary.
3. **Grid.** Explain why storing $u$, $v$ and $p$ at the same nodes allows a **checkerboard pressure**, and how the **staggered (MAC) grid** prevents it.
4. **Discretization.** On a staggered grid with $h = H/16$, write the predictor for $u$ and $v$ (FTCS, central differences), the **pressure Poisson equation** of each cell (including the inlet, wall and outlet cells), and the velocity correction. Find the stable time step.
5. **Solution.** Starting from plug flow, march with the **projection method** until the flow is steady. Solve the pressure equation with SOR; explain why a long channel needs a block correction.
6. **Results.** Plot the velocity field and profiles. Find the **entrance length** and compare it with Durst et al. Check **mass conservation** (the flow rate at several $x$). Find the **pressure drop**: the fully developed gradient and the extra drop of the entrance region.
7. **Verification.** Repeat for $Re = 50$ with $h = H/8$, $H/16$, $H/32$; find the observed order of accuracy and use Richardson extrapolation.
8. *Hand calculation (whiteboard).* On 2 × 3 cells ($h = 1/3$, $Re = 50$, $\Delta t = 0.01$), carry out one projection step from plug flow by hand: predictor, pressure equation, correction, and the divergence check.

## What you will learn

- How to solve the Navier–Stokes equations for the **primitive variables** $u$, $v$, $p$, and what the pressure does in an incompressible flow.
- The **projection method**: predictor, **pressure Poisson equation**, correction.
- Why a **staggered grid** avoids the checkerboard pressure of a collocated grid.
- How to set **inlet and outlet boundary conditions**, and which variable to prescribe where.
- What the **entrance length** and the **extra pressure drop** of a developing flow are.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell. `04_whiteboard_guide.pdf` guides one projection step by hand, for the board.
:::
