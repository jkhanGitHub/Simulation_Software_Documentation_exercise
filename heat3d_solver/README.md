# 3D Heat Equation Solver (explicit finite‑difference)

A minimal, pure‑Python implementation of the transient 3‑D heat equation
using an explicit forward‑Euler scheme with a 7‑point Laplacian stencil.

## Features

* Uniform Cartesian grid (configurable size)
* Dirichlet or Neumann boundary conditions on each face
* Gaussian hotspot initial condition (default)
* Automatic stability‑limited time step (or user‑supplied `dt`)
* Optional intermediate snapshots
* Quick slice plot of the final field
* Configurable via a human‑readable `config.yaml`
* Simple test suite (`pytest`)

## Installation

```bash
git clone <repo-url>  # or just copy the files into a folder
cd heat3d_solver
pip install -r requirements.txt
```

## Running the simulation

```bash
python main.py               # uses the provided config.yaml
# or with a custom file
python main.py -c my_config.yaml
```

Results are written to the folder defined under `output.folder` in the
configuration (default: `results`). The final temperature field is saved as
`temperature_final.npy`. If `output_every` > 0, snapshots are stored as
`snapshot_0000.npy`, `snapshot_0001.npy`, …  
A PNG with a central `xy` slice is also generated if `plot_slice: true`.

## Editing the configuration

All parameters are documented in `config.yaml`. You may change:

* Domain size (`domain.Lx`, `Ly`, `Lz`)
* Grid resolution (`grid.Nx`, `Ny`, `Nz`)
* Material diffusivity (`material.alpha`)
* Time step / total time (`time.dt`, `t_final`)
* Boundary types (`Dirichlet` or `Neumann`) and values
* Initial condition (currently only Gaussian)
* Output options (folder, naming, snapshot frequency, slice plot)

## Testing

```bash
pytest -q
```

The test runs a short simulation and checks that the discrete energy
(L2‑norm) does not increase.

## License

This educational example is released under the MIT License.
