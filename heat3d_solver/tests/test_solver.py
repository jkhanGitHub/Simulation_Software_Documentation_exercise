"""
tests/test_solver.py
--------------------

A minimal test that runs the solver for a few steps and checks that the
L2‑norm (energy) of the temperature does not increase, which is expected for
pure diffusion with Dirichlet boundaries.
"""

import pathlib
import shutil
import tempfile

import numpy as np
import pytest

from heat3d import config_parser, solver


def test_energy_decay(tmp_path: pathlib.Path):
    """
    Run a very short simulation (t_final = 0.005) and assert that the
    discrete L2‑norm of the temperature field never grows.
    """
    # --------------------------------------------------------------- #
    # 1️⃣ Create a temporary configuration that overrides the time
    #    settings so the test finishes quickly.
    # --------------------------------------------------------------- #
    cfg = config_parser.load_config("config.yaml")
    cfg["time"]["t_final"] = 0.005
    cfg["time"]["output_every"] = 0  # no snapshots needed
    # Use a small grid to keep the test fast
    cfg["grid"]["Nx"] = cfg["grid"]["Ny"] = cfg["grid"]["Nz"] = 12

    # --------------------------------------------------------------- #
    # 2️⃣ Run the solver
    # --------------------------------------------------------------- #
    result = solver.explicit_solver(cfg)
    final = result["final_field"]

    # --------------------------------------------------------------- #
    # 3️⃣ Compute L2 norm and compare with the initial norm
    # --------------------------------------------------------------- #
    # Re‑create the initial field for comparison
    from heat3d.solver import _initial_temperature
    from heat3d.utils import compute_grid_vectors

    x, y, z, _ = compute_grid_vectors(cfg)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    init = _initial_temperature(cfg, X, Y, Z)

    norm_init = np.linalg.norm(init.ravel())
    norm_final = np.linalg.norm(final.ravel())

    # For pure diffusion the norm should not increase (energy is dissipated)
    assert norm_final <= norm_init * (1.0 + 1e-12)  # allow tiny numerical noise
