---
title: Phosphorus diffusion into silicon
subtitle: One-dimensional unsteady diffusion in a semi-infinite medium, solved with the Finite Difference Method
problem: 2
kind: Problem statement
---

## The problem

::: given
In a typical process, phosphorus oxychloride (POCl₃), which has a normal boiling point of 105 °C, is vaporised. The POCl₃ vapour is fed into a **chemical vapour deposition (CVD) reactor** at elevated temperature and reduced pressure (e.g. 0.10 atm), where it decomposes on the silicon surface according to the reaction

$$\mathrm{Si(s)} + 2\,\mathrm{POCl_3(g)} \;\longrightarrow\; \mathrm{SiO_2(s)} + 3\,\mathrm{Cl_2(g)} + 2\,\mathrm{P(s)}.$$

A SiO₂ coating rich in molecular phosphorus forms over the crystalline-silicon surface. The phosphorus then **diffuses into the crystalline silicon** to form a Si–P thin film. The coating is the **source** for mass transfer of phosphorus, and the silicon wafer is the **sink**.

Consider a simplified case where the silicon wafer initially contains no P, and after the start of the reaction the P concentration at the interface is constant. Because the diffusion coefficient of P in crystalline silicon is very low and only a thin film is desired, the phosphorus atoms do not penetrate very far into the silicon. They cannot "see" through the entire thickness of the wafer, so the silicon acts as a **semi-infinite sink**.

Consider the phosphorus doping of crystalline silicon at **1100 °C**. The surface concentration of phosphorus is $c_{As} = 2.5\times10^{20}$ atoms P/cm³ of solid Si, which is relatively dilute. The diffusivity of P in Si is $D_{AB} = 6.5\times10^{-13}$ cm²/s. The phosphorus-rich coating is an infinite source, so $c_{As}$ stays constant.

**Predict the depth of the Si–P thin film after 1 h, if the target concentration is 1 % of the surface value ($2.5\times10^{18}$ atoms P/cm³), and the concentration profile of P atoms after 1 h.**
:::

![The P-rich SiO₂ coating keeps the surface concentration at $c_{As}$; phosphorus diffuses down into the silicon wafer, which starts free of P. The depth $z$ is measured from the surface.](figures/schematic.png)

## Data

| Quantity | Symbol | Value |
|---|:-:|---|
| process temperature | $T$ | 1100 °C |
| surface concentration of P (constant) | $c_{As}$ | $2.5\times10^{20}$ atoms/cm³ |
| initial concentration of P in the wafer | $c_{A0}$ | 0 |
| diffusivity of P in Si at 1100 °C | $D_{AB}$ | $6.5\times10^{-13}$ cm²/s |
| doping time | $t$ | 1 h = 3600 s |
| film edge (1 % of the surface value) | $c_A$ | $2.5\times10^{18}$ atoms/cm³ |

## Assumptions

- Unsteady state.
- Semi-infinite medium.
- One-dimensional diffusion in the $z$-direction.
- Constant boundary conditions ($c_{A0}$ and $c_{As}$).
- Constant temperature and pressure, and constant diffusivity.

## Tasks

1. **Physics.** Starting from a mass balance on a thin slice of the wafer and Fick's first law, derive the diffusion equation for $c_A(z, t)$. State the initial condition and the two boundary conditions.
2. **Exact solution.** Use the analytical solution
   $\dfrac{c_{As} - c_A}{c_{As} - c_{A0}} = \mathrm{erf}\!\left(\dfrac{z}{2\sqrt{D_{AB}\,t}}\right)$
   to find the film depth after 1 h.
3. **Grid.** The wafer is semi-infinite, but a computer grid must end somewhere. Choose a depth $z_{max}$ at which to cut the domain, and justify it. Use $\Delta z = 0.1$ µm.
4. **Discretization.** Discretize the diffusion equation with the explicit **FTCS** scheme (forward difference in time, central difference in space).
5. **Solution setup.** Find the stability condition of the scheme and choose a stable time step $\Delta t$.
6. **Results.** March from $t = 0$ to $t = 1$ h. Plot the concentration profile at several times and find the film depth after 1 h. Compare with the exact solution.
7. **Verification.** Refine the grid and show that the numerical solution converges. What happens if the time step violates the stability condition?

## What you will learn

- How a mass balance and Fick's law lead to the unsteady diffusion equation.
- How to treat a semi-infinite domain with a finite grid.
- How to march a parabolic PDE in time with the explicit FTCS scheme.
- Why explicit schemes have a time-step limit, and what happens when you break it.
- How to extract a quantity of interest (the film depth) from a discrete profile.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell.
:::
