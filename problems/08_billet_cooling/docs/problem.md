---
title: Cooling a steel billet
subtitle: Two-dimensional unsteady conduction with convection on every surface, solved with explicit and implicit (ADI) finite differences
problem: 8
kind: Problem statement
---

## The problem

::: given
A long **steel billet** with a **square cross-section of 100 mm × 100 mm** leaves a furnace at a uniform **600 °C**. It is then cooled on **all four sides** by a water-mist spray at **30 °C**, with an average convection coefficient **$h = 1000$ W/(m²·K)**. Find the **temperature distribution $T(x, y, t)$** in the cross-section and the **time at which the centre of the billet reaches 100 °C**, with the **Finite Difference Method**: an **explicit** method (FTCS) and an **implicit** method (**ADI**). Verify the results with the exact solution, and check whether the simple **lumped-capacitance** model could have been used instead.
:::

![Cross-section of the billet, cooled on all four sides. By symmetry only one quarter needs to be computed.](figures/schematic.png)

## Data

| Quantity | Symbol | Value |
|---|:-:|---|
| side of the square cross-section | $2L$ | 100 mm ($L = 50$ mm) |
| initial temperature | $T_i$ | 600 °C |
| temperature of the cooling fluid | $T_\infty$ | 30 °C |
| convection coefficient (all four sides) | $h$ | 1000 W/(m²·K) |
| target temperature of the centre | $T_{target}$ | 100 °C |
| thermal conductivity | $k$ | 48.0 W/(m·K) |
| density | $\rho$ | 7854 kg/m³ |
| specific heat | $c_p$ | 559 J/(kg·K) |
| main grid (one quarter) | $N$, $\Delta x$ | 10 × 10 intervals, $\Delta x = \Delta y = 5$ mm (11 × 11 nodes) |
| time steps | $\Delta t$ | FTCS 0.5 s; ADI 10 s (and 5 to 120 s for a study) |
| hand calculation (whiteboard) | $N$, $\Delta x$ | 2 × 2 intervals, $\Delta x = 25$ mm (3 × 3 nodes) |

**Source of the properties.** Plain carbon steel (Mn ≤ 1 %, Si ≤ 0.1 %) at 600 K, Incropera et al., *Fundamentals of Heat and Mass Transfer*, Table A.1 (the density is the 300 K value given there). 600 K ≈ 330 °C lies near the middle of the cooling range; the properties are taken as constant.

This gives $\alpha = k/(\rho c_p) = 1.093 \times 10^{-5}$ m²/s and a Biot number $Bi = hL/k = 1.042$.

::: note
**Data for simulation software** (for example COMSOL Multiphysics 4.3a, *Heat Transfer in Solids*, 2D, time-dependent study):

- geometry: the quarter cross-section, a square from $(0, 0)$ to $(0.05, 0.05)$ m (the centre of the billet at the origin); the whole 0.1 m × 0.1 m square also works, at four times the cost;
- material: a user-defined solid with $k = 48$ W/(m·K), $\rho = 7854$ kg/m³, $c_p = 559$ J/(kg·K) (the values above; library "steel" has different values and gives a different answer);
- initial value: $T = 600$ °C (873.15 K) everywhere;
- boundaries $x = 0.05$ m and $y = 0.05$ m: **heat flux, convective**, $h = 1000$ W/(m²·K), external temperature 30 °C (303.15 K);
- boundaries $x = 0$ and $y = 0$: **symmetry** (no heat flux, the same as thermal insulation in heat transfer);
- mesh: mapped, 10 × 10 square elements (also 5 × 5, 20 × 20 and 40 × 40 for a mesh study);
- time: 0 to 600 s, output every 30 s (and 349 s); the solver chooses its own steps (BDF) unless forced;
- results to compare: the temperature at the centre $(0, 0)$, the middle of a face $(0.05, 0)$ and the corner $(0.05, 0.05)$ against time; the time at which the centre reaches 100 °C (exact: 349.1 s); the temperature along the line $y = 0$ at 30, 120, 300 and 600 s.
:::

## Assumptions

- Two-dimensional conduction: the billet is long and nothing changes along its length.
- Constant properties ($k$, $\rho$, $c_p$) and a constant, uniform convection coefficient on all four sides.
- No heat generation; radiation is included in $h$ or neglected.
- Uniform initial temperature.

## Tasks

1. **Lumped capacitance?** Compute the Biot number $Bi = h L_c/k$ with $L_c = V/A$. Can the billet be treated as having one uniform temperature? What time to reach 100 °C would that model predict?
2. **Symmetry and grid.** Explain why one quarter of the cross-section is enough. Draw the grid with $N = 10$ and mark the node types: interior, symmetry line (ghost nodes), convective surface, corner.
3. **Explicit scheme.** Derive the FTCS equation of every node type from an **energy balance** on its control volume (full, half and quarter cells). Show that every equation is the sum of an $x$ and a $y$ second difference.
4. **Stability.** Find the largest $r = \alpha\,\Delta t/\Delta x^2$ for which every weight in the FTCS equations is positive. Which node sets the limit? Run FTCS just below and just above the limits on $N = 2$ and $N = 10$.
5. **Implicit scheme.** Write the two half steps of the **ADI** (Peaceman–Rachford) method, and show that each one is a set of tridiagonal systems, solved with the **Thomas algorithm** of Problem 1.
6. **Exact solution.** Write the exact solution as the **product of two plane-wall solutions** (eigenvalues from $\zeta\tan\zeta = Bi$). Find the time at which the centre reaches 100 °C.
7. **Results and verification.** Plot temperature maps and $T(t)$ at the centre, the middle of a face and the corner. Compare FTCS and ADI with different time steps (cost and accuracy). Show the order of convergence in $\Delta x$ and in $\Delta t$.
8. *Hand calculation (whiteboard).* With $N = 2$ and $r = 0.14$, carry out two FTCS steps by hand, then one ADI step with $r = 0.7$.

## What you will learn

- When **lumped capacitance** fails, and why a temperature field is then needed.
- How **symmetry** and **energy balances** give every node equation of a 2D unsteady problem.
- Why the **convective corner** limits the time step of the explicit method more than the interior does.
- How the **ADI method** makes an implicit 2D step cheap by reusing the **Thomas algorithm**, and what "unconditionally stable" does and does not promise.
- How a **product solution** gives an exact 2D answer to verify a code, and how to measure the order of a scheme in space and in time.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell. `04_whiteboard_guide.pdf` guides two explicit steps and one ADI step by hand, for the board.
:::
