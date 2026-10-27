---
title: Steady convection and diffusion in one dimension
subtitle: Central versus upwind differences for the convection term, solved with the Finite Difference Method
problem: 5
kind: Problem statement
---

## The problem

::: given
A property $\phi$ (for example a temperature or the concentration of a dye) is **transported by convection and diffusion** through a one-dimensional domain $0 \le x \le L$ between two reservoirs. The fluid flows from left to right with a **constant velocity** $u$. The left reservoir holds $\phi = 1$ and the right reservoir holds $\phi = 0$. Find the **steady-state distribution of $\phi$** with the **Finite Difference Method**, discretizing the convection term with **central differences** and with **upwind differences**, for a slow flow ($u = 0.1$ m/s) and a fast flow ($u = 2.5$ m/s).

*(Adapted from Versteeg & Malalasekera, An Introduction to Computational Fluid Dynamics, chapter 5.)*
:::

![A fluid flows with velocity $u$ from a reservoir at $\phi_0 = 1$ to a reservoir at $\phi_L = 0$. Convection carries $\phi$ downstream; diffusion spreads it in both directions.](figures/schematic.png)

## Governing equation

In steady state, with no source of $\phi$:

$$\frac{d(\rho u\,\phi)}{dx} = \frac{d}{dx}\left(\Gamma\,\frac{d\phi}{dx}\right), \qquad \phi(0) = \phi_0 = 1, \qquad \phi(L) = \phi_L = 0.$$

The flow also satisfies continuity, $d(\rho u)/dx = 0$, so $\rho u$ is constant.

## Data

| Quantity | Symbol | Value |
|---|:-:|---|
| length of the domain | $L$ | 1.0 m |
| density | $\rho$ | 1.0 kg/m³ |
| diffusion coefficient | $\Gamma$ | 0.1 kg/(m·s) |
| value at $x = 0$ (left reservoir) | $\phi_0$ | 1 |
| value at $x = L$ (right reservoir) | $\phi_L$ | 0 |
| velocity, case 1 (slow flow) | $u$ | 0.1 m/s |
| velocity, case 2 (fast flow) | $u$ | 2.5 m/s |
| grid for cases 1 and 2 | $N$, $\Delta x$ | 5 intervals, $\Delta x = 0.2$ m (nodes $0$ to $5$, unknowns $1$ to $4$) |
| grids for case 3 (refinement) | $N$ | 5, 10, 20, 40, 80, 160, 320 intervals, $u = 2.5$ m/s |

The exact solution of this problem is

$$\frac{\phi(x) - \phi_0}{\phi_L - \phi_0} = \frac{\exp(\rho u x/\Gamma) - 1}{\exp(\rho u L/\Gamma) - 1}.$$

::: note
**Data for simulation software** (for example COMSOL Multiphysics, *Transport of Diluted Species*, 1D):

- geometry: an interval from $x = 0$ to $x = 1$ m;
- diffusion coefficient $D = \Gamma/\rho = 0.1$ m²/s; convection by a given velocity field $u$ (no flow equations need to be solved);
- velocity $u = 0.1$ m/s (case 1) and $u = 2.5$ m/s (cases 2 and 3);
- boundary conditions: concentration $c(0) = 1$ mol/m³ and $c(L) = 0$; no reactions or sources; stationary study;
- mesh: uniform elements of size 0.2 m (5 elements) for cases 1 and 2; 0.1, 0.05, 0.025, 0.0125, 0.00625 and 0.003125 m (10 to 320 elements) for case 3.

With $c$ in mol/m³ the numbers are the same as $\phi$. Commercial codes add numerical **stabilisation** to the convection term by default; to compare with the plain central-difference scheme, switch it off.
:::

## Assumptions

- Steady state: $\phi$ no longer changes with time.
- One-dimensional transport along $x$.
- Constant density $\rho$, velocity $u$ and diffusion coefficient $\Gamma$.
- No source or sink of $\phi$ inside the domain.

## Tasks

1. **Physics.** Explain the two terms of the equation: what does convection do, and what does diffusion do? Compute the **Péclet number** $Pe_L = \rho u L/\Gamma$ for both velocities. Sketch how the exact solution changes as $u$ grows.
2. **Grid.** Divide the domain into $N = 5$ equal intervals. Compute the **cell Péclet number** $Pe_\Delta = \rho u\,\Delta x/\Gamma$ for both velocities.
3. **Discretization.** Use a central difference for the diffusion term, and for the convection term
   a. a **central difference** (CDS): $\;d\phi/dx|_i \approx (\phi_{i+1} - \phi_{i-1})/(2\Delta x)$;
   b. an **upwind difference** (UDS): $\;d\phi/dx|_i \approx (\phi_i - \phi_{i-1})/\Delta x$ for $u > 0$.

   Write each interior equation in the form $a_P\,\phi_i = a_W\,\phi_{i-1} + a_E\,\phi_{i+1}$ and give $a_W$, $a_E$ and $a_P$ in terms of $F = \rho u$ and $D = \Gamma/\Delta x$.
4. **Solution.** Solve the tridiagonal systems with the **Thomas algorithm**.
5. **Case 1** ($u = 0.1$ m/s) and **case 2** ($u = 2.5$ m/s). Compare CDS, UDS and the exact solution at the nodes. Which results are physically possible? Explain what you see using the signs of the coefficients.
6. **False diffusion.** Show that the upwind scheme equals the central scheme with an extra diffusion coefficient $\rho u\,\Delta x/2$. How large is it compared with $\Gamma$?
7. **Case 3, verification.** For $u = 2.5$ m/s, refine the grid ($N = 5$ to $320$). Plot the largest error against $\Delta x$ on log–log axes for both schemes. When does CDS start to work? What are the orders of accuracy?
8. *Optional.* Solve the case-2 equations with **Gauss–Seidel** iteration. What happens with CDS?

## What you will learn

- What the **convection term** does, and why it is what makes CFD *fluid* dynamics.
- What the **Péclet number** measures, and why the **cell** Péclet number decides how a scheme behaves.
- Why central differences produce **non-physical wiggles** when $Pe_\Delta > 2$ (negative coefficients, loss of diagonal dominance), and why upwinding is always **bounded**.
- What **false diffusion** is, and why commercial codes use upwind-biased or stabilised schemes.
- How a grid-refinement study reveals the **order of accuracy** of a scheme.

::: tip
**Files for this problem:** `02_solution.pdf` explains the solution step by step. `03_fdm_solver.ipynb` contains the complete Python code (plain Python, no numerical libraries), with explanations and plots, to run cell by cell. `04_whiteboard_guide.pdf` solves cases 1 and 2 by hand for the board.
:::
