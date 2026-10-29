---
title: Advection of a pulse, by hand
subtitle: A board-by-board guide for teaching the CFL condition, von Neumann analysis, numerical diffusion and dispersion with a pocket calculator, before showing the code
problem: 9
kind: Whiteboard guide
---

::: goal
**Aim of the lesson.** Students march a pulse of dye round a loop by hand on **8 nodes**, two time steps with each of three schemes at $C = 0.5$. They *see* upwind smear the pulse (all values positive), Lax–Wendroff put a negative value behind it, and FTCS make it grow. Then they find the reason on the board with a **von Neumann analysis**, first by putting one wave through the formulas by hand, then with the amplification factor $G$. Every number below can be checked against the notebook cells under *Checking the whiteboard numbers* and *Von Neumann stability analysis*.
:::

## Lesson plan (about 60 minutes)

| Board | Content | Time |
|:-:|---|:-:|
| 1 | The loop, the advection equation, characteristics and the exact solution | 6 min |
| 2 | The periodic grid, the Courant number and the CFL condition | 7 min |
| 3 | Three schemes and their weights at $C = 0.5$ | 8 min |
| 4 | Upwind, two steps by hand | 7 min |
| 5 | Lax–Wendroff, two steps by hand | 8 min |
| 6 | FTCS, two steps by hand: it grows | 6 min |
| 7 | Von Neumann analysis on the board: one wave by hand, then $G$ | 12 min |
| 8 | $C = 1$, $C > 1$, numerical diffusion and what the computer shows | 6 min |

::: tip
**Calculator advice for the class.** At $C = 0.5$ all weights are simple fractions (0.5; 0.375, 0.75, 0.125; 0.25), so every number is exact with at most **6 decimals**. Always compute a new time level **entirely from the old one**: write the old row on the board and do not overwrite it. Remember the wrap: the west neighbour of node 0 is node 7, the east neighbour of node 7 is node 0 (here those values are 0, so the wrap does not change any number, but say it).
:::

## Board 1 · The loop and the advection equation

![The closed loop and the unrolled, periodic domain.](figures/schematic.png)

Write the data: loop length $L = 1$ m, plug flow $c = 1$ m/s, one lap $t = L/c = 1$ s. The dye is only **carried**, it does not diffuse.

**Balance** of the dye in a piece of pipe between $x$ and $x + dx$: what flows in minus what flows out,

$$\frac{\partial u}{\partial t}\,dx = c\,u(x) - c\,u(x + dx) \qquad\Longrightarrow\qquad \frac{\partial u}{\partial t} + c\,\frac{\partial u}{\partial x} = 0.$$

**Characteristics.** Ride along with the water, $x = x_0 + c\,t$: then $du/dt = u_t + c\,u_x = 0$. Each value is carried unchanged:

$$u(x, t) = u_0(x - c\,t).$$

**Ask the class:** *What does the dye look like after one lap?* (Exactly like at the start. Anything else is a numerical error.)

Point out the type: **hyperbolic**. Information travels with speed $c$, in one direction, and nothing fades. Compare with Problem 2 (diffusion: a disturbance is felt everywhere at once and dies out).

## Board 2 · The grid, the Courant number and the CFL condition

![The periodic grid with $N = 8$: nodes 0 to 7, node 8 is node 0 again.](figures/grid.png)

$$N = 8, \qquad \Delta x = 0.125\ \text{m}, \qquad x_i = 0,\ 0.125,\ \dots,\ 0.875\ \text{m}.$$

**Courant number:** the distance the flow moves in one step, in grid intervals,

$$C = \frac{c\,\Delta t}{\Delta x}. \qquad\text{We take } C = 0.5:\quad \Delta t = \frac{0.5 \times 0.125}{1} = 0.0625\ \text{s}.$$

**Initial values.** The square pulse covers $0.4 \le x \le 0.6$ m: on this grid only node 4 ($x = 0.5$) is inside.

| node $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| $u_i^0$ | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 |

**Exact answer after two steps:** the flow moves $2 \times 0.5 = 1$ interval, so the spike is at **node 5**.

**CFL condition.** Draw the characteristic back from $P$ at $t^{n+1}$: it lands $C\,\Delta x$ upstream.

![The characteristic through $P$ lands inside the stencil for $C = 0.5$, outside it for $C = 1.1$.](figures/cfl-stencil.png)

**Ask the class:** *Our formulas use only $W$, $P$ and $E$. What if $C = 1.1$?* (The information comes from beyond $W$; the scheme cannot see it: $C \le 1$.)

## Board 3 · Three schemes

Forward in time, three choices for $\partial u/\partial x$ (multiply by $\Delta t$ to bring in $C$):

| scheme | $\partial u/\partial x$ | update | weights at $C = 0.5$ |
|---|---|---|---|
| FTCS | $\dfrac{u_E - u_W}{2\Delta x}$ | $u_P - \frac{C}{2}(u_E - u_W)$ | $0.25\,u_W + u_P - 0.25\,u_E$ |
| upwind | $\dfrac{u_P - u_W}{\Delta x}$ | $(1 - C)\,u_P + C\,u_W$ | $0.5\,u_W + 0.5\,u_P$ |
| Lax–Wendroff | central + $\tfrac12\Delta t^2 u_{tt}$ | $u_P - \frac{C}{2}(u_E - u_W) + \frac{C^2}{2}(u_E - 2u_P + u_W)$ | $0.375\,u_W + 0.75\,u_P - 0.125\,u_E$ |

Lax–Wendroff on the board: $u^{n+1} = u + \Delta t\,u_t + \tfrac12\Delta t^2\,u_{tt}$, and the equation gives $u_t = -c\,u_x$, $u_{tt} = c^2 u_{xx}$. Its weights at $C = 0.5$: $W$: $0.25 + 0.125 = 0.375$; $P$: $1 - 0.25 = 0.75$; $E$: $-0.25 + 0.125 = -0.125$.

**Ask the class:** *What do the weights of each scheme add up to?* (1, always: a constant $u$ stays constant.) *Which schemes have a negative weight?* (FTCS and Lax–Wendroff. Remember Problem 5: negative weights allow values outside the range of the neighbours.)

## Board 4 · Upwind by hand: $u_i^{new} = 0.5\,u_{i-1} + 0.5\,u_i$

Only nodes near the spike change; all others stay 0.

**Step 1** (from $u^0$):

| node | calculation | $u_i^1$ |
|:-:|---|:-:|
| 4 | $0.5 \times 0 + 0.5 \times 1$ | **0.5** |
| 5 | $0.5 \times 1 + 0.5 \times 0$ | **0.5** |

**Step 2** (from $u^1$):

| node | calculation | $u_i^2$ |
|:-:|---|:-:|
| 4 | $0.5 \times 0 + 0.5 \times 0.5$ | **0.25** |
| 5 | $0.5 \times 0.5 + 0.5 \times 0.5$ | **0.5** |
| 6 | $0.5 \times 0.5 + 0.5 \times 0$ | **0.25** |

**Point out:** the centre is right, $\sum i\,u_i = 4 \times 0.25 + 5 \times 0.5 + 6 \times 0.25 = 5$ (node 5, as the exact solution), and the amount is right, $\sum u_i = 1$. But the spike is now spread over three nodes and its peak is 0.5 instead of 1. Every value stays between 0 and 1: two positive weights make each new value an **average**. This is **numerical diffusion**.

## Board 5 · Lax–Wendroff by hand: $u_i^{new} = 0.375\,u_{i-1} + 0.75\,u_i - 0.125\,u_{i+1}$

**Step 1:**

| node | calculation | $u_i^1$ |
|:-:|---|:-:|
| 3 | $0.375 \times 0 + 0.75 \times 0 - 0.125 \times 1$ | **−0.125** |
| 4 | $0.375 \times 0 + 0.75 \times 1 - 0.125 \times 0$ | **0.75** |
| 5 | $0.375 \times 1 + 0.75 \times 0 - 0.125 \times 0$ | **0.375** |

**Step 2:**

| node | calculation | $u_i^2$ |
|:-:|---|:-:|
| 2 | $0 + 0 - 0.125 \times (-0.125)$ | **0.015625** |
| 3 | $0 + 0.75 \times (-0.125) - 0.125 \times 0.75$ | **−0.1875** |
| 4 | $0.375 \times (-0.125) + 0.75 \times 0.75 - 0.125 \times 0.375$ | **0.46875** |
| 5 | $0.375 \times 0.75 + 0.75 \times 0.375 - 0.125 \times 0$ | **0.5625** |
| 6 | $0.375 \times 0.375 + 0 - 0$ | **0.140625** |

**Check:** $\sum u_i = 0.015625 - 0.1875 + 0.46875 + 0.5625 + 0.140625 = 1$ ✓, and $\sum i\,u_i = 5$ ✓. The peak is now 0.5625 at node 5 (better than upwind's 0.5), but there is a **negative** concentration, $-0.19$, at node 3, **behind** the pulse. No dye concentration can be negative.

**Ask the class:** *Why behind, not in front?* (Board 7: the short waves travel too slowly and fall back.)

## Board 6 · FTCS by hand: $u_i^{new} = 0.25\,u_{i-1} + u_i - 0.25\,u_{i+1}$

**Step 1:** node 3: $-0.25 \times 1$ = **−0.25**; node 4: **1**; node 5: $0.25 \times 1$ = **0.25**.

**Step 2:**

| node | calculation | $u_i^2$ |
|:-:|---|:-:|
| 2 | $0 + 0 - 0.25 \times (-0.25)$ | **0.0625** |
| 3 | $0 + (-0.25) - 0.25 \times 1$ | **−0.5** |
| 4 | $0.25 \times (-0.25) + 1 - 0.25 \times 0.25$ | **0.875** |
| 5 | $0.25 \times 1 + 0.25 - 0$ | **0.5** |
| 6 | $0.25 \times 0.25 + 0 - 0$ | **0.0625** |

Again $\sum u_i = 1$ and $\sum i\,u_i = 5$: all three schemes conserve the dye and move its centre correctly. The difference is in the **sum of squares** $\sum u_i^2$, which measures how big the bumps are:

| | start | after step 1 | after step 2 |
|---|:-:|:-:|:-:|
| upwind | 1 | 0.5 | 0.375 |
| Lax–Wendroff | 1 | 0.71875 | 0.591309 |
| FTCS | 1 | **1.125** | **1.273438** |
| exact | 1 | 1 | 1 |

![The two steps by hand for the three schemes.](figures/hand.png)

**Ask the class:** *FTCS gives the biggest peak (0.875). Is it the best scheme?* (No: its sum of squares **grows**. The values $-0.5$ and $0.5$ next to the spike are wiggles that keep growing.)

## Board 7 · Von Neumann analysis on the board

**First by hand.** Put the wave $4\Delta x$ long, $u_i = 1, 0, -1, 0, 1, 0, -1, 0$ (it is $\cos(\pi i/2)$, so $\theta = \pi/2$), through the three formulas once. Two nodes are enough, the rest repeats:

| | node 0 ($W = 0$, $P = 1$, $E = 0$) | node 1 ($W = 1$, $P = 0$, $E = -1$) | new wave | size $\sqrt{u_0^2 + u_1^2}$ |
|---|:-:|:-:|---|:-:|
| FTCS | $0 + 1 - 0 = 1$ | $0.25 + 0 + 0.25 = 0.5$ | $1, 0.5, -1, -0.5, \dots$ | $\sqrt{1.25}$ = **1.118** |
| upwind | $0 + 0.5 = 0.5$ | $0.5 + 0 = 0.5$ | $0.5, 0.5, -0.5, -0.5, \dots$ | $\sqrt{0.5}$ = **0.707** |
| Lax–Wendroff | $0 + 0.75 - 0 = 0.75$ | $0.375 + 0 + 0.125 = 0.5$ | $0.75, 0.5, -0.75, -0.5, \dots$ | $\sqrt{0.8125}$ = **0.901** |

The wave keeps its shape and only changes its size and position: FTCS makes it **11.8 % bigger every step**. One lap is 200 steps on the notebook's grid: $1.118^{200} = 1.25^{100} \approx 5 \times 10^9$.

**Then in general.** Put $u_i^n = G^n\,e^{\,\mathrm{i}\theta i}$ into FTCS and divide by $u_i^n$, using $u_{i\pm1} = e^{\pm\mathrm{i}\theta}u_i$:

$$G = 1 - \frac{C}{2}\left(e^{\mathrm{i}\theta} - e^{-\mathrm{i}\theta}\right) = 1 - \mathrm{i}\,C\sin\theta, \qquad |G|^2 = 1 + C^2\sin^2\theta.$$

Check with the table: $C = 0.5$, $\theta = \pi/2$: $|G|^2 = 1 + 0.25 = 1.25$, $|G| = 1.118$ ✓. And $|G|^2 > 1$ for **every** $C > 0$ and every wave except $\theta = 0$ and $\pi$: FTCS is **unconditionally unstable**. A smaller $\Delta t$ does not help.

Write the results for the other two (derivation as homework):

$$|G_{upwind}|^2 = 1 - 2C(1 - C)(1 - \cos\theta), \qquad |G_{LW}|^2 = 1 - C^2(1 - C^2)(1 - \cos\theta)^2.$$

At $C = 0.5$, $\theta = \pi/2$: $1 - 2 \times 0.25 = 0.5$ ($|G| = 0.707$ ✓) and $1 - 0.25 \times 0.75 = 0.8125$ ($|G| = 0.901$ ✓). Both are $\le 1$ for every wave exactly when $0 \le C \le 1$.

**Where did the wave go?** The exact wave moves $C = 0.5$ interval per step, a phase of $C\theta = 45°$. Upwind's new wave $0.5, 0.5, -0.5, -0.5$ is exactly the old one shifted half an interval (and smaller): right speed. FTCS's and Lax–Wendroff's lie less far along: **too slow**. Short waves that travel too slowly fall behind the pulse: the negative value of Board 5.

![Amplitude and speed of every wave at $C = 0.5$.](figures/amplification.png)

## Board 8 · $C = 1$, $C > 1$ and numerical diffusion

**$C = 1$.** Put $C = 1$ into upwind: $u_i^{new} = u_{i-1}$. Lax–Wendroff: weights $W$: $0.5 + 0.5 = 1$, $P$: $1 - 1 = 0$, $E$: $-0.5 + 0.5 = 0$, the same. Each step moves every value exactly one node: **exact**. The characteristic lands exactly on $W$.

**$C = 1.1$.** The shortest wave ($\theta = \pi$, $u = 1, -1, 1, \dots$): upwind $G = 1 - 2C = -1.2$, $|G| = 1.2 > 1$: it grows 20 % per step. The computer shows the square pulse at $10^6$ after one lap.

**Numerical diffusion.** Taylor-expand the upwind formula (do it in two lines, keep the $u_{tt}$ and $u_{xx}$ terms, use $u_{tt} = c^2 u_{xx}$):

$$u_t + c\,u_x = D_{num}\,u_{xx}, \qquad D_{num} = \frac{c\,\Delta x}{2}\,(1 - C).$$

**Ask the class:** *Where have we seen $u\,\Delta x/2$ before?* (Problem 5: the false diffusion of upwinding.) Here the error of the time step removes a fraction $C$ of it, all of it at $C = 1$.

On the notebook's grid ($\Delta x = 0.01$ m, $C = 0.5$): $D_{num} = 0.01 \times 0.5/2 = 0.0025$ m²/s. A Gaussian of width $\sigma = 0.05$ m diffusing for 1 s widens to $\sigma_t = \sqrt{0.0025 + 2 \times 0.0025 \times 1} = 0.0866$ m and its peak falls to $0.05/0.0866$ = **0.577**. The computer's upwind peak after one lap: **0.577**.

::: answer
**Summary for the board.** After two steps at $C = 0.5$ (exact: a spike of height 1 at node 5): upwind gives 0.25, 0.5, 0.25 (spread, positive: numerical diffusion); Lax–Wendroff gives 0.016, −0.19, 0.47, 0.56, 0.14 (better peak, negative value behind: dispersion); FTCS gives 0.06, −0.5, 0.875, 0.5, 0.06 with a growing sum of squares (unstable, $|G| = 1.118$ for the $4\Delta x$ wave). Upwind and Lax–Wendroff are stable for $C \le 1$ and exact at $C = 1$.
:::

## Questions for the class

- **Reverse the flow** ($c = -1$ m/s). Which node is upwind now, and what is the upwind formula? ($u_i^{new} = u_i + C\,(u_{i+1} - u_i)$ with $C = |c|\,\Delta t/\Delta x$.) What happens if you keep the old formula? (The characteristic comes from the east, outside the stencil: unstable.)
- **What does upwind do to the shortest wave** $1, -1, 1, -1$ at $C = 0.5$? ($0.5 \times (-1) + 0.5 \times 1 = 0$: it disappears in one step, $|G| = 0$.)
- **Why is FTCS fine for diffusion (Problem 2) but not here?** (The diffusion term adds positive damping $r(u_E - 2u_P + u_W)$; pure advection has none to stabilise the central difference.)
- **On a fixed grid, does a smaller time step help upwind?** (No: $D_{num} = \tfrac12 c\,\Delta x(1 - C)$ grows as $C$ falls. The notebook: peak 0.50 at $C = 0.25$, 0.58 at $C = 0.5$, 0.71 at $C = 0.75$.)
- **A real flow has a different speed everywhere.** Can $C = 1$ hold at every node? (No. Codes choose $\Delta t$ from the largest $c/\Delta x$ and run below $C = 1$.)

## Common mistakes to watch for

- **Overwriting old values** during a step: the new level must be computed entirely from the old one (unlike Gauss–Seidel in Problems 1 and 3).
- Using the **downstream** node for upwind: for a flow from left to right the upwind node is $i - 1$.
- Forgetting the **periodic wrap** at nodes 0 and 7.
- Getting the Lax–Wendroff weights wrong: $C/2 = 0.25$ and $C^2/2 = 0.125$; the $E$ weight is $-0.25 + 0.125 = -0.125$.
- Thinking FTCS is best because its peak is highest after two steps: look at the growing wiggles and the sum of squares.
- Believing that a scheme that conserves the dye ($\sum u_i = 1$) must be right.

## From the board to the notebook

Every board has a matching cell in `03_fdm_solver.ipynb`: `step_ftcs`, `step_upwind` and `step_lax_wendroff` are Board 3; the cell under *Checking the whiteboard numbers* prints every value of Boards 4 to 6, with $\sum u_i$ and $\sum u_i^2$; `amplification` and its printed table are Board 7 ($|G|$ at $\theta = \pi/4, \pi/2, \pi$ for $C = 0.5$, 1 and 1.1). The notebook then runs one lap on 100 intervals at $C = 0.5$, 1.0 and 1.1, checks the modified-equation prediction of Board 8 at four Courant numbers, and shows in an error study from 25 to 1600 intervals that upwind converges at 1st order and Lax–Wendroff at 2nd order.
