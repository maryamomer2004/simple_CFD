---
title: Cooling a steel billet, by hand
subtitle: A board-by-board guide for teaching 2D time marching, explicit and implicit (ADI), with a pocket calculator, before showing the code
problem: 8
kind: Whiteboard guide
---

::: goal
**Aim of the lesson.** Students see a 2D temperature field evolve in time, step by step. On the coarsest possible grid (one quarter of the billet, $N = 2$, 3 × 3 nodes) they first check that lumped capacitance fails, derive the node equations from energy balances, find the time-step limit set by the cooled corner, and march **two explicit steps** by hand. Then they take **one ADI step** five times as long, with the Thomas algorithm of Problem 1, and compare both with the exact solution. Every number below can be checked against the notebook cell under *Checking the whiteboard numbers*.
:::

## Lesson plan (about 70 minutes)

| Board | Content | Time |
|:-:|---|:-:|
| 1 | The billet, the Biot number, and why one temperature is not enough | 7 min |
| 2 | Symmetry, the quarter, and the 3 × 3 grid | 6 min |
| 3 | Energy balances: the node equations and the time-step limit | 12 min |
| 4 | FTCS step 1: only the surface feels the cooling | 6 min |
| 5 | FTCS step 2: the cooling moves inwards | 10 min |
| 6 | ADI, half step 1: one tridiagonal system per row | 12 min |
| 7 | ADI, half step 2, and the comparison with the exact solution | 12 min |
| 8 | Questions and discussion | 5 min |

::: tip
**Calculator advice for the class.** Work with the **excess temperature** $\theta = T - T_\infty = T - 30$ °C: the cooling fluid is then at $\theta = 0$ and every constant $T_\infty$ term disappears. The billet starts at $\theta = 570$. Keep **3 decimals**. Use the **symmetry** of the quarter about its diagonal: node $(i, j)$ has the same temperature as node $(j, i)$, so only 6 of the 9 values must be computed in each FTCS step.
:::

## Board 1 · The billet and the Biot number

![The billet cross-section, cooled on all four sides.](figures/schematic.png)

Data: $2L = 100$ mm, $T_i = 600$ °C, $T_\infty = 30$ °C, $h = 1000$ W/(m²·K), steel $k = 48$ W/(m·K), $\rho = 7854$ kg/m³, $c_p = 559$ J/(kg·K).

$$\alpha = \frac{k}{\rho c_p} = \frac{48}{7854 \times 559} = 1.093 \times 10^{-5}\ \text{m}^2/\text{s}.$$

**Ask the class:** *Can we treat the billet as one temperature?* Lumped capacitance needs $Bi = hL_c/k < 0.1$, with $L_c = V/A$. Per metre of billet, $V = 0.1^2 = 0.01$ m³ and $A = 4 \times 0.1 = 0.4$ m², so $L_c = 0.025$ m:

$$Bi = \frac{1000 \times 0.025}{48} = 0.52 \quad\gg\quad 0.1.$$

**No.** The surface will be much colder than the centre. (If we did it anyway: $\tau = \rho c_p L_c/h = 109.8$ s and $t = \tau \ln(570/70) = 230$ s to reach 100 °C. Remember this number for the end of the lesson.)

## Board 2 · Symmetry and the grid

The billet is symmetric about its two centre lines: no heat crosses them. We compute **one quarter**, with the centre of the billet at the origin.

Grid: $N = 2$ intervals per side, $\Delta x = \Delta y = 25$ mm, nodes $(i, j)$ with $i, j = 0, 1, 2$:

| | $i = 0$ | $i = 1$ | $i = 2$ |
|:-:|:-:|:-:|:-:|
| $j = 2$ (cooled surface) | surface | surface | **corner** |
| $j = 1$ | symmetry | interior | surface |
| $j = 0$ (symmetry line) | **centre** | symmetry | surface |

All 9 temperatures are unknown. By the diagonal symmetry there are only 6 different values: the centre $(0,0)$, the symmetry node $(1,0) = (0,1)$, the interior node $(1,1)$, the surface middle $(2,0) = (0,2)$, the surface node $(2,1) = (1,2)$ and the corner $(2,2)$.

## Board 3 · Energy balances and the time-step limit

For each control volume: *(heat stored in one time step) = (heat flowing in, at the old time level).* With

$$r = \frac{\alpha\,\Delta t}{\Delta x^2}, \qquad Bi_{cell} = \frac{h\,\Delta x}{k} = \frac{1000 \times 0.025}{48} = 0.52083,$$

and in $\theta$ (so that $T_\infty$ disappears):

| node | control volume | FTCS update |
|---|---|---|
| interior $(1,1)$ | full cell | $\theta + r\,(\theta_E + \theta_W + \theta_N + \theta_S - 4\theta)$ |
| symmetry $(1,0)$ | half cell, or ghost $\theta_S = \theta_N$ | $\theta + r\,(\theta_E + \theta_W + 2\theta_N - 4\theta)$ |
| centre $(0,0)$ | quarter cell, two ghosts | $\theta + r\,(2\theta_E + 2\theta_N - 4\theta)$ |
| surface $(2,1)$ | half cell | $\theta + r\,(2\theta_W + \theta_N + \theta_S - 4\theta) - 2\,r\,Bi_{cell}\,\theta$ |
| surface middle $(2,0)$ | quarter cell | $\theta + r\,(2\theta_W + 2\theta_N - 4\theta) - 2\,r\,Bi_{cell}\,\theta$ |
| corner $(2,2)$ | quarter cell, two cooled faces | $\theta + 2r\,(\theta_W + \theta_S - 2\theta) - 4\,r\,Bi_{cell}\,\theta$ |

**Derive one on the board**, the corner: a quarter cell $\tfrac{\Delta x}{2} \times \tfrac{\Delta x}{2}$, heat from W and S through faces $\Delta x/2$ long, heat to the fluid through two faces $\Delta x/2$ long:

$$\rho c_p \frac{\Delta x^2}{4}\,\frac{\theta^{n+1} - \theta}{\Delta t} = k\,\frac{\Delta x}{2}\,\frac{\theta_W - \theta}{\Delta x} + k\,\frac{\Delta x}{2}\,\frac{\theta_S - \theta}{\Delta x} - 2\,h\,\frac{\Delta x}{2}\,\theta.$$

Multiply by $4\Delta t/(\rho c_p \Delta x^2)$ to get the last row of the table.

**The time-step limit.** The weight of $\theta$ itself must not be negative:

$$\text{interior: } 1 - 4r \ge 0, \qquad \text{corner: } 1 - 4r - 4rBi_{cell} \ge 0 \;\Longrightarrow\; r \le \frac{1}{4(1 + Bi_{cell})} = \frac{1}{4 \times 1.52083} = 0.164.$$

**Point out:** the corner is stricter than the interior (0.164 against 0.25), because it loses heat through two faces but stores heat in only a quarter cell.

We take $r = 0.14$, so $\Delta t = 0.14 \times 0.025^2/(1.093 \times 10^{-5}) = 8.00$ s. The numbers we need:

$$4r = 0.56, \qquad 2r = 0.28, \qquad 2\,r\,Bi_{cell} = 0.145833, \qquad 4\,r\,Bi_{cell} = 0.291667.$$

## Board 4 · FTCS step 1 ($t = 8$ s)

Start: $\theta = 570$ at every node. **Ask the class:** *Which nodes change in the first step?* Wherever all neighbours are equal, every bracket is zero. Only the **convection terms** act:

| node | calculation | new $\theta$ | $T$ [°C] |
|---|---|:-:|:-:|
| centre, symmetry, interior | brackets are 0, no convection | 570 | 600 |
| surface middle $(2,0)$, surface $(2,1)$ | $570 - 0.145833 \times 570 = 570 - 83.125$ | **486.875** | 516.875 |
| corner $(2,2)$ | $570 - 0.291667 \times 570 = 570 - 166.25$ | **403.750** | 433.750 |

**Point out:** in one step only the surface feels the cooling, and the corner (two cooled faces) feels it twice as much.

## Board 5 · FTCS step 2 ($t = 16$ s)

Use **only the values of step 1** on the right-hand side (explicit: write the new values in a new table).

| node | calculation | new $\theta$ | $T$ [°C] |
|---|---|:-:|:-:|
| centre $(0,0)$ | $570 + 0.14\,(2 \times 570 + 2 \times 570 - 4 \times 570)$ | 570.000 | 600.000 |
| symmetry $(1,0)$ | $570 + 0.14\,(486.875 + 570 + 2 \times 570 - 2280) = 570 - 11.6375$ | **558.3625** | 588.3625 |
| interior $(1,1)$ | $570 + 0.14\,(486.875 + 570 + 486.875 + 570 - 2280) = 570 - 23.275$ | **546.725** | 576.725 |
| surface middle $(2,0)$ | $486.875 + 0.14\,(2 \times 570 + 2 \times 486.875 - 4 \times 486.875) - 0.145833 \times 486.875$ | **439.147** | 469.147 |
| surface $(2,1)$ | $486.875 + 0.14\,(2 \times 570 + 403.75 + 486.875 - 4 \times 486.875) - 71.003$ | **427.510** | 457.510 |
| corner $(2,2)$ | $403.75 + 0.28\,(486.875 + 486.875 - 2 \times 403.75) - 0.291667 \times 403.75$ | **332.540** | 362.540 |

For the surface middle: $0.14 \times 166.25 = 23.275$ and $0.145833 \times 486.875 = 71.003$, so $486.875 + 23.275 - 71.003 = 439.147$.

For the corner: $0.28 \times 166.25 = 46.55$ and $0.291667 \times 403.75 = 117.760$, so $403.75 + 46.55 - 117.760 = 332.540$.

**Point out:** the cooling has moved one node inwards (the symmetry and interior nodes now change); the centre still has not noticed. Heat conduction needs time: on this grid the centre changes from step 3 on.

![The hand grid: two FTCS steps, then FTCS after 5 steps, one ADI step of the same 40 s, and the exact solution.](figures/hand.png)

## Board 6 · ADI, half step 1: implicit along the rows

**Ask the class:** *Can we take one step of 40 s instead of five of 8 s?* With FTCS $r = 0.70 > 0.164$: unstable. An **implicit** method can. ADI splits the step into two halves; in the first, the $x$ direction is implicit and the $y$ direction explicit. With $s = r/2 = 0.35$, for each row $j$:

$$\theta^*_i - s\,\delta_x^2\theta^*_i = \theta_i + s\,\delta_y^2\theta_i,$$

with the second differences of Board 3: $\delta^2\theta = 2(\theta_1 - \theta_0)$ at a symmetry node, $\theta_{i+1} - 2\theta_i + \theta_{i-1}$ inside, $2(\theta_1 - \theta_2) - 2Bi_{cell}\theta_2$ at a cooled node. The same 3 × 3 tridiagonal matrix serves every row:

$$\begin{bmatrix} 1.7 & -0.7 & \\ -0.35 & 1.7 & -0.35 \\ & -0.7 & 2.064583 \end{bmatrix}
\begin{bmatrix} \theta^*_0 \\ \theta^*_1 \\ \theta^*_2 \end{bmatrix} = \text{right-hand side}, \qquad 2.064583 = 1 + 0.7\,(1 + 0.52083).$$

**Thomas algorithm (Problem 1).** The forward-sweep factors depend only on the matrix, so compute them once:

$$c^*_0 = \frac{-0.7}{1.7} = -0.411765, \qquad d_1 = 1.7 - (-0.35)(-0.411765) = 1.555882, \qquad c^*_1 = \frac{-0.35}{1.555882} = -0.224953,$$
$$d_2 = 2.064583 - (-0.7)(-0.224953) = 1.907116.$$

Then for every right-hand side: $r^*_0 = \text{rhs}_0/1.7$, $r^*_1 = (\text{rhs}_1 + 0.35\,r^*_0)/1.555882$, $r^*_2 = (\text{rhs}_2 + 0.7\,r^*_1)/1.907116$, and back: $\theta_2 = r^*_2$, $\theta_1 = r^*_1 + 0.224953\,\theta_2$, $\theta_0 = r^*_0 + 0.411765\,\theta_1$.

**Right-hand sides** (explicit in $y$, from $\theta = 570$ everywhere): in rows $j = 0$ and $1$, $\delta_y^2\theta = 0$, so every entry is 570. In row $j = 2$ (the cooled surface), $\delta_y^2\theta = 2(570 - 570) - 2 \times 0.52083 \times 570 = -593.75$, so every entry is $570 - 0.35 \times 593.75 = 362.1875$.

| row | right-hand side | $r^*_0,\ r^*_1,\ r^*_2$ | $\theta^*_0,\ \theta^*_1,\ \theta^*_2$ |
|:-:|:-:|:-:|:-:|
| $j = 0$ and $j = 1$ | 570, 570, 570 | 335.294, 441.777, 461.033 | **559.907, 545.488, 461.033** |
| $j = 2$ | 362.1875 (×3) | 213.051, 280.712, 292.948 | **355.774, 346.612, 292.948** |

**Point out:** after this half step the cooling has reached **every node of a row at once**, even the centre (559.907 < 570). In an implicit method information crosses the whole grid in one step. The intermediate field $\theta^*$ is not symmetric (only $x$ was treated implicitly); the second half step restores the symmetry.

## Board 7 · ADI, half step 2, and the comparison

Now implicit along each **column** $i$, explicit in $x$ (using $\theta^*$): $\theta^{n+1}_j - s\,\delta_y^2\theta^{n+1}_j = \theta^*_j + s\,\delta_x^2\theta^*_j$. Same matrix, same factors.

Right-hand sides, for example column 0, row 0: $\delta_x^2\theta^* = 2(545.488 - 559.907) = -28.838$, so $559.907 - 0.35 \times 28.838 = 549.813$. Column 2, row 0 (a cooled node): $\delta_x^2\theta^* = 2(545.488 - 461.033) - 1.041667 \times 461.033 = -311.333$, so $461.033 - 108.967 = 352.066$.

| column | right-hand side ($j = 0, 1, 2$) | $r^*_0,\ r^*_1,\ r^*_2$ | $\theta^{n+1}$ ($j = 0, 1, 2$) |
|:-:|:-:|:-:|:-:|
| $i = 0$ | 549.813, 549.813, 349.361 | 323.420, 426.131, 339.598 | **530.342, 502.525, 339.598** |
| $i = 1$ | 520.975, 520.975, 331.036 | 306.456, 403.780, 321.786 | **502.525, 476.167, 321.786** |
| $i = 2$ | 352.066, 352.066, 223.709 | 207.098, 272.868, 217.457 | **339.598, 321.786, 217.457** |

**Point out:** the result **is** symmetric again: $\theta_{1,0} = \theta_{0,1} = 502.525$, $\theta_{2,0} = \theta_{0,2} = 339.598$.

**Compare at $t = 40$ s** (in °C, $T = \theta + 30$; the notebook did the five FTCS steps):

| node | FTCS, 5 steps of 8 s | ADI, 1 step of 40 s | exact |
|---|:-:|:-:|:-:|
| centre $(0,0)$ | 562.2 | 560.3 | 558.1 |
| interior $(1,1)$ | 488.8 | 506.2 | 484.6 |
| surface middle $(2,0)$ | 386.0 | 369.6 | 386.6 |
| corner $(2,2)$ | 267.6 | 247.5 | 270.8 |

::: answer
**One ADI step of 40 s (five different Thomas solves of 3 unknowns) gives the same picture as five FTCS steps**, and FTCS could not have taken that step at all. On this very coarse grid both differ from the exact solution by a few degrees inside; ADI is further off at the corner, because a single long step cannot follow the very fast initial cooling there. The notebook refines to 11 × 11 nodes, where FTCS ($\Delta t = 0.5$ s) and ADI ($\Delta t = 10$ s) both find that the centre reaches 100 °C after 349 s, as the exact solution does, and not after 230 s as lumped capacitance claimed on Board 1.
:::

## Questions for the class

- **Why does only the surface change in the first FTCS step?** (All brackets are zero in a uniform field; only the convection terms act. Information travels one node per explicit step.)
- **Why is the corner the most restrictive node?** (Two cooled faces, a quarter cell: it loses heat fastest relative to what it stores.)
- **What happens if we take $r = 0.25$ with FTCS on this grid?** (The corner weight $1 - 4r(1 + Bi_{cell}) = -0.52$ is negative. The notebook shows it oscillates and grows: unstable already at $r = 0.24$.)
- **Why is the ADI intermediate field not symmetric?** (In the first half step only $x$ is implicit; the second half step treats $y$ the same way and restores the symmetry.)
- **ADI is unconditionally stable. Can we take one step of 600 s?** (It stays bounded, but it is inaccurate, and the corner temperature oscillates. Stability is not accuracy.)
- **Why does lumped capacitance give a much shorter time?** (It uses the average temperature; the centre is the hottest point and the last to cool.)

## Common mistakes to watch for

- Forgetting the factor **2** for the ghost nodes on the symmetry lines, or for the neighbour across from a cooled face.
- Using **new** values on the right-hand side of an FTCS step.
- Forgetting the convection term ($-2rBi_{cell}\theta$, or $-4rBi_{cell}\theta$ at the corner), or its sign.
- In ADI: putting the implicit direction on the right-hand side, or forgetting the explicit $\delta^2$ term of the other direction.
- In the Thomas algorithm: the off-diagonals are **negative**, so $-a_i\,r^*_{i-1}$ becomes $+0.35\,r^*_0$ and $+0.7\,r^*_1$.

## From the board to the notebook

`03_fdm_solver.ipynb` repeats every board: the Biot-number check of Board 1 is the lumped-capacitance cell; the table of Board 3 is `second_difference` and `ftcs_step`; the limits of Board 3 are `limits`; Boards 6 and 7 are `adi_step`, which calls the `thomas` function of Problem 1. The cell under *Checking the whiteboard numbers* prints every field of Boards 4 to 7, and the notebook then refines the grid to 11 × 11 nodes (and up to 41 × 41 for the convergence study).
