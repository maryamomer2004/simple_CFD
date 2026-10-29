# Problem 8 · COMSOL solution · handoff for the desktop session

This file is a work order for a later session on the owner's Windows PC with **COMSOL Multiphysics 4.3a**. It contains everything needed to build the COMSOL model of Problem 8, the student guide and the comparison with the finite difference notebook, without any other context. When the work is done, **replace this file by `README.md`** (see §1) and delete `HANDOFF.md`.

Nothing in this folder has been made with COMSOL yet. All numbers below come from `../03_fdm_solver.ipynb` (plain-Python FDM) and from the exact solution, and are stored in [`fdm_reference.json`](fdm_reference.json), which the notebook writes in its last cell.

---

## 0 · The problem in one paragraph

A long steel billet with a **100 mm × 100 mm** square cross-section leaves a furnace at a uniform **600 °C** and is cooled on **all four sides** by a water-mist spray at **30 °C** with **h = 1000 W/(m²·K)**. Steel: **k = 48.0 W/(m·K), ρ = 7854 kg/m³, c_p = 559 J/(kg·K)** (plain carbon steel at 600 K, Incropera et al., Table A.1; constant properties). Find T(x, y, t) and the time at which the centre reaches **100 °C**. 2D, unsteady heat conduction; by symmetry one **quarter** (0 ≤ x, y ≤ L = 0.05 m, centre of the billet at the origin) is modelled, with symmetry on x = 0 and y = 0 and convection on x = L and y = L.

Key facts (from the notebook):

| quantity | value |
|---|---|
| thermal diffusivity α = k/(ρc_p) | 1.0933e-5 m²/s |
| Biot number Bi = hL/k (half-width) | 1.0417 |
| Biot number for lumped capacitance, h(V/A)/k, V/A = L/2 | 0.521 (> 0.1: lumped capacitance fails) |
| **exact time for the centre to reach 100 °C** | **349.14 s** |
| lumped capacitance prediction | 230.18 s (−34 %) |
| FTCS, 11 × 11 nodes, Δt = 0.5 s | 348.57 s |
| ADI, 11 × 11 nodes, Δt = 10 s | 349.15 s |
| at t = 349.14 s: middle of a face (L, 0) / corner (L, L) | 74.97 °C / 58.89 °C |

Exact solution: θ* = (T − T∞)/(Tᵢ − T∞) = P(x, t)·P(y, t), with P(x, t) = Σ Cₙ exp(−ζₙ² Fo) cos(ζₙ x/L), Fo = αt/L², Cₙ = 4 sin ζₙ/(2ζₙ + sin 2ζₙ), ζₙ tan ζₙ = Bi. First roots: ζ₁ = 0.873168, ζ₂ = 3.435952, ζ₃ = 6.443461; C₁ = 1.122485, C₂ = −0.156251, C₃ = 0.048353 (all six stored in the JSON). 50 terms are more than enough for t > 0.

---

## 1 · Goal and deliverables

Produce the same kind of `comsol_solution/` folder as Problems 2 to 5 (see `../../04_brick_column_convection/comsol_solution/` and `../../02_phosphorus_diffusion/comsol_solution/` for the format, and `../../06_lid_driven_cavity/comsol_solution/p6_build_guide.py` for how the guide PDF was assembled from annotated screenshots with ReportLab):

| file | content |
|---|---|
| `COMSOL_Billet_Cooling_Guide.pdf` | step-by-step guide for students with annotated screenshots (about 25 pages, like the Problem 2 and 4 guides): cover, problem page, a short theory page (Biot number, symmetry, explicit vs implicit time stepping, BDF), then numbered COMSOL steps built around the **new skills of §3**, a results/comparison page and a "what can go wrong" page |
| `billet_cooling_comsol.mph` | the finished model (user-defined material, quarter geometry, probes, mesh, study), saved in COMSOL 4.3a. Optionally a second file `billet_cooling_comsol_extensions.mph` for the extensions of §3.6 |
| exported data (`.txt`) | `billet_points.txt` (T at the three points against time), `billet_profiles.txt` (T along y = 0 at 30, 120, 300, 600 s), `billet_mesh_study.txt`, `billet_solver_steps.txt`, `billet_material.txt` (see §4) |
| `billet_cooling.gif` (or `.avi`) | the exported animation of the temperature field, 0 to 600 s |
| `p8_analysis.py` | reads the exported COMSOL data and `fdm_reference.json`, computes the comparison numbers and writes `p8_comsol_numbers.json` |
| `p8_fig.py` | draws the comparison figures (`p8_comparison.png`, `p8_steps.png`, optionally `p8_material.png`) |
| `p8_build_guide.py` | (optional, if the guide is built like Problem 6's) assembles the guide PDF |
| `p8_comsol_numbers.json` | the COMSOL numbers behind the README table |
| `README.md` | replaces this file; same structure as `../../04_brick_column_convection/comsol_solution/README.md`: one-paragraph intro, the main comparison figure, a file table, the key comparison table, a short conclusion, and a back link `⬅ Back to Problem 8` |

Also:

- Add one sentence + link to `../README.md` (the Problem 8 README), as in Problem 4's README: *"The same billet is also solved with the finite element method in COMSOL Multiphysics 4.3a: see [`comsol_solution/`](comsol_solution) for the model file and a step-by-step guide for students. …"* (with the headline COMSOL number).
- The course home page (`../../../README.md`) lists which problems have a `comsol_solution/` folder ("Problems 1 to 5 also have…"). Update that sentence only if no other session is editing the home page at the same time; otherwise leave it for the coordinating session and say so in the PR.
- **Paths in scripts:** the earlier scripts hard-coded `C:\Users\marya\Downloads\...`. New scripts must find their files relative to their own folder:

  ```python
  from pathlib import Path
  HERE = Path(__file__).resolve().parent
  REF = json.loads((HERE / "fdm_reference.json").read_text(encoding="utf-8"))
  ```

  The analysis and figure scripts may use NumPy and Matplotlib (only the notebook solvers are restricted to plain Python).
- Keep `fdm_reference.json` in the folder (the scripts read it). If the notebook is changed, re-run it: its last cell rewrites the JSON.

---

## 2 · The COMSOL 4.3a model

Names of menus and settings are given as remembered for COMSOL 4.3a; everything marked **(verify in COMSOL)** must be checked on screen and corrected in the guide if it differs.

### 2.1 Model Wizard

1. **New** → Model Wizard → Space dimension **2D**.
2. Add physics: **Heat Transfer → Heat Transfer in Solids (ht)**.
3. Study: **Preset Studies → Time Dependent**. Finish.

### 2.2 Parameters (Global Definitions → Parameters)

| name | expression | description |
|---|---|---|
| `L` | `0.05[m]` | half-width of the billet |
| `T_init` | `600[degC]` | initial temperature |
| `T_inf` | `30[degC]` | fluid temperature |
| `h_conv` | `1000[W/(m^2*K)]` | convection coefficient |
| `k_s` | `48[W/(m*K)]` | conductivity (Incropera A.1, 600 K) |
| `rho_s` | `7854[kg/m^3]` | density |
| `cp_s` | `559[J/(kg*K)]` | specific heat |
| `n_el` | `10` | elements per side (for the mesh study) |

(`degC` is accepted as a unit in 4.3a; the model works internally in K: 600 °C = 873.15 K, 30 °C = 303.15 K. **(verify in COMSOL** that `[degC]` converts as an absolute temperature in Initial Values and External temperature; if not, use `873.15[K]` and `303.15[K]`.)

### 2.3 Geometry

- **Square** (or Rectangle), side `L`, base **Corner**, position (0, 0). Build All.
- Boundary numbers in 4.3a for a square are usually 1 = left (x = 0), 2 = bottom (y = 0), 3 = top (y = L), 4 = right (x = L) **(verify in COMSOL)**; points 1 = (0, 0), 2 = (0, L), 3 = (L, 0), 4 = (L, L) **(verify)**.
- Teaching point for the guide: show the full 2L × 2L square first, then explain why the quarter is enough (symmetry of geometry, initial condition and boundary conditions), and that it cuts the number of unknowns by four.

### 2.4 Material: user-defined first, then the Material Library

1. **Materials → Material** (a blank material), name it `Steel (Problem 8 data)`. In *Material Contents* fill in **Thermal conductivity** `k_s`, **Density** `rho_s`, **Heat capacity at constant pressure** `cp_s` (the rows marked with a red/green flag are the ones Heat Transfer in Solids needs). This is the material used for every comparison with the notebook.
2. **Material Library skill** (see §3.1): open **Add Material** (right-click Materials → *Open Material Browser*, or the Add Material window) and look at the steels:
   - **Built-In** library: `Structural steel` and `Steel AISI 4340`. In 4.3a both are expected to have k = 44.5 W/(m·K), ρ = 7850 kg/m³, c_p = 475 J/(kg·K) **(verify in COMSOL** and write the actual values in the guide).
   - **Material Library** (a separately licensed add-on with temperature-dependent data; **verify whether it is installed**): if available, pick a plain carbon steel (for example AISI 1010 or 1020) and show its k(T) and c_p(T) curves (in the material node, the function plot buttons).
3. Swap the material of the domain (Domain 1) to the library steel, re-run, and record how much the answer changes (§4.5). Then switch back to `Steel (Problem 8 data)` for all other results.

**Predicted effect** (exact solution, constant properties): with k = 44.5, ρ = 7850, c_p = 475, α = 1.193e-5 m²/s and Bi = 1.124, the centre reaches 100 °C after **304.5 s** instead of 349.1 s (−13 %), and T_centre(300 s) = **102.47 °C** instead of 127.14 °C. With the 300 K values of plain carbon steel (k = 60.5, c_p = 434) it would be 251.9 s (−28 %). A temperature-dependent library steel cannot be checked against this exact solution; compare it with the constant-property COMSOL run instead. Teaching point: the material data matter more than the mesh.

### 2.5 Physics: Heat Transfer in Solids

| node | selection | settings |
|---|---|---|
| Heat Transfer in Solids 1 | domain 1 | thermal conductivity, density, heat capacity **From material** |
| Initial Values 1 | domain 1 | Temperature `T_init` |
| Thermal Insulation 1 (default) | all boundaries until overridden | — |
| **Symmetry 1** (new) | x = 0 and y = 0 | no settings. In heat transfer, symmetry = zero normal heat flux, i.e. the same equation as Thermal Insulation; use the Symmetry node anyway, because it states the modelling intent **(verify in COMSOL** that ht in 4.3a offers a *Symmetry* boundary condition; if not, keep Thermal Insulation and explain) |
| **Heat Flux 1** | x = L and y = L | select **Convective heat flux**; Heat transfer coefficient *User defined* `h_conv`; External temperature `T_inf` **(verify** the exact labels in 4.3a: it may also be offered as a separate *Convective Heat Flux* node) |

The Problem 4 COMSOL guide (`../../04_brick_column_convection/comsol_solution/COMSOL_Brick_Column_Guide.pdf`) already shows the convective heat flux dialog in 4.3a: reuse its wording.

### 2.6 Mesh

- **Mapped** mesh with a **Distribution** of `n_el` elements on one horizontal and one vertical boundary (or on all four). Main mesh: **10 × 10** quadrilaterals (element size 5 mm, the same spacing as the notebook's N = 10 grid).
- **Mesh study:** n_el = 5, 10, 20, 40 (and 80 if fast). Use a **Parametric Sweep** over `n_el` in the study, or re-mesh by hand.
- **Element order:** Heat Transfer in Solids uses **quadratic** Lagrange elements by default in 4.3a **(verify** under the physics node's *Discretization* section, which is shown after enabling *Show → Discretization* in the Model Builder toolbar). For the comparison with FDM, also run the 10 × 10 mesh with **linear** elements: a 10 × 10 linear mesh has exactly the notebook's 11 × 11 nodes. This is the fairest like-for-like comparison, although the equations are not identical (bilinear elements couple each node to all 8 neighbours, the FDM stencil to 4). Quadratic elements are much more accurate on the same mesh.

### 2.7 Study: output times and the time-dependent solver

- **Study 1 → Step 1: Time Dependent → Times:** `range(0,10,600)` (every 10 s, 61 outputs; fine enough to interpolate the time to 100 °C to < 0.1 s). Add `349.14` if desired: `range(0,10,600) 349.14`.
- These are **output times only**: the BDF solver chooses its own internal steps. Make this the first solver lesson (§3.5).
- **Relative tolerance:** default 0.01. For the comparison runs set **0.0001** (Study → Step 1 → *Study Settings* → Relative tolerance) **(verify** location: in 4.3a it is on the Time Dependent step, check box *Relative tolerance*).
- **Results While Solving:** enable *Plot* and select the probe plot (§3.3).

---

## 3 · The new COMSOL skills this problem must teach

Build the guide around these (each one a numbered step or two, with a screenshot and a "why?" box, as in the earlier guides). Earlier guides already taught: model wizard, parameters, geometry, mesh basics, fixed-temperature and convective boundaries, stationary and time-dependent studies, line graphs, derived values, and table export.

### 3.1 The Material Library / Material Browser

- Opening the browser, the difference between Built-In and the (licensed) Material Library, searching for "steel", reading the property table (which properties are constants and which are functions of T), the red/green flags showing which properties the physics needs.
- Adding a library material vs a blank user-defined material; assigning a material to a domain; the material node overriding order.
- Result to show: the same model with the library steel gives a noticeably different cooling time (§2.4 prediction: about −13 % for the Built-In steel values). Moral: check the data, not only the mesh.

### 3.2 Symmetry to model a quarter

- Why the quarter is enough; the Symmetry boundary condition (= no flux for heat transfer); the 4× saving.
- Optional check: build the full 2L × 2L square once (`billet_full` in the same .mph or a second component), run it on a 20 × 20 mapped mesh and show the centre temperature agrees with the quarter model (it must, to solver tolerance).

### 3.3 A domain point probe plotting the centre temperature while solving

- **Definitions → Probes → Domain Point Probe** at (0, 0): expression `T`, unit degC. Add two more: at (L, 0) and (L, L) (or use **Point Probes** on the geometry vertices; show both and explain the difference: a domain point probe can be placed anywhere, a point probe needs a vertex) **(verify** probe names and that a domain point probe accepts a point on the boundary; if not, use (1e-6, 1e-6) or the vertex point probe).
- In Study → Time Dependent → **Results While Solving**: Plot = on, Probes = all. The **Probe Plot** then draws the centre temperature against time while the solver runs, and the **Probe Table** collects the values at every output time.
- Use the probe table to read off the time at which the centre crosses 100 °C (interpolate between the two output times around it; with 10 s outputs, linear interpolation is accurate to about 0.1 s; for the guide also show the exact 349.14 s).

### 3.4 Choosing output times and exporting an animation

- `range(start, step, stop)` syntax; the difference between output times and solver steps; a dense list for curves vs a few times for field plots (30, 120, 300, 600 s, the notebook's snapshot times).
- Surface plot of T in degC with a fixed colour range 30 to 600 °C (Range: manual), plus **Contour** isotherms; a **Mirror 2D** data set (**Data Sets → Mirror 2D**, axis x = 0, then a second Mirror 2D about y = 0) to show the full cross-section from the quarter model **(verify** that 4.3a has *Mirror 2D*; it should, under Data Sets).
- **Results → Export → Animation**: format GIF (or AVI on Windows), all output times, frame rate about 10 fps, file `billet_cooling.gif` **(verify** the export node and the available formats in 4.3a, it may be *Export → Animation* with a *Player* node).

### 3.5 Adaptive BDF time steps vs forced fixed steps

This is the most important new skill; tie it to the notebook's FTCS vs ADI story.

- 4.3a's Time-Dependent Solver (Study → Solver Configurations → Solver 1 → **Time-Dependent Solver 1** → *Time Stepping* section): Method **BDF** (default; variable order 1 to 5) or Generalized-α; **Steps taken by solver: Free** (default) / **Intermediate** / **Strict** / **Manual** with a *Time step* field **(verify** these four names and where the *Maximum BDF order* and *Initial step* fields are).
- Runs to make on the 10 × 10 mesh (quadratic elements, user-defined steel), recording for each: number of time steps taken (solver log), solution time (Messages/Log), T at the three points at 300 s, and the time to 100 °C:

  | run | settings | compare with |
  |---|---|---|
  | A | Free, default relative tolerance 0.01 | — (shows the default is coarse) |
  | B | Free, relative tolerance 1e-4 | the exact values |
  | C | Strict, tolerance 1e-4 | B (Strict makes the solver hit every output time exactly) |
  | D | Manual, time step 10 s, BDF max order 2 | notebook ADI Δt = 10 s (both second-order implicit) |
  | E | Manual, time step 60 s, BDF max order 2 | notebook ADI Δt = 60 s: does COMSOL also oscillate at the corner? |
  | F | Manual, time step 0.5 s, BDF max order 1 (backward Euler) | notebook FTCS Δt = 0.5 s (first order in time, but implicit) |

- **Export the step sizes**: in the Time-Dependent Solver *Output* section (or Study step *Times to store*), choose to store **Steps taken by solver** for run B; export T_centre at every stored step and plot Δt against t **(verify** that 4.3a offers *Times to store: Steps taken by solver*). Expected picture: tiny steps at the start (the surface temperature changes fastest there; the notebook needed Δt ≈ 10 s or less for an accurate corner at early times), growing to tens of seconds later. Overlay the FTCS limit 0.518 s (constant) and the ADI 10 s line in `p8_steps.png`.
- Teaching points (all supported by the notebook): an implicit method is stable for any Δt, but accuracy still needs small steps where things change fast; adaptive stepping does that automatically; a fixed large step (run E) reproduces the oscillation the notebook shows for ADI with Δt = 60 to 120 s (or, for BDF2, damps it more strongly than ADI/Crank–Nicolson; report what is seen).

### 3.6 Optional extensions (second .mph, short section at the end of the guide)

1. **2D axisymmetric round billet**: a round bar of the same cross-section area (radius R = 2L/√π = 56.4 mm) or with the inscribed radius (R = L = 50 mm), in **2D axisymmetric** (r, z): a rectangle 0 ≤ r ≤ R, 0 ≤ z ≤ H (any H) with convection on r = R and insulation on z = 0 and z = H, so that nothing changes along z (an infinitely long bar); the axis r = 0 needs no condition. Exact solution: infinite cylinder series (Incropera §5.6), ζ J₁(ζ)/J₀(ζ) = Bi with Bi = hR/k. Compare the centre cooling times of the round and the square billet.
2. **Temperature-dependent k(T)** (and c_p(T)): either the Material Library steel or a user-defined interpolation function, e.g. k = 60.5, 56.7, 48.0, 39.2, 30.0 W/(m·K) at 300, 400, 600, 800, 1000 K and c_p = 434, 487, 559, 685, 1169 J/(kg·K) (plain carbon steel, Incropera Table A.1; **check these values against the book** before using them). Report the change of the time to 100 °C. (This is also the notebook's "Try it yourself 5".) Note that c_p has a strong peak near the Curie/austenite transition (~1000 K) that tables smooth over; above 600 °C the start is outside this problem anyway.

---

## 4 · Results to export and the comparisons to make

Reference numbers are all in `fdm_reference.json`; the most important ones are repeated here.

### 4.1 Temperature at three points against time (main comparison)

Export from the probe table (or Derived Values → Point Evaluation on Cut Point 2D data sets) for run B, 10 × 10 mesh, at the output times 30, 60, 120, …, 600 s → `billet_points.txt`. Reference (°C):

| t [s] | 30 | 60 | 120 | 180 | 240 | 300 | 360 | 420 | 480 | 540 | 600 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exact, centre (0, 0) | 580.39 | 504.00 | 352.36 | 246.23 | 174.94 | 127.14 | 95.11 | 73.64 | 59.25 | 49.60 | 43.14 |
| exact, face middle (L, 0) | 413.35 | 340.36 | 237.30 | 168.92 | 123.11 | 92.41 | 71.83 | 58.03 | 48.79 | 42.59 | 38.44 |
| exact, corner (L, L) | 297.01 | 233.22 | 163.31 | 119.25 | 89.81 | 70.09 | 56.87 | 48.01 | 42.07 | 38.09 | 35.42 |
| FTCS N = 10, Δt = 0.5 s, centre | 580.73 | 504.10 | 352.11 | 245.89 | 174.59 | 126.84 | 94.85 | 73.43 | 59.09 | 49.48 | 43.05 |
| ADI N = 10, Δt = 10 s, centre | 581.09 | 504.60 | 352.53 | 246.30 | 174.96 | 127.14 | 95.10 | 73.63 | 59.24 | 49.59 | 43.13 |

(FTCS and ADI values at the face middle and the corner are in the JSON, `point_histories`.)

Figure `p8_comparison.png`, left panel: T against t at the three points, exact lines, COMSOL markers, FDM (FTCS) small markers, plus the lumped-capacitance curve T∞ + (Tᵢ − T∞) exp(−t/109.76 s) and the 100 °C line, in the style of `../docs/figures/history.png`.

### 4.2 Time for the centre to reach 100 °C

Table for the README and the guide:

| method | time to 100 °C |
|---|---|
| exact | 349.14 s |
| lumped capacitance | 230.18 s |
| FTCS, N = 10, Δt = 0.5 s | 348.57 s |
| ADI, N = 10, Δt = 10 s | 349.15 s |
| COMSOL, 10 × 10 quadratic, run B | *to fill* |
| COMSOL, 10 × 10 linear, run B | *to fill* |
| COMSOL, library steel | *to fill* (prediction for Built-In steel values: 304.5 s) |

### 4.3 Profiles along y = 0

Line graph on a **Cut Line 2D** from (0, 0) to (L, 0) at t = 30, 120, 300, 600 s, exported at 11 points x = 0, 5, …, 50 mm → `billet_profiles.txt`. Reference exact values (°C), x = 0 → 50 mm:

- 30 s: 580.39, 579.28, 575.87, 569.86, 560.79, 548.12, 531.25, 509.63, 482.86, 450.75, 413.35
- 120 s: 352.36, 351.14, 347.49, 341.42, 333.00, 322.27, 309.31, 294.21, 277.09, 258.07, 237.30
- 300 s: 127.14, 126.77, 125.67, 123.83, 121.28, 118.03, 114.11, 109.56, 104.39, 98.66, 92.41
- 600 s: 43.14, 43.09, 42.94, 42.69, 42.35, 41.91, 41.38, 40.76, 40.06, 39.29, 38.44

(FTCS and ADI profiles are in the JSON, `profiles_y0`.)

### 4.4 Mesh study (spatial convergence)

For n_el = 5, 10, 20, 40, with run-B solver settings (tolerance 1e-4, or Manual small steps so that the time error is negligible), record the largest |T_COMSOL − T_exact| over the domain at t = 300 s (or at the nodes / the three points) and T_centre(300 s) → `billet_mesh_study.txt`. Do it for quadratic and linear elements. Notebook reference (FTCS, r ≈ 0.2, largest error over all nodes at 300 s): Δx = 10, 5, 2.5, 1.25 mm → 1.1176, 0.2785, 0.0696, 0.0174 °C (ratio 4.0: second order; for FTCS this includes the time error, which scales with Δx² because Δt ∝ Δx²). Exact T_centre(300 s) = 127.1439 °C.

Expected: linear elements second order (similar size of error to FDM if the time error is removed: the notebook's spatial error at N = 10 is +0.018 °C at the centre, see `time_study_N10_t300.reference_centre_C` = 127.16214 °C vs exact 127.14392 °C); quadratic elements much smaller errors. Figure `p8_comparison.png`, right panel: error against element size (log-log) for FDM, COMSOL linear, COMSOL quadratic, with slope-2 (and slope-3/4) guide lines.

### 4.5 Solver-step study and material

- `billet_solver_steps.txt`: one row per run A to F of §3.5 (steps, solution time, T at the three points at 300 s, time to 100 °C), plus the step-size history of run B. Notebook reference on N = 10 (centre at 300 s, exact 127.144 °C; time to 100 °C, exact 349.14 s):

  | method | Δt [s] | steps to 600 s | T_centre(300 s) | time to 100 °C |
  |---|---|---|---|---|
  | FTCS | 0.5 | 1200 | 126.838 | 348.6 |
  | ADI | 5 | 120 | 127.158 | 349.2 |
  | ADI | 10 | 60 | 127.144 | 349.2 |
  | ADI | 20 | 30 | 127.091 | 349.4 |
  | ADI | 30 | 20 | 127.001 | 349.6 |
  | ADI | 60 | 10 | 125.507 | 350.1 |

  ADI corner temperature after 1, 2, 3, 4 steps (exact in brackets): Δt = 60 s: 146.8, 220.0, 87.8, 115.8 (233.2, 163.3, 119.2, 89.8). Δt = 10 s: 346.6, 354.9, 282.1, 280.1 (390.1, 333.0, 297.0, 270.9). Compare with COMSOL runs D and E at the corner.
- `billet_material.txt`: user-defined vs library steel (property values used, T at the three points at 300 s, time to 100 °C).
- Figure `p8_steps.png`: COMSOL step size against time (run B), with horizontal lines at the FTCS limit (0.518 s on N = 10) and the ADI step (10 s).

### 4.6 Stability numbers (for the theory page of the guide)

On the N = 10 grid: interior r ≤ 1/4, convective surface r ≤ 0.2376, **corner r ≤ 0.2264 → Δt ≤ 0.518 s** (positive-weight rule); true FTCS limit r = 0.2491. On the hand grid N = 2: corner 0.1644 (Δt ≤ 9.40 s), true limit 0.2293. COMSOL's implicit BDF has no such limit; this is the reason to explain why COMSOL can take 10 to 60 s steps.

---

## 5 · Things that could not be verified here (check in COMSOL 4.3a)

COMSOL was not available in the session that wrote this file. Check on screen and correct the guide where these differ:

1. The exact name and location of the convective boundary condition in Heat Transfer in Solids (Heat Flux node with a *Convective heat flux* option vs a separate node), and its field labels.
2. Whether ht in 4.3a has a **Symmetry** boundary condition (else: Thermal Insulation, which is mathematically identical here).
3. Boundary and point numbering of the square.
4. Built-In steel property values (expected k = 44.5, ρ = 7850, c_p = 475 for *Structural steel* and *Steel AISI 4340*), and whether the separately licensed **Material Library** is installed on the PC (and which plain carbon steels it lists).
5. `[degC]` handling in Initial Values and External temperature.
6. Probe names (*Domain Point Probe*, *Point Probe*), whether a domain point probe may sit on the boundary point (0, 0), and the *Results While Solving* settings.
7. Time-Dependent Solver settings: *Steps taken by solver* (Free / Intermediate / Strict / Manual), *Maximum BDF order*, where the *Relative tolerance* is, and *Times to store: Steps taken by solver*; where the number of steps appears in the Log.
8. Data Sets → *Mirror 2D* and *Cut Point 2D* / *Cut Line 2D* names.
9. Animation export (node name, GIF/AVI availability).
10. How to switch the element order to linear (*Discretization* section, after *Show → Discretization*).
11. The k(T), c_p(T) table of §3.6 (from memory of Incropera Table A.1; verify against the book).

---

## 6 · Checklist for the desktop session

- [ ] Build `billet_cooling_comsol.mph` (§2) and save it in COMSOL 4.3a.
- [ ] Runs: main (B), mesh study (5/10/20/40, quadratic and linear), solver runs A to F, library steel; export the `.txt` files of §4 and the animation.
- [ ] `p8_analysis.py` and `p8_fig.py` with paths relative to `Path(__file__).parent`; produce `p8_comsol_numbers.json`, `p8_comparison.png`, `p8_steps.png`.
- [ ] Guide `COMSOL_Billet_Cooling_Guide.pdf` built around §3, with annotated screenshots and the comparison tables.
- [ ] `README.md` replacing this file; delete `HANDOFF.md`.
- [ ] One sentence + link in `../README.md`; home-page mention only if no other session is editing it.
- [ ] Check every number written in the README and the guide against the exported data and `fdm_reference.json`.
