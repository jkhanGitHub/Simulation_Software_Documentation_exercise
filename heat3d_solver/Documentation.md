# **Documentation**
**3‑D Heat‑Equation Solver (explicit finite‑difference)**  
*Version 1.0 – 2025‑12‑16*  

---

## Table of Contents
1. [Introduction](#introduction)  
2. [Features](#features)  
3. [Directory structure](#directory-structure)  
4. [Installation & requirements](#installation--requirements)  
5. [Configuration file (`config.yaml`)](#configuration-file-configyaml)  
6. [How the program works](#how-the-program-works)  
   - 6.1 [Overall workflow](#overall-workflow)  
   - 6.2 [Modules & public API](#modules--public-api)  
   - 6.3 [Finite‑difference algorithm](#finite-difference-algorithm)  
7. [Running the solver](#running-the-solver)  
8. [Output files](#output-files)  
9. [Visualization & demo script](#visualization--demo-script)  
10. [Testing](#testing)  
11. [Extending the code](#extending-the-code)  
12. [License](#license)  
13. [References & further reading](#references--further-reading)  

---  

## 1. Introduction
This repository contains a **stand‑alone, pure‑Python implementation** of the transient three‑dimensional heat equation  

\[
\frac{\partial T}{\partial t}= \alpha \nabla^2 T ,
\]

solved on a uniform Cartesian grid with the **explicit forward‑Euler scheme** and a **7‑point Laplacian stencil**.  
The program is intentionally minimal: it demonstrates the numerical method, provides a clean Python API, and writes the results to disk in a format that can be post‑processed with any scientific‑Python toolchain.

---

## 2. Features
| Feature | Description |
|---|---|
| **3‑D uniform grid** | Size and resolution are user‑defined in the config file. |
| **Finite‑difference method** | Explicit forward‑Euler time integration; 7‑point Laplacian. |
| **Boundary conditions** | Dirichlet or Neumann on each of the six faces. |
| **Initial condition** | Gaussian hotspot (default) – easily extensible. |
| **Automatic time‑step selection** | Uses the CFL limit `dt ≤ dx²/(6α)` if `dt` is omitted. |
| **Config‑driven** | All parameters live in a human‑readable `config.yaml`. |
| **Result storage** | Final temperature field and optional snapshots saved as NumPy `.npy`. |
| **Quick visual check** | Automatic central‑slice PNG plot. |
| **Test suite** | `pytest` sanity‑check (energy never increases). |
| **Demo script** | `demo.py` loads the results and produces static/animated visualisations. |
| **No compiled extensions** | Pure Python → easy to install on any platform. |

---

## 3. Directory structure
```
heat3d_solver/
│
├─ config.yaml               # default configuration (editable by the user)
├─ main.py                   # entry point – parses CLI, runs solver, writes output
│
├─ heat3d/                   # package containing the library code
│   ├─ __init__.py
│   ├─ config_parser.py      # loads/validates YAML config
│   ├─ utils.py              # small helper functions (grid, stability)
│   ├─ solver.py             # explicit FD solver
│   └─ io_utils.py           # saving .npy files, slice plotting
│
├─ demo.py                   # optional demonstration/visualisation script
│
├─ tests/
│   └─ test_solver.py        # pytest sanity test
│
├─ requirements.txt          # Python dependencies
└─ README.md                 # short user guide (this file expands it)
```

All files are **self‑contained**; there are no external data files required beyond the configuration.

---

## 4. Installation & requirements
The code depends only on the scientific‑Python stack:

| Package | Version (minimum) |
|---|---|
| Python | 3.9+ |
| NumPy | 1.20+ |
| PyYAML | 5.3+ |
| Matplotlib | 3.3+ |
| pytest (optional, for testing) | 6.0+ |
| imageio (optional, for `demo.py`) | 2.9+ |

**Installation steps**

```bash
# 1. Clone or copy the repository
git clone <repo‑url>
cd heat3d_solver

# 2. Install dependencies (prefer a virtual environment)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The solver can now be invoked with `python main.py`.

---

## 5. Configuration file (`config.yaml`)

The file is written in **YAML**; missing entries are automatically filled with sensible defaults (see `_DEFAULTS` in `heat3d/config_parser.py`).  
Below is a complete annotated template (identical to the shipped one).

```yaml
# ------------------------------
# 3D Heat Equation – Default Run
# ------------------------------

domain:
  # Physical size of the cubic domain [m]
  Lx: 1.0
  Ly: 1.0
  Lz: 1.0

grid:
  # Number of nodes in each direction (including boundaries)
  Nx: 30
  Ny: 30
  Nz: 30

material:
  # Thermal diffusivity α (m²/s)
  alpha: 1.0

time:
  # Total simulation time (s)
  t_final: 0.1
  # Time step (s). If omitted the program will compute the max stable dt.
  dt:                        # leave empty → computed from stability condition
  # Write a snapshot every N steps (0 = only final field)
  output_every: 10

boundary:
  # Dirichlet = fixed temperature, Neumann = insulated
  # Choose "Dirichlet" or "Neumann" for each face.
  # Values are the temperature for Dirichlet faces (ignored for Neumann).
  x_min:
    type: Dirichlet
    value: 0.0
  x_max:
    type: Dirichlet
    value: 0.0
  y_min:
    type: Dirichlet
    value: 0.0
  y_max:
    type: Dirichlet
    value: 0.0
  z_min:
    type: Dirichlet
    value: 0.0
  z_max:
    type: Dirichlet
    value: 0.0

initial_condition:
  # Gaussian hotspot
  type: Gaussian
  amplitude: 1.0
  center: [0.5, 0.5, 0.5]   # relative coordinates (0‑1)
  sigma: 0.1                # width of the Gaussian (in physical units)

output:
  # Folder where results are stored (will be created if missing)
  folder: results
  # File name for the final temperature field
  final_field: temperature_final.npy
  # Prefix for intermediate snapshots (if output_every > 0)
  snapshot_prefix: snapshot_   # becomes snapshot_0000.npy, snapshot_0001.npy, …
  # Whether to create a quick slice plot of the final field (true/false)
  plot_slice: true
```

### Key sections

| Section | Meaning |
|---|---|
| `domain` | Physical size of the cube (`Lx`, `Ly`, `Lz`). |
| `grid` | Number of grid points (`Nx`, `Ny`, `Nz`). Must be ≥ 3. |
| `material` | Thermal diffusivity `α`. Must be > 0. |
| `time` | Total simulation time `t_final`, optional explicit `dt`, and snapshot frequency `output_every`. |
| `boundary` | For each face (`x_min`, `x_max`, …) specify `type` (`Dirichlet` or `Neumann`). Dirichlet needs a `value`. |
| `initial_condition` | Currently only `Gaussian` is supported. `center` is given in *relative* coordinates (0–1) and `sigma` in physical units. |
| `output` | Destination folder, naming of the final field and snapshots, and whether a slice PNG is produced. |

All keys are optional – if a key is omitted the program substitutes the default value shown in the file.

---

## 6. How the program works  

### 6.1 Overall workflow
```
main.py
   └─ load config (config_parser.load_config)
       └─ build output directory
           └─ run explicit solver (solver.explicit_solver)
               ├─ build uniform grid (utils.compute_grid_vectors)
               ├─ initialise temperature (solver._initial_temperature)
               ├─ apply Dirichlet BCs (solver._apply_dirichlet_bc)
               ├─ time‑loop:
               │     • compute Laplacian (solver._laplacian_7point)
               │     • forward‑Euler update
               │     • re‑apply Dirichlet BCs
               │     • store snapshots if requested
               └─ return final field + list of snapshots
           └─ write field(s) to .npy (io_utils.save_field)
           └─ optional slice PNG (io_utils.plot_slice)
```

### 6.2 Modules & public API  

| Module | Public objects | Purpose |
|---|---|---|
| `heat3d/config_parser.py` | `load_config(path: str) -> dict` | Reads *config.yaml*, merges with defaults, validates. |
| `heat3d/utils.py` | `max_dt(dx, alpha)`, `compute_grid_vectors(cfg)` | Stability limit calculation, grid generation. |
| `heat3d/solver.py` | `explicit_solver(cfg) -> dict` | Core explicit finite‑difference solver. |
| `heat3d/io_utils.py` | `save_field(field, path)`, `plot_slice(field, out_path, cfg, slice_index=None)` | Write `.npy` files, generate a central‑slice PNG. |
| `main.py` | `run(config_path)` | CLI entry point – orchestrates all steps. |
| `demo.py` (optional) | `plot_central_slice`, `animate_slices`, `plot_volume_view` | Post‑processing visualisations. |

### 6.3 Finite‑difference algorithm  

1. **Spatial discretisation**  
   Uniform Cartesian grid with spacing  
   \[
   \Delta x = \frac{L_x}{N_x-1},\qquad
   \Delta y = \frac{L_y}{N_y-1},\qquad
   \Delta z = \frac{L_z}{N_z-1}.
   \]  
   For stability we use the *smallest* spacing `dx = min(Δx,Δy,Δz)`.

2. **Laplacian (7‑point stencil)**  
   For any interior node `(i,j,k)`  
   \[
   (\nabla^2 T)_{i,j,k}= \frac{
     T_{i+1,j,k}+T_{i-1,j,k}+T_{i,j+1,k}+T_{i,j-1,k}+T_{i,j,k+1}+T_{i,j,k-1}
     -6\,T_{i,j,k}}{\Delta x^2}.
   \]  
   Implemented efficiently with NumPy slicing (no explicit Python loops).

3. **Time integration (forward‑Euler)**  
   \[
   T^{n+1}=T^{n}+ \Delta t\,\alpha\,\nabla^2 T^{n}.
   \]  
   `Δt` is either the user‑supplied value or, if omitted, set to the **CFL limit**  
   \[
   \Delta t_{\max}= \frac{\Delta x^2}{6\,\alpha}.
   \]  
   The algorithm computes `n_steps = ceil(t_final/Δt)` and then adjusts `Δt` so the final time is hit exactly.

4. **Boundary handling**  
   *Dirichlet*: face values are overwritten after each time step (`_apply_dirichlet_bc`).  
   *Neumann*: no explicit action is required; the interior stencil automatically yields a zero normal derivative because ghost values are never accessed.

5. **Energy decay check (used in tests)**  
   For pure diffusion with homogeneous Dirichlet/Neumann boundaries the discrete L²‑norm \(\|T\|_2\) can only stay constant or decrease. The test ensures the implementation respects this property.

---

## 7. Running the solver  

```bash
# Basic usage (reads config.yaml from the current directory)
python main.py

# Use a custom configuration file
python main.py -c my_config.yaml
```

The program prints a short summary at the end:

```
Simulation completed.
Final field saved to: results/temperature_final.npy
5 snapshots saved.
```

If the output directory does not exist it is created automatically.

### Command‑line options (only one)

| Option | Description |
|---|---|
| `-c`, `--config` | Path to the YAML configuration file (default: `config.yaml`). |

---

## 8. Output files  

All results are placed inside the folder given by `output.folder` (default `results/`).

| File | Content |
|---|---|
| `temperature_final.npy` | 3‑D NumPy array (`float64`) of the temperature at `t = t_final`. |
| `snapshot_####.npy` | Intermediate fields (only if `output_every > 0`). The integer `####` is a zero‑padded snapshot index. |
| `final_slice.png` | PNG image of the central `xy` slice (produced when `output.plot_slice: true`). |
| `demo` scripts may create additional visualisation files (`slice_animation.gif`, `volume_view.png`). |

The `.npy` files can be loaded in any Python session:

```python
import numpy as np
T = np.load('results/temperature_final.npy')
print(T.shape)   # e.g. (30, 30, 30)
```

---

## 9. Visualization & demo script  

A ready‑to‑run script `demo.py` demonstrates how to post‑process the results:

* **Static central slice** – `slice_center.png`.  
* **Animated sweep** – `slice_animation.gif` (or `.mp4` if requested).  
* **3‑D scatter view** – `volume_view.png` (only for modest grids ≤ 30³).  

Run it after the solver finishes:

```bash
python demo.py          # uses folder “results/”
python demo.py -d my_results/   # custom folder
python demo.py -g mp4          # MP4 animation instead of GIF
```

All visualisation code lives in `demo.py`; the core solver does **not** depend on `imageio` or the additional 3‑D plot, keeping the main package lightweight.

---

## 10. Testing  

The repository ships a minimal unit test `tests/test_solver.py` that:

1. Loads the default configuration.  
2. Overrides a few parameters to make the test fast (`t_final = 0.005`, small grid).  
3. Runs the solver.  
4. Re‑creates the initial condition and checks that the L²‑norm never grows.  

Run the test suite with:

```bash
pip install -r requirements.txt   # ensure pytest is installed
pytest -q
```

The test should finish instantly and print `1 passed`. It guarantees that the explicit scheme respects the physical principle of energy dissipation.

---

## 11. Extending the code  

| What you might want | Where to edit / add |
|---|---|
| **Different initial condition** (e.g. step function) | Add a new branch in `_initial_temperature` (solver.py) and expose parameters in `config.yaml`. |
| **Implicit or Crank–Nicolson time integration** | Implement a new function in `solver.py` (e.g. `implicit_solver`). You will need a linear system solver (SciPy sparse) and a different stability handling. |
| **Spatially varying diffusivity** | Extend `material` to contain a 3‑D field, modify Laplacian accordingly (multiply each term by local `α`). |
| **Parallelisation** | Wrap the Laplacian computation with Numba (`@njit(parallel=True)`) or use `cupy` for GPU acceleration. |
| **HDF5 output** | Replace `np.save`/`np.load` in `io_utils.py` with `h5py.File`. |
| **More sophisticated visualisation** | Use `vtk`/`paraview` Python bindings, or generate VTK files from the solver. |
| **Command‑line options for snapshots** | Add `argparse` arguments in `main.py` and propagate them to the solver. |

The code is deliberately modular: each component (config parsing, utilities, solver, I/O) lives in its own file with a small public API, making it straightforward to replace or augment any part.

---

## 12. License  

This educational example is released under the **MIT License**:

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...

[Full MIT text omitted for brevity – see LICENSE file in the repository]
```

You may freely use, modify, and redistribute the code for both academic and commercial purposes.

---

## 13. References & further reading  

* J. H. Ferziger & M. Perić, **Computational Methods for Fluid Dynamics**, 3rd ed., Springer, 2002 – Chapter on diffusion equations.  
* R. Courant, K. Friedrichs, H. Lewy, *On the partial difference equations of mathematical physics* (1928) – CFL condition.  
* M. Griebel, T. Dornseifer, T. Neunhoeffer, **Numerical Simulation in Fluid Dynamics**, SIAM, 1998 – Explicit FD for heat equation.  
* NumPy documentation – efficient array slicing and broadcasting.  
* Matplotlib documentation – `imshow`, `savefig`, and 3‑D plotting (`Axes3D`).  

---  

**End of documentation**  

You can place the above content into a file named `Documentation.md` (or `docs/Documentation.md`) alongside the repository. If you need additional sections or a different format (PDF, HTML, etc.), just let me know!
