---
title: Channel flow, by hand
subtitle: A board-by-board guide for teaching the projection method on a staggered grid with a pocket calculator, before showing the code
problem: 10
kind: Whiteboard guide
---

::: goal
**Aim of the lesson.** Students carry out **one complete time step of the projection method** by hand: the predictor, the pressure Poisson equation, the correction, and the check that the new velocity conserves mass. The grid is the smallest one that shows everything: a channel of $2 \times 3$ cells. Along the way they see why the pressure lives in the cell centres and the velocities on the faces, and how the inlet, the walls and the outlet enter the pressure equation. Every number below can be checked against the notebook cell under *Checking the whiteboard numbers*.
:::

## Lesson plan (about 60 minutes)

| Board | Content | Time |
|:-:|---|:-:|
| 1 | The channel, the entrance length, and why we now need the pressure | 7 min |
| 2 | The projection method in three lines | 8 min |
| 3 | The staggered grid and the checkerboard | 10 min |
| 4 | The hand grid, ghost values, step 1: predictor | 8 min |
| 5 | Step 2: the pressure equation of each cell, solved by hand | 12 min |
| 6 | Step 3: correction, divergence check, flow rate | 10 min |
| 7 | From one step to the steady flow; questions | 5 min |

::: tip
**Calculator advice for the class.** Work with $h = 1/3$, $Re = 50$, $\Delta t = 0.01$. Useful combinations: $1/(Re\,h^2) = 9/50 = 0.18$, $h/\Delta t = 33.33$, $\Delta t/h = 0.03$ and $\Delta t/(h/2) = 0.06$. Keep **6 decimals** for velocities and pressures: the changes in one time step are small.
:::

## Board 1 · The channel and the entrance length

![The channel: uniform inlet, growing boundary layers, the parabola of fully developed flow, the outlet at p = 0.](figures/schematic.png)

**Ask the class:** *The fluid enters with the same speed everywhere. What happens next to the walls? And in the middle?* Next to the walls it is slowed by friction (no slip). The same amount of fluid must pass every cross-section, so the middle has to speed up. Far downstream the profile stops changing: the parabola $u = 6U\,(y/H)(1 - y/H)$, with $u_{max} = 1.5\,U$.

The **entrance length** $L_e$ is where the centre velocity reaches 99 % of $1.5\,U$; Durst et al. (2005): $L_e \approx 0.044\,Re\,H$ for not too small $Re$.

**Why not the stream function and vorticity of Problems 6 and 7?** We want the **pressure drop**, and that is the variable they eliminate. So we solve for $u$, $v$ and $p$ directly ("primitive variables"). But there is no equation **for** $p$: the pressure is whatever keeps $\nabla\cdot\mathbf u = 0$.

## Board 2 · The projection method in three lines

Write in a box:

1. **Predictor** (momentum without the pressure): $\mathbf u^* = \mathbf u^n + \Delta t\left[\dfrac{1}{Re}\nabla^2\mathbf u^n - (\mathbf u^n\cdot\nabla)\,\mathbf u^n\right]$
2. **Pressure Poisson equation:** $\nabla^2 p = \dfrac{\nabla\cdot\mathbf u^*}{\Delta t}$
3. **Correction:** $\mathbf u^{n+1} = \mathbf u^* - \Delta t\,\nabla p$, and now $\nabla\cdot\mathbf u^{n+1} = 0$.

**Point out:** step 2 follows from step 3: take the divergence of step 3 and demand $\nabla\cdot\mathbf u^{n+1} = 0$. Step 1 is Problem 5's convection–diffusion, step 2 is Problem 3's Poisson equation. Nothing here is new except how they are put together.

## Board 3 · The staggered grid and the checkerboard

Draw a row of nodes with the pressures $1, 0, 1, 0, 1, 0$. **Ask the class:** *What is the pressure gradient at the second node with a central difference?* $(p_E - p_W)/(2h) = (1 - 1)/(2h) = 0$. At every node it is zero! If $u$, $v$ and $p$ are stored at the same points (a **collocated** grid), the momentum equations cannot see this zig-zag (in 2D: a checkerboard), and nothing removes it.

![The staggered grid: p at the cell centres, u on the vertical faces, v on the horizontal faces; ghost values (grey) outside.](figures/grid.png)

**The cure (Harlow and Welch, 1965):** pressure at the **cell centres**, $u$ on the **vertical faces**, $v$ on the **horizontal faces**. The push on a face is $(p_E - p_P)/h$, from the two cells on either side: for the zig-zag it is $\pm 1/h$, the largest possible. And the mass leaving a cell is simply what crosses its four faces:

$$\nabla\cdot\mathbf u \;\to\; \frac{u_E - u_W + v_N - v_S}{h}.$$

## Board 4 · The hand grid and step 1: the predictor

![The hand grid: 2 × 3 cells of size h = 1/3 (L = 2/3). Inlet u = 1 on the left, outlet p = 0 on the right, walls at the top and bottom. The numbers are those after the time step (Board 6).](figures/hand-1.png)

**Start:** plug flow, $u = 1$ on all vertical faces, $v = 0$, $p = 0$.

**Ghost values.** A wall lies **between** the first row of $u$ and a ghost row. No slip means their average is zero: $u_{ghost} = -u_{inside} = -1$. (At the inlet, $v_{ghost} = -v = 0$.)

**Predictor for $u$ on the inner faces** ($i = 1$). With $u$ uniform along $x$ and $v = 0$, the convection terms are zero; only diffusion across the channel acts:

| face | $u_E + u_W + u_N + u_S - 4u_P$ | $\times\,\Delta t/(Re\,h^2) = 0.0018$ | $u^*$ |
|:-:|---|:-:|:-:|
| bottom row, $j = 1$ | $1 + 1 + 1 + (-1) - 4 = -2$ | $-0.0036$ | **0.996400** |
| middle row, $j = 2$ | $1 + 1 + 1 + 1 - 4 = 0$ | $0$ | **1.000000** |
| top row, $j = 3$ | $1 + 1 + (-1) + 1 - 4 = -2$ | $-0.0036$ | **0.996400** |

The **outlet** faces copy their neighbour ($\partial u/\partial x = 0$): $0.996400$, $1.000000$, $0.996400$. All $v^* = 0$ (nothing has made $v$ move yet).

**Point out:** the wall rows slowed down, the middle did not: so $u^*$ **loses mass**. Cell $(1, 1)$ receives $1$ through its left face but passes on only $0.9964$ through its right face.

## Board 5 · Step 2: the pressure equation

For every cell, multiplied by $h^2$:

$$a_E(p_E - p_P) + a_W(p_W - p_P) + a_N(p_N - p_P) + a_S(p_S - p_P) = b_P = \frac{h}{\Delta t}\,(u^*_E - u^*_W + v^*_N - v^*_S).$$

**The coefficients at the boundary.** Ask the class for each side:

- **inlet, walls:** the velocity is **given** there and must not be corrected, so $\partial p/\partial n = 0$: drop the term ($a = 0$);
- **outlet:** $p = 0$ **on the face**, only half a cell from the centre: $(0 - p_P)/(h/2)$, so $a_E = 2$, $p_E = 0$;
- inside: $a = 1$.

**Sources.** $b_{(1,1)} = 33.33 \times (0.9964 - 1) = -0.12$; the same for $(1, 3)$; all others are $0$ (the outlet cells pass on what they receive).

**Symmetry.** Top and bottom rows are mirror images: $p_{1,3} = p_{1,1}$, $p_{2,3} = p_{2,1}$. Four unknowns remain:

| cell | equation | simplified |
|:-:|---|---|
| (1, 1) | $(p_{21} - p_{11}) + (p_{12} - p_{11}) = -0.12$ | $p_{21} + p_{12} - 2p_{11} = -0.12$ |
| (2, 1) | $2(0 - p_{21}) + (p_{11} - p_{21}) + (p_{22} - p_{21}) = 0$ | $p_{11} + p_{22} - 4p_{21} = 0$ |
| (1, 2) | $(p_{22} - p_{12}) + 2\,(p_{11} - p_{12}) = 0$ | $p_{22} + 2p_{11} - 3p_{12} = 0$ |
| (2, 2) | $2(0 - p_{22}) + (p_{12} - p_{22}) + 2\,(p_{21} - p_{22}) = 0$ | $p_{12} + 2p_{21} - 5p_{22} = 0$ |

**Elimination** (with the class): from (2, 1), $p_{22} = 4p_{21} - p_{11}$. Into (1, 2): $p_{12} = (p_{11} + 4p_{21})/3$. Into (2, 2), times 3: $16\,p_{11} = 50\,p_{21}$, so $p_{21} = 0.32\,p_{11}$, then $p_{12} = 0.76\,p_{11}$ and $p_{22} = 0.28\,p_{11}$. Finally (1, 1): $-0.92\,p_{11} = -0.12$:

$$p_{11} = \tfrac{3}{23} = \mathbf{0.130435}, \quad p_{21} = \mathbf{0.041739}, \quad p_{12} = \mathbf{0.099130}, \quad p_{22} = \mathbf{0.036522}.$$

**Point out:** the pressure is highest at the inlet next to the walls, where the fluid is being slowed down most, and it falls towards the outlet. The computer solves the same equations with SOR (68 sweeps for this tiny grid to 13 decimals), not by elimination.

## Board 6 · Step 3: the correction, and the check

$u = u^* - \Delta t\,(p_E - p_P)/h$ with $\Delta t/h = 0.03$; at the outlet $\Delta t/(h/2) = 0.06$ and $p_E = 0$; $v = v^* - \Delta t\,(p_N - p_P)/h$:

| face | calculation | new value |
|---|---|:-:|
| $u$, bottom row, $i = 1$ | $0.9964 - 0.03\,(0.041739 - 0.130435)$ | **0.999061** |
| $u$, bottom row, outlet | $0.9964 - 0.06\,(0 - 0.041739)$ | **0.998904** |
| $u$, middle row, $i = 1$ | $1 - 0.03\,(0.036522 - 0.099130)$ | **1.001878** |
| $u$, middle row, outlet | $1 - 0.06\,(0 - 0.036522)$ | **1.002191** |
| $v$, above the bottom row, $i = 1$ | $0 - 0.03\,(0.099130 - 0.130435)$ | **+0.000939** |
| $v$, above the bottom row, $i = 2$ | $0 - 0.03\,(0.036522 - 0.041739)$ | **+0.000157** |

The top row mirrors the bottom one ($v = -0.000939$ and $-0.000157$ below the top row).

**Divergence check**, $u_E - u_W + v_N - v_S$ for each cell (×$1/h$):

| cell | $u_E - u_W$ | $v_N - v_S$ | sum |
|:-:|:-:|:-:|:-:|
| (1, 1) | $0.999061 - 1 = -0.000939$ | $0.000939 - 0$ | **0** |
| (2, 1) | $0.998904 - 0.999061 = -0.000157$ | $0.000157 - 0$ | **0** |
| (1, 2) | $1.001878 - 1 = +0.001878$ | $-0.000939 - 0.000939$ | **0** |
| (2, 2) | $1.002191 - 1.001878 = +0.000313$ | $-0.000157 - 0.000157$ | **0** (rounding) |

**Flow rate at the outlet:** $\tfrac13\,(0.998904 + 1.002191 + 0.998904) = 1.000000$.

::: answer
**After one projection step, mass is conserved in every cell.** The pressure pushed the fluid that the walls slowed down **towards the centre** ($v > 0$ above the bottom row, $v < 0$ below the top row), and the middle row **accelerated** from 1 to 1.0022. That is exactly how the flow develops: repeat this step a few hundred times and the profile becomes the Poiseuille parabola.
:::

## Board 7 · From one step to the steady flow

The notebook repeats the same three steps on a grid of $160 \times 16$ cells. Starting from plug flow, it needs about 500 time steps at $Re = 50$ and 1500 at $Re = 100$ (the stable time step is $\Delta t = 0.0142$ and $0.0071$) to reach the steady state. The result: $L_e = 2.44\,H$ and $4.67\,H$ (Durst et al.: $2.39\,H$ and $4.54\,H$), the parabola downstream, and the flow rate equal to 1 at every cross-section to eight decimals.

## Questions for the class

- **Why does the pressure equation have no source in the middle row?** (There $u^* = 1$ on both faces: no mass is lost in the predictor.)
- **Why $a_E = 2$ at the outlet but $a = 0$ at the walls?** (At the outlet the pressure is given, half a cell away; at the walls the velocity is given, so the pressure must not push through them.)
- **What if we prescribed both $u$ and $p$ at the inlet?** (Too many conditions: the flow rate would be fixed twice, and in general no solution exists.)
- **Why does $v$ point towards the centre?** (The slowed fluid near the walls leaves less room for the flow; continuity pushes the excess towards the middle.)
- **What would the checkerboard of Board 3 do on the staggered grid?** (It produces the largest possible pressure push on every face, so the correction removes it at once.)

## Common mistakes to watch for

- Putting the wall **on** the first row of $u$: on the staggered grid it lies **halfway** between the first row and the ghost row, so $u_{ghost} = -u$, not $u_{ghost} = 0$.
- Forgetting the factor **2** of the outlet coefficient (the face is only $h/2$ away).
- Keeping wall or inlet terms in the pressure equation (they must be dropped: $\partial p/\partial n = 0$).
- Correcting the inlet velocity or the wall $v$: they are given and never change.
- Sign errors in $b_P$: it is **out minus in**, $u^*_E - u^*_W + v^*_N - v^*_S$.

## From the board to the notebook

`03_fdm_solver.ipynb` repeats every board: `boundary_conditions` sets the ghost values of Board 4, `predictor` is Board 4's table, `pressure_source` and `solve_pressure` are Board 5 (solved with SOR and a block correction instead of elimination), `correct` and `divergence` are Board 6. The cell under *Checking the whiteboard numbers* prints all of them for this hand grid. `solve_channel` then repeats the step until the flow is steady.
