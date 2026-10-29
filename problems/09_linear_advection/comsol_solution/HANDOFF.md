# Problem 9 · Handoff for the COMSOL desktop session

This file is a work order for a later session on the owner's Windows PC with **COMSOL Multiphysics 4.3a**. It contains everything needed to build the COMSOL model and the student guide of Problem 9 without any other context. **No COMSOL result exists yet**: every number below comes from the plain-Python finite difference notebook or from plain-Python finite element *expectations*, never from COMSOL. When the work is done, replace this file by a `README.md` (see section 1) and delete `HANDOFF.md`.

Read first, in this folder's parent (`problems/09_linear_advection/`):

- `docs/problem.md` (the problem statement; its *Data for simulation software* box is the short version of section 2 below);
- `docs/solution.md` and `03_fdm_solver.ipynb` (the finite difference solution: FTCS, upwind, Lax–Wendroff, CFL, von Neumann, modified equation);
- the existing COMSOL folders for the style to copy: `problems/05_convection_diffusion/comsol_solution/` (closest in content: stabilisation on/off) and `problems/02_phosphorus_diffusion/comsol_solution/` (closest in setup: 1D, time-dependent).

---

## 1 · Goal and deliverables

**Goal.** Solve the same advection problem with the finite element method in COMSOL 4.3a, write a step-by-step student guide around the **new COMSOL skills** of section 3, and compare COMSOL's peak and error after one lap with the finite difference schemes and the exact solution.

**Deliverables in `problems/09_linear_advection/comsol_solution/`** (same pattern as Problems 2 to 5):

| File | Content |
|---|---|
| `COMSOL_Advection_Pulse_Guide.pdf` | step-by-step guide for students with **annotated screenshots** of every step (about 20 to 30 pages, like `COMSOL_Convection_Diffusion_Guide.pdf`): short theory recap, building the model, the solver experiments of section 3, the comparison with the notebook, conclusions |
| `advection_pulse.mph` | the finished model (save it with the recommended settings of section 2.8, solution included or cleared to keep the file small) |
| `profiles_*.txt` | exported data (section 4.1), one file per experiment, with a short header naming the settings |
| `p9_analysis.py` | reads the exports, computes peak and largest error after one lap, writes `p9_comsol.json` |
| `p9_fig.py` | draws the comparison figures (section 4.3) as PNG files for the guide and the README |
| `p9_comsol.json` | the COMSOL numbers behind the tables |
| `fdm_reference.py`, `fdm_reference.json` | already here: the finite difference reference and finite element expectations (do not edit the numbers by hand; rerun the script if needed) |
| `README.md` | replaces this file: what the folder contains, the main figure, the comparison tables, a note on how to run the scripts (copy the layout of `problems/05_convection_diffusion/comsol_solution/README.md`) |

Also:

- add a section **"🔁 Cross-check with COMSOL"** to `problems/09_linear_advection/README.md`, before *Run it* or after it as in Problems 5 and 7, with a link to `comsol_solution/` and two or three key numbers;
- on the course home page `README.md`, add 9 to the list of problems in the "Cross-check with commercial software" tip (check first whether the coordinating session already changed that sentence).

**Scripts: paths relative to the script's own folder.** The earlier COMSOL scripts hard-coded `C:\Users\marya\Downloads\...` (their READMEs carry a note about it). New scripts must not: start every script with

```python
from pathlib import Path
HERE = Path(__file__).resolve().parent    # read and write files next to this script
```

and open every file as `HERE / "profiles_N100_C05_BDF.txt"` etc. `fdm_reference.py` already does this. The analysis scripts may use NumPy and Matplotlib (they are not course solvers), but keep them short and readable.

---

## 2 · COMSOL 4.3a model specification

Items marked **(verify in COMSOL)** could not be checked without COMSOL; menu names are from memory of the 4.3/4.3a interface. Correct them in the guide if they differ, and mention the real names.

### 2.1 Model Wizard

- Space dimension: **1D**.
- Physics: **Mathematics → PDE Interfaces → Coefficient Form PDE (c)**. Dependent variable `u`, 1 component. Leave the units of the dependent variable and of the source term dimensionless **(verify in COMSOL: 4.3a may not have unit fields on this page at all; then the variable is dimensionless by default)**.
- Study: **Preset Studies → Time Dependent**.

### 2.2 Global Definitions

**Parameters** (Global Definitions → Parameters):

| Name | Expression | Description |
|---|---|---|
| `L0` | `1[m]` | length of the loop |
| `c0` | `1[m/s]` | flow speed |
| `x0` | `0.5[m]` | centre of the pulses |
| `sig` | `0.05[m]` | standard deviation of the Gaussian |
| `Nel` | `100` | number of mesh elements |
| `CFL` | `0.5` | Courant number |
| `dt` | `CFL*L0/Nel/c0` | time step, 0.005 s for `CFL = 0.5` |

**Functions** (Global Definitions → Functions). This is one of the skills to teach (section 3):

1. **Gaussian Pulse** `gp1`: *Location* `x0`, *Standard deviation* `sig`. COMSOL's Gaussian pulse is normalised to **area 1**, so its peak is $1/(\sigma\sqrt{2\pi}) = 7.979$. The initial value must have height 1: use `u = sig*sqrt(2*pi)*gp1(x)` (factor 0.12533). Plot the function (Plot button in its settings) to show the class the peak before and after scaling. **(verify in COMSOL: the normalisation of Gaussian Pulse in 4.3a; if it already has peak 1, drop the factor.)**
2. **Square pulse**, two ways (show both, use one):
   - **Rectangle** `rect1`: *Lower limit* `0.4`, *Upper limit* `0.6`, smoothing *Size of transition zone* `0.01` (one element). **(verify in COMSOL: Rectangle exists in 4.3a and its argument is dimensionless; if the argument must be dimensionless, call it as `rect1(x/1[m])`.)**
   - or the difference of two **Step** functions, `step1(x - 0.4[m]) - step1(x - 0.6[m])`, with *Location* 0, *From* 0, *To* 1 and a smoothing zone of 0.01. **(verify in COMSOL: unit handling of the argument.)**

   The finite difference notebook uses a *sharp* square pulse at the nodes (21 nodes equal to 1, from 0.40 to 0.60 m inclusive). A smoothing zone of one element changes the initial values only at the two edge nodes; mention this when comparing.
3. Optional, for the comparison: an **Analytic** function `an1(xx) = exp(-(xx - 0.5)^2/(2*0.05^2))` with dimensionless argument, which reproduces the notebook's Gaussian exactly.

### 2.3 Geometry

**Interval** from 0 to `L0`. Build All. The two end points are Points 1 ($x = 0$) and 2 ($x = L$).

### 2.4 Coefficient Form PDE

COMSOL's equation (shown at the top of the settings window):

$$e_a\,\frac{\partial^2 u}{\partial t^2} + d_a\,\frac{\partial u}{\partial t} + \nabla\cdot\left(-c\,\nabla u - \alpha\,u + \gamma\right) + \beta\cdot\nabla u + a\,u = f$$

Set, in the **Coefficient Form PDE 1** domain node:

| COMSOL coefficient | Value | Default | Meaning here |
|---|:-:|:-:|---|
| diffusion coefficient $c$ | **0** | 1 | no diffusion (do not confuse COMSOL's $c$ with the flow speed!) |
| absorption $a$ | 0 | 0 | |
| source $f$ | **0** | 1 | no source |
| mass $e_a$ | 0 | 0 | |
| damping/mass $d_a$ | **1** | 1 | coefficient of $\partial u/\partial t$ |
| conservative flux convection $\alpha$ | 0 | 0 | |
| conservative flux source $\gamma$ | 0 | 0 | |
| convection $\beta$ | **`c0`** | 0 | the flow speed, 1 m/s |

(Units: COMSOL may colour some fields orange for inconsistent units because `u` is dimensionless; this is harmless. If it bothers students, write `1` instead of `c0`. **(verify in COMSOL)**)

**Initial Values 1:** `u = sig*sqrt(2*pi)*gp1(x)` (Gaussian) or `u = rect1(x)` (square pulse). Leave $\partial u/\partial t$ at 0 (unused because $e_a = 0$).

**Periodic Condition:** right-click Coefficient Form PDE 1 → **Periodic Condition**, select **both points 1 and 2**. This replaces the default *Zero Flux 1* on those points (Zero Flux stays in the tree, overridden). **(verify in COMSOL: in 1D the periodic condition is applied to both points in one node; in 4.3a the node may be under the boundary-condition submenu as "Periodic Condition"; there may also be a "Destination Selection" subnode: leave it at default.)** A check that it works: plot $u$ at $t = 0.5$ s; the Gaussian must appear split between $x = 0$ and $x = 1$.

**Discretization** (settings of the Coefficient Form PDE interface node, section *Discretization*; may need **View → Show → Discretization**, the "eye" button in the Model Builder toolbar **(verify in COMSOL)**): *Element order*: **Lagrange, Linear** to compare with the finite difference grid (one node per FDM node); the default is **Quadratic**.

**Stabilization** (same interface node, section *Stabilization*, shown after **Show → Stabilization** **(verify in COMSOL)**): *Consistent stabilization*: **Streamline diffusion** and *Crosswind diffusion* check boxes; *Inconsistent stabilization*: *Isotropic diffusion*. Record the defaults you find in 4.3a (Problem 5's guide found streamline diffusion **on** by default in Transport of Diluted Species; check whether the Coefficient Form PDE has it on too).

### 2.5 Mesh

User-controlled mesh → **Edge 1** (or *Size* + *Distribution*): **Distribution**, *Fixed number of elements* `Nel` (100), uniform. For the grid study set `Nel` to 25, 50, 100, 200, 400, 800, 1600 (a Parametric Sweep over `Nel`, as in Problem 5, or by hand). The mesh vertices then sit exactly on the finite difference nodes $x_i = i\,\Delta x$ (COMSOL also stores $x = 1$, which equals $x = 0$).

### 2.6 Study: times and solver settings

**Study 1 → Step 1: Time Dependent:** *Times* `range(0, dt, 1)` (201 output times for `CFL = 0.5`). Relative tolerance: default 0.01; record it, it matters for BDF (section 3).

**Solver** (Study 1 → right-click → *Show Default Solver*, then **Solver Configurations → Solution 1 → Time-Dependent Solver 1**, section **Time Stepping**) **(verify in COMSOL: names of every field below)**:

| Setting | Values to use | Purpose |
|---|---|---|
| *Method* | **BDF** (default) / **Generalized alpha** | the time integrator |
| *Steps taken by solver* | **Free** (default) / **Intermediate** / **Strict** (and **Manual** if 4.3a offers it) | Strict forces a step at every output time; with output every `dt`, and *Maximum step* `dt`, every step is exactly `dt` |
| *Initial step* | `dt` | first step = notebook step |
| *Maximum step constraint* / *Maximum step* | *Constant*, `dt` | no step larger than the notebook's |
| *Maximum BDF order* | 5 (default) / **2** / **1** | order 1 = implicit Euler; compare with the expectations in `fdm_reference.json` |
| *Amplification for high frequency* (generalized alpha, $\rho_\infty$) | 0.75 (default) / **1** | $\rho_\infty = 1$: no numerical damping (like the trapezoidal rule) |

If 4.3a has a **Manual** option with a *Time step* field, use it with `dt` (this is the cleanest way to force fixed steps). If it has no Manual option, use **Strict** + initial step + maximum step as above, and verify the steps taken in the solver log (*Log* window: the number of time steps should be `1/dt`).

### 2.7 Results to set up

- **1D Plot Group: Line Graph** of `u` at $t = 0$ and $t = 1$ s, with the exact solution (`sig*sqrt(2*pi)*gp1(x)` at $t = 1$ s, since one lap brings the pulse back) as a second Line Graph.
- **Maximum** coupling operator: **Definitions → Model Couplings → Maximum** (`maxop1`), on Domain 1 **(verify in COMSOL: in 4.3a it may be "Component Couplings" or "Model Couplings"; in 1D the domain is the interval)**. Then **Derived Values → Global Evaluation** of `maxop1(u)` (peak) and `maxop1(abs(u - sig*sqrt(2*pi)*gp1(x)))` (largest error, only meaningful at $t = 1$ s) at the last time. Use `maxop1(-u)` for the most negative value.
- Optional **animation** of `u(x, t)` over one lap with a periodic wrap (Results → Export → Animation), like the heating-rod animation on the course home page.

### 2.8 Recommended final state of the saved model

Linear elements, 100 elements, stabilisation **off**, **Generalized alpha** with $\rho_\infty = 1$, fixed step `dt = 0.005` s, Gaussian initial value. The other settings are experiments in the guide (save extra copies only if useful; one `.mph` is enough).

---

## 3 · The new COMSOL skills this problem must teach

Build the guide around these skills (each one a numbered step with screenshots), in this order:

1. **Writing your own PDE with the Coefficient Form PDE interface.** Until now every problem used a ready-made physics interface (Heat Transfer, Transport of Diluted Species, Laminar Flow). Here students type the coefficients themselves: match COMSOL's general equation term by term with $u_t + c\,u_x = 0$ and set $d_a = 1$, $\beta = c$, everything else 0 (watch out: COMSOL's $c$ is a diffusion coefficient and its default is 1, its default source $f$ is 1).
2. **Periodic condition.** No inlet and no outlet: the two end points are the same point of the loop. Show what happens with the default Zero Flux alone (the pulse leaves and does not come back) and with the Periodic Condition.
3. **Functions.** Define the initial value with Global Definitions → Functions: Gaussian Pulse (and its area-1 normalisation, so the factor $\sigma\sqrt{2\pi}$), Rectangle or Step with a smoothing zone, Analytic. Plot each function before using it.
4. **Time-dependent solver settings.**
   - BDF (default) versus Generalized alpha; the BDF order (1 = implicit Euler, 2, up to 5); $\rho_\infty$ of generalized alpha.
   - Forcing fixed steps ("Steps taken by solver: Strict" with initial and maximum step `dt`, or Manual) so that $\Delta t$ matches the notebook's Courant number, $\Delta t = C\,\Delta x/c$ (0.005 s at $C = 0.5$, 0.01 s at $C = 1$).
   - Reading the solver log to check the number of steps actually taken.
   - With the default *Free* steps and relative tolerance 0.01, record how many steps BDF takes and what peak it returns; then tighten the tolerance (0.001, 0.0001) and see the peak improve.
5. **Element order.** Linear versus quadratic Lagrange elements on the same mesh (quadratic has twice as many nodes).
6. **Consistent stabilisation (streamline diffusion) on/off.** As in Problem 5, but now in time: stabilisation adds diffusion along the flow, like upwinding.

**The key lesson.** An implicit time integrator is **stable for any time step** (no CFL limit, unlike the explicit schemes of the notebook), but it is **not exact**: COMSOL's default BDF **damps the pulse even with stabilisation switched off**, because the time integrator itself adds numerical diffusion, just as upwinding does in space. The plain-Python expectations in `fdm_reference.json` make this concrete: with linear elements, no stabilisation and a fixed step $\Delta t = 0.005$ s on 100 elements, implicit Euler (BDF order 1) should return the Gaussian with a peak of about **0.578**, the same as first-order upwind (0.577): its time error is a diffusion $c^2\Delta t/2 = 0.0025$ m²/s, exactly the $D_{num}$ of upwind at $C = 0.5$. BDF2 should give about 0.973 and the trapezoidal rule (generalized alpha with $\rho_\infty = 1$ should be close) about 0.998, with dispersive wiggles behind the square pulse instead (minimum about −0.26). Whether COMSOL's adaptive variable-order BDF lands near the order-1 or order-2 value is exactly what the student should measure. A second lesson for the guide: an implicit solver happily runs at $C = 1.1$ or $C = 5$ without blowing up, but the answer gets more and more damped. Stability is not accuracy.

---

## 4 · Results to export and comparisons to make

### 4.1 Experiments and exports

Run the Gaussian pulse for every experiment; the square pulse for experiments A, B, D and F at least. Export $u$ at $t = 1$ s on the mesh nodes (Results → Export → Data, *Points to evaluate in*: **Node points** for linear elements, or a regular grid of 101 points $x = 0, 0.01, \dots, 1$ **(verify in COMSOL: option names)**). Name each file `profiles_<experiment>_<pulse>.txt`, e.g. `profiles_A_gauss.txt`, and write the settings in the first line.

| ID | Elements | Order | Stabilisation | Time stepping | $\Delta t$ |
|:-:|:-:|---|---|---|:-:|
| A | 100 | linear | defaults of 4.3a (record them) | BDF, Free, default tolerance 0.01 | solver's choice (record the number of steps) |
| B | 100 | linear | **off** | BDF, Free, tolerance 0.01 | solver's choice |
| B2 | 100 | linear | off | BDF, Free, tolerance 0.001 and 0.0001 | solver's choice |
| C1 | 100 | linear | off | BDF, **max order 1**, fixed step | 0.005 s ($C = 0.5$) |
| C2 | 100 | linear | off | BDF, **max order 2**, fixed step | 0.005 s |
| D | 100 | linear | off | **Generalized alpha**, $\rho_\infty = 1$, fixed step | 0.005 s |
| D2 | 100 | linear | off | Generalized alpha, $\rho_\infty = 0.75$ (default), fixed step | 0.005 s |
| E | 100 | linear | off | Generalized alpha, $\rho_\infty = 1$, fixed step | 0.01 s ($C = 1$) and 0.011 s ($C = 1.1$, up to $t = 1.001$ s) |
| F | 100 | linear | **on** (streamline diffusion) | Generalized alpha, $\rho_\infty = 1$, fixed step | 0.005 s |
| G | 100 | **quadratic** | off | Generalized alpha, $\rho_\infty = 1$, fixed step | 0.005 s |
| H | 25 … 1600 | linear | off | Generalized alpha, $\rho_\infty = 1$, fixed step | $0.5\,\Delta x$ ($C = 0.5$) |

### 4.2 Tables for the guide and the README

**Table 1 · Peak and largest error of the Gaussian after one lap, 100 elements / intervals, $\Delta t = 0.005$ s.** Fill the COMSOL rows; the reference rows are from `fdm_reference.json`:

| Method | peak | min | largest error |
|---|:-:|:-:|:-:|
| exact | 1.000 | 0.000 | 0 |
| FDM upwind, $C = 0.5$ | 0.5770 | 0.0000 | 0.423 |
| FDM Lax–Wendroff, $C = 0.5$ | 0.9639 | −0.0307 | 0.129 |
| FDM upwind and Lax–Wendroff, $C = 1$ | 1.0000 | 0.0000 | 7 × 10⁻¹⁶ |
| FDM FTCS, $C = 0.5$ | blows up: 65.8 | −69.7 | 69.7 |
| *expected* FEM linear + implicit Euler, $\Delta t = 0.005$ | *0.5776* | *0.0000* | *0.422* |
| *expected* FEM linear + BDF2, $\Delta t = 0.005$ | *0.9726* | *−0.0092* | *0.086* |
| *expected* FEM linear + trapezoidal, $\Delta t = 0.005$ | *0.9977* | *−0.0000* | *0.024* |
| COMSOL A … H | | | |

**Table 2 · Square pulse after one lap** (same layout): FDM upwind peak 0.8626, min 0.0000, error 0.474; FDM Lax–Wendroff peak 1.223, min −0.221, error 0.596; *expected* FEM + implicit Euler 0.880 / −0.006 / 0.468, + BDF2 1.251 / −0.229 / 0.566, + trapezoidal 1.334 / −0.256 / 0.660. COMSOL: where are its wiggles, in front of or behind the pulse? (Lax–Wendroff: behind.)

**Table 3 · Courant number** (experiment E vs the notebook): FDM at $C = 1.1$: upwind Gaussian peak 1.274 (error 0.279), Lax–Wendroff 1.007 (error 0.041), square pulse $1.2 \times 10^6$ and $3 \times 10^{12}$ (blown up). COMSOL with an implicit integrator should stay bounded: show it.

**Table 4 · Grid study** (experiment H vs `error_study_gaussian_C0.5` in the JSON): largest error and peak against $N$. FDM: upwind order → 1 (0.88 at the finest pair), Lax–Wendroff order 2.0. Report COMSOL's observed order.

All numbers of the notebook (README of Problem 9): upwind peak 0.577 (modified equation 0.577), Lax–Wendroff 0.964 for the Gaussian; 0.863 and 1.223 for the square pulse; both exact at $C = 1$, both unstable at $C = 1.1$.

### 4.3 Figures

1. `p9_lap.png`: Gaussian and square pulse after one lap (two panels, $x$ from 0.2 to 0.8 m): exact, FDM upwind, FDM Lax–Wendroff, COMSOL B (default BDF, stabilisation off) and COMSOL D (generalized alpha, $\rho_\infty = 1$). This is the main figure for the README.
2. `p9_integrators.png`: Gaussian peak after one lap for every COMSOL experiment as a bar chart, with horizontal lines for exact (1), FDM upwind (0.577) and FDM Lax–Wendroff (0.964).
3. `p9_convergence.png`: largest error against $\Delta x$ (log–log) for FDM upwind, FDM Lax–Wendroff and COMSOL H, with slope-1 and slope-2 guide lines (copy the style of `../plots.py`, function `convergence`: colours `#2a78d6` blue, `#eb6834` orange, ink `#1f2328`).
4. Screenshots for every step of the guide (Model Builder tree, settings windows, plots), annotated like the earlier guides.

---

## 5 · Not verified here (check in COMSOL 4.3a and correct the guide)

- Exact menu paths and names: *Mathematics → PDE Interfaces → Coefficient Form PDE*; *Periodic Condition* in 1D (both points in one node, any *Destination Selection* subnode); *View/Show → Discretization* and *Show → Stabilization*; *Definitions → Model Couplings → Maximum* (or *Component Couplings*).
- Defaults of the Coefficient Form PDE in 4.3a: $c = 1$, $f = 1$, $d_a = 1$ (as assumed above); default element order (assumed quadratic); whether streamline diffusion is **on** by default for this interface.
- The **Gaussian Pulse** normalisation (assumed area 1, peak $1/(\sigma\sqrt{2\pi})$) and the parameter names *Location*, *Standard deviation*; whether **Rectangle** exists in 4.3a and how it handles the unit of its argument.
- Time-stepping options: whether *Steps taken by solver* offers **Manual** in 4.3a or only Free / Intermediate / Strict; the names *Initial step*, *Maximum step*, *Maximum BDF order*, *Amplification for high frequency*; where the number of steps taken appears in the log.
- Export option names (*Points to evaluate in: Node points*).
- Whether COMSOL integrates the linear-element mass matrix exactly (consistent mass matrix $h/6\,(1, 4, 1)$, as assumed in the expectations of `fdm_reference.json`). If experiment C1 with forced steps does not match the expected 0.578 to 3 decimals, check the steps taken and the BDF order first.

Rerun `python fdm_reference.py` in this folder to regenerate `fdm_reference.json` (plain Python, a few seconds).
