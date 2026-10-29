# Problem 10 · COMSOL handoff (for the desktop session)

This file is a work order for a later session on the owner's Windows PC with **COMSOL Multiphysics 4.3a**. It contains everything needed to build the COMSOL model of Problem 10 and the student guide, without any other context. When the work is done, **replace this file with `README.md`** (see §1) and delete `HANDOFF.md`. Nothing in this folder links to this file on purpose.

Nothing COMSOL-related has been run yet: no `.mph` file exists and no COMSOL number below is known. All reference numbers come from the finite difference (FDM) notebook `../03_fdm_solver.ipynb` and are stored in [`fdm_reference.json`](fdm_reference.json) in this folder.

---

## 0 · The problem in five lines

A fluid enters the gap between two parallel plates (height $H$) with a uniform velocity $U$, and leaves at $x = L = 10\,H$ where $p = 0$. No slip on both plates. Steady, laminar, incompressible, 2D. Reynolds number $Re = \rho U H/\mu = 50$ and $100$. Wanted: the developing velocity field, the **entrance length** $L_e$ (where the centre-line velocity reaches 99 % of its fully developed value), and the **pressure drop**. Exact fully developed solution: $u = 6U\,(y/H)(1 - y/H)$, $u_{max} = 1.5\,U$, $dp/dx = -12\mu U/H^2$. Correlation (Durst, Ray, Ünsal, Bayoumi, *J. Fluids Eng.* 127, 2005, 1154–1160, uniform inlet, $Re$ on $H$ and the mean velocity): $L_e/H = [0.631^{1.6} + (0.0442\,Re)^{1.6}]^{1/1.6}$ = 2.3915 ($Re = 50$), 4.5422 ($Re = 100$). Read `../docs/problem.md` (the "Data for simulation software" box) and `../02_solution.pdf` for the full story.

The FDM solved it with the **projection method on a staggered (MAC) grid** (160 × 16 square cells, $h = H/16$). The central teaching point of the FDM solution is that a **collocated grid lets a checkerboard pressure hide**, and the staggered grid prevents it. The COMSOL guide must make the same point with finite elements (§3, skill 6).

---

## 1 · Goal and deliverables

Match the existing `comsol_solution/` folders of Problems 2–7 (look at `problems/07_natural_convection/comsol_solution/` first: it is the most recent and the best template, including `p7_build_guide.py`, the script that produced the guide PDF from screenshots with ReportLab). Create in this folder:

| File | What |
|---|---|
| `COMSOL_Channel_Flow_Guide.pdf` | step-by-step student guide with annotated screenshots, built like `COMSOL_Natural_Convection_Guide.pdf` (cover page with the result, the problem and the physics, the hand calculation summary, ~20 numbered COMSOL steps each with numbered callouts and a "Why?" box, results, comparison with the FDM and the exact solution, grid study, the checkerboard experiment, troubleshooting page) |
| `channel_flow_comsol.mph` | the finished model (all solutions stored, as in Problem 7), opens in COMSOL 4.3a or newer |
| exported data, e.g. `centre_line_*.txt`, `profiles_*.txt`, `pressure_line_*.txt`, `flow_rates.txt`, `checkerboard_*.txt` | the raw COMSOL exports the scripts read |
| `p10_comsol.py` | reads the exports, computes $L_e$, $dp/dx$, inlet pressure, extra pressure drop, flow rates, profile errors, writes `p10_comsol_numbers.json` |
| `p10_fig.py` | the comparison figures (`p10_centreline.png`, `p10_profiles.png`, `p10_pressure.png`, `p10_checkerboard.png`, optionally `p10_convergence.png`) |
| `p10_build_guide.py` | builds the guide PDF from the screenshots (as `p7_build_guide.py`; the raw screenshots folder `shots/` is not committed) |
| `p10_comsol_numbers.json` | every COMSOL number used in the guide and the README |
| `README.md` | replaces this file; same structure as `problems/07_natural_convection/comsol_solution/README.md`: one-paragraph summary, main figure, file table, comparison tables, "What agrees" / "What differs", a note on how to run the scripts, back link `⬅ Back to Problem 10` |

Also:

- **Link it from the problem README**: add a section `## 🔁 Cross-check with COMSOL` to `problems/10_channel_flow/README.md` just above the final back link, in the style of Problem 7's (one paragraph with the two or three headline COMSOL numbers).
- Keep `fdm_reference.json` in the folder (the scripts read it).
- **Paths:** earlier scripts (Problems 2–6) hard-coded `C:\Users\marya\Downloads\...`. New scripts must use paths relative to the script's own folder, e.g. `HERE = Path(__file__).resolve().parent` and `HERE / "centre_line_Re50.txt"`. The scripts may use NumPy and Matplotlib (only the course notebooks are restricted to plain Python).
- The course home page lists which problems have a `comsol_solution/` folder in shared text ("Problems 1 to 5 also have…"). Do **not** edit that sentence in the PR of this work unless the owner asks; mention in the PR body that it needs updating.

---

## 2 · The COMSOL 4.3a model

Dimensionless problem → unit properties, exactly as in Problems 6 and 7: $H = 1$ m, $U = 1$ m/s, $\rho = 1$ kg/m³, $\mu = 1/Re$ Pa·s. Then every SI number equals the dimensionless one in `fdm_reference.json`.

1. **Model Wizard:** 2D → *Fluid Flow > Single-Phase Flow > Laminar Flow (spf)* → *Stationary*.
2. **Global Definitions > Parameters:**

   | Name | Expression | Description |
   |---|---|---|
   | `Re` | `50` | Reynolds number (swept: 50, 100) |
   | `U0` | `1[m/s]` | inlet velocity |
   | `H` | `1[m]` | channel height |
   | `L` | `10[m]` | channel length |
   | `rho0` | `1[kg/m^3]` | density |
   | `mu0` | `rho0*U0*H/Re` | dynamic viscosity (0.02 / 0.01 Pa·s) |
   | `nx` | `160` | elements along the channel |
   | `ny` | `16` | elements across the channel |
   | `ratio` | `1` | element ratio across the channel (1 = uniform; try 4) |

   (If COMSOL objects to the name `Re`, use `Re0`. *Verify in COMSOL.*)
3. **Geometry:** one Rectangle, width `L`, height `H`, corner at (0, 0). In 4.3a the boundaries of a rectangle are usually numbered 1 = left (inlet), 2 = bottom, 3 = top, 4 = right (outlet). *Verify in COMSOL* by hovering/clicking before assigning conditions; the guide must show the numbering in a screenshot.
4. **Laminar Flow > Fluid Properties 1:** density *User defined* `rho0`; dynamic viscosity *User defined* `mu0`. Compressibility: *Incompressible flow* (check that this is selected in the Laminar Flow node; *verify in COMSOL* where 4.3a shows it).
5. **Inlet** (right-click Laminar Flow > Inlet), boundary 1: boundary condition *Velocity*, *Normal inflow velocity* `U0`. (Uniform inlet, like the FDM. Do **not** use *Laminar inflow*, which would impose a developed profile.)
6. **Outlet**, boundary 4: boundary condition *Pressure, no viscous stress*, $p_0 = 0$, **Suppress backflow** checked. *Verify in COMSOL* the exact wording of the option list in 4.3a and that the checkbox exists there.
7. **Wall 1** (default): no slip on boundaries 2 and 3.
8. **No Pressure Point Constraint.** Contrast with Problems 6 and 7: a closed cavity fixes only pressure differences, so one point needed $p = 0$; here the outlet condition fixes the pressure level. A "Why?" box should say so.
9. **Initial Values 1:** velocity field `U0` (x) and `0` (y), pressure `0`: the plug flow the FDM started from. (COMSOL's stationary solver uses Newton's method, not a time march; the initial value only helps convergence.)
10. **Mesh:** *Mapped*. *Distribution 1* on boundaries 2 and 3 (along $x$): *Fixed number of elements* `nx`. *Distribution 2* on boundaries 1 and 4 (across): number of elements `ny`, *Element ratio* `ratio`, *Distribution method: Geometric sequence*, **Symmetric distribution** checked (smallest elements at both walls). With `ratio = 1` this is the FDM grid spacing exactly (160 × 16 squares, 2560 elements; the Messages window should say so). *Verify in COMSOL* the 4.3a names of these fields and whether "element ratio" is largest/smallest or last/first element size.
11. **Study 1 > Parametric Sweep:** parameter `Re`, values `50 100` (100 then starts from the 50 solution). For the mesh study add a second sweep over `nx ny` pairs, or a separate study (see §4).
12. **Discretization** (the key experiment, §3 skill 6): the default for Laminar Flow in 4.3a is **P1+P1 with stabilisation** (as stated in Problem 6's guide). To see and change it, the discretization and stabilisation sections must be made visible in the settings window (in 4.3a: the *Show* button / eye icon in the Model Builder toolbar → *Discretization* and *Stabilization*; *verify in COMSOL*). Then the Laminar Flow node shows *Discretization of fluids* (P1+P1, P2+P1, P3+P2) and the stabilisation options (consistent: *Streamline diffusion*, *Crosswind diffusion*; inconsistent: *Isotropic diffusion*).

Solve three variants and store all their solutions in the `.mph` (e.g. three studies, or copy the physics settings per study; *verify in COMSOL* the simplest way in 4.3a, perhaps with separate Stationary studies and *Solver Configurations* duplicated, or simply solve, export, change, solve again):

| Variant | Discretization | Stabilisation | Expected |
|---|---|---|---|
| A (default) | P1+P1 | on (streamline + crosswind diffusion) | smooth, accurate to ~1 % on 160 × 16 |
| B | P1+P1 | **all off** | equal-order elements violate the inf-sup (LBB) condition: expect a **checkerboard pressure**, or a singular-matrix error / no convergence |
| C | **P2+P1** (Taylor–Hood) | off | stable, smooth pressure, most accurate |

**Variant B is the experiment that links FDM and FEM.** Equal-order linear velocity and pressure is the finite element analogue of the FDM collocated grid: the discrete equations cannot see a checkerboard pressure mode. COMSOL's default stabilisation (in the GLS family that it calls streamline diffusion) adds pressure coupling, the FEM counterpart of the staggered grid's fix; P2+P1 cures it at the root, as the staggered grid does. Whatever variant B does, document it honestly with screenshots: a checkerboard in a zoomed surface plot of $p$ near the inlet (show the mesh edges), wiggles in $p$ along a line, an error message, or (possible on this mesh, because the outlet pressure condition is natural rather than imposed node by node) a solution with only mild wiggles. If 4.3a does not let all stabilisation be switched off for Laminar Flow, say so and show the closest available setting. ***Verify in COMSOL: whether P1+P1 without stabilisation can be selected and solved in 4.3a, and what happens.*** If the mapped quad mesh does not show it clearly, try a mapped mesh split into triangles (*Convert* in the mesh sequence) as a second attempt and report both.

---

## 3 · The new COMSOL skills this guide must teach

Students already know from the guides of Problems 6 and 7: the Model Wizard, Laminar Flow, user-defined fluid properties, walls and moving walls, the pressure point constraint, parameters, a mapped mesh with a fixed number of elements, a parametric sweep (over the mesh and over $Ra$), cut lines, line integration (Nusselt number), exports and line graphs. Build this guide around what is **new**:

1. **Open boundaries.** *Inlet* (velocity) and *Outlet* (pressure, no viscous stress, suppress backflow), and why no pressure point constraint is needed. Tie to the FDM rule "where the velocity is given the pressure is free, and vice versa".
2. **Mapped mesh with a graded distribution.** *Distribution* with *Element ratio* and *Geometric sequence*, *Symmetric distribution*: small elements at the walls where the velocity gradients are largest. Compare uniform (`ratio = 1`, the FDM spacing) with graded (`ratio = 4`, `ny = 16` or `20`).
3. **Parametric sweep over Re** (the viscosity is `rho0*U0*H/Re`).
4. **2D cut lines** for profiles: the centre line $y = 0.5$ from $x = 0$ to $10$ and vertical lines at $x = 0.5, 1, 2, 4, 10$ (the last on the outlet); line graphs of $u$ along them, and *Export > Data*.
5. **Line integration** for the **flow rate** $\int_0^1 u\,dy$ at $x = 0$ (boundary 1), at $x = 10$ (boundary 4), and at interior stations $x = 1, 2, 5$ (on Cut Line 2D data sets, if *Line Integration* accepts a cut line data set in 4.3a; *verify in COMSOL*; if not, add interior boundaries by drawing the channel as several rectangles with *Form Union*, which keeps a mapped mesh per piece). And for the **pressure drop**: *Line Average* of $p$ over the inlet, *Point Evaluation* (Cut Point 2D) of $p$ at $(0, 0.5)$, and $dp/dx$ at $(9, 0.5)$ (expression `px`, *verify in COMSOL*) or from two points.
6. **Discretization and stabilisation** (§2 step 12): the checkerboard experiment. This is the key lesson linking FDM and FEM.

---

## 4 · Results to export and the comparison to make

Run on the uniform 160 × 16 mesh (the FDM spacing) for both $Re$, all three discretization variants where they solve; plus a mesh study for variants A and C at $Re = 50$ (e.g. `nx × ny` = 80 × 8, 160 × 16, 320 × 32) and one graded mesh. Exports (one file per case; name them so the script can parse them, e.g. `centre_line_Re50_A_n16.txt`):

| Export | Data set / how | Expressions |
|---|---|---|
| centre line | Cut Line 2D (0, 0.5)–(10, 0.5), *Export > Data* with a fine, regular point spacing (e.g. 1001 points; *verify in COMSOL* how 4.3a sets the resolution of a cut line export) | `x`, `u`, `p` |
| profiles | Cut Line 2D at $x = 0.5, 1, 2, 4, 10$ from $y = 0$ to $1$ | `y`, `u`, `v` |
| flow rates | Line Integration (inlet, outlet, cut lines at $x = 1, 2, 5$) | `u` |
| pressure | Point Evaluation at $(0, 0.5)$ and $(9, 0.5)$; Line Average on the inlet | `p`, `px` |
| checkerboard | for variants A, B, C: Cut Line 2D (0, 0.25)–(3, 0.25) and surface-plot screenshots of $p$ on $0 \le x \le 2$ with mesh edges | `p` |

**How to compute the numbers (in `p10_comsol.py`):**

- $L_e$: first $x$ where $u(x, 0.5) = 0.99\,u(10, 0.5)$ (linear interpolation). The FDM used the centre value of its own grid's discrete Poiseuille profile; for COMSOL the outlet value is the right counterpart (at $Re = 100$ the FDM outlet value differs from its grid value by only 0.02 %).
- $dp/dx$ downstream: from the centre-line pressure between $x = 8$ and $9.5$ (or `px` at $x = 9$).
- Inlet pressure: $p(0, 0.5)$. Extra pressure drop: $p(0, 0.5) - |dp/dx|\,L$; $K = 2 \times$ extra. Expect this number to be **mesh dependent**: the pressure is singular at the inlet corners (uniform inlet meets the wall); the FDM shows only first-order convergence for it. Say so.
- Outlet profile error: $\max |u(10, y) - 6y(1-y)|$.

**Reference values** (all in `fdm_reference.json`; FDM on $h = H/16$, $L = 10\,H$ unless noted):

| | $Re = 50$ | $Re = 100$ |
|---|:-:|:-:|
| $L_e/H$, FDM | 2.4384 | 4.6694 |
| $L_e/H$, FDM Richardson ($h = H/16$, $H/32$; $L = 5H$) | 2.4308 | – |
| $L_e/H$, Durst et al. (2005) | 2.3915 | 4.5422 |
| centre velocity at the outlet, FDM (exact 1.5) | 1.48837 | 1.48805 |
| $dp/dx$ at the outlet, FDM (exact) | −0.23814 (−0.24) | −0.11906 (−0.12) |
| $p(0, 0.5)$, FDM | 2.6139 | 1.4613 |
| extra pressure drop, FDM ($K$) | 0.2325 (0.465) | 0.2707 (0.541) |
| extra pressure drop, FDM Richardson ($Re = 50$, $L = 5H$; first order only) | 0.2202 | – |
| flow rate at $x = 0, 1, 2, 5, 10$, FDM | 1.00000000 | 1.00000000 |
| largest outlet-profile error vs Poiseuille, FDM | 0.0058 | 0.0061 |

`fdm_reference.json` also has the FDM centre-line velocity and pressure at $x = 0 \dots 10$, the profiles $u(y)$ at $x = 0.5, 1, 2, 4, 10$ (at $y = (j - \tfrac12)/16$), and the FDM grid study ($h = H/8, H/16, H/32$ at $Re = 50$ with observed orders).

**Tables for the guide and the README:**

1. *Entrance length:* COMSOL A / C (160 × 16, finest mesh, graded mesh) vs FDM vs FDM Richardson vs Durst, both $Re$.
2. *Pressure:* $dp/dx$ (vs −12/Re), $p(0, 0.5)$, extra drop, for COMSOL A / C vs FDM.
3. *Mass conservation:* flow rate at the five stations for COMSOL A and C (finite elements conserve mass only weakly: expect small deviations, especially for P1+P1 with stabilisation; the FDM conserves it to 8 decimals per cell). This is a genuine FDM/FEM difference worth a "What differs" bullet.
4. *Outlet profile:* max deviation from Poiseuille.
5. *Checkerboard:* for A, B, C: a qualitative row (smooth / checkerboard / failed) plus the amplitude of the pressure wiggle along $y = 0.25$ (e.g. max |second difference| between neighbouring nodes).

**Figures:** `p10_centreline.png` ($u(x, 0.5)$: COMSOL A and C, FDM, Durst markers, both $Re$), `p10_profiles.png` (COMSOL vs FDM vs exact at the five stations), `p10_pressure.png` (centre-line $p(x)$ with the fully developed line), `p10_checkerboard.png` (the three pressure fields near the inlet, mesh edges visible), optionally `p10_convergence.png` (mesh study of $L_e$ and $dp/dx$).

---

## 5 · Not verified (check in COMSOL 4.3a, and correct this plan where needed)

- Boundary numbering of the rectangle (1 left, 2 bottom, 3 top, 4 right is assumed).
- Whether the parameter name `Re` is accepted.
- The exact option names: *Inlet > Velocity > Normal inflow velocity*; *Outlet > Pressure, no viscous stress*; the *Suppress backflow* checkbox; the *Compressibility* setting.
- How to show the *Discretization* and *Stabilization* sections in 4.3a (Show/eye menu), the names of the discretization choices (P1+P1, P2+P1, P3+P2) and of the stabilisation checkboxes.
- **Whether all stabilisation can be switched off for P1+P1 Laminar Flow in 4.3a, and what then happens** (checkerboard, singular matrix, or a mild effect). The guide must report what actually happens.
- The *Distribution* fields of a mapped mesh: *Element ratio*, *Distribution method: Geometric sequence*, *Symmetric distribution*, and which way the ratio goes.
- Whether *Line Integration* (and *Line Average*) can use a *Cut Line 2D* data set; otherwise use interior boundaries.
- Whether `px` is available as the pressure derivative in a Point Evaluation.
- How to set the number of points of a cut-line *Export > Data*.
- Storing several solutions (variants A, B, C and the sweeps) in one `.mph` in the simplest way.

The FDM numbers are verified (the notebook was run top to bottom; see `../03_fdm_solver.ipynb`). Durst et al.'s correlation is quoted as the 1.6-power blend with the constants 0.631 and 0.0442 that later papers attribute to Durst et al. (2005); the original paper could not be opened from the session that wrote this file, so if a copy is at hand, check the formula and that $Re$ there is based on the full gap $H$ and the mean velocity.
