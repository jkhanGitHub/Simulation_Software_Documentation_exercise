"""
utils.py
---------

Utility functions that are useful across the package.
"""

from typing import Tuple

import numpy as np


def max_dt(dx: float, alpha: float) -> float:
    """
    Compute the stability limit for the explicit forward‑Euler scheme
    with a 7‑point Laplacian in 3‑D.

    The CFL condition for a uniform grid reads:

        dt <= dx² / (6 * alpha)

    Parameters
    ----------
    dx : float
        Spatial step (assumed equal in all directions).
    alpha : float
        Thermal diffusivity.

    Returns
    -------
    float
        Maximum stable time step.
    """
    return dx ** 2 / (6.0 * alpha)


def compute_grid_vectors(cfg: dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Build the physical coordinate vectors (x, y, z) and the uniform spacing dx.

    Parameters
    ----------
    cfg : dict
        Configuration dictionary.

    Returns
    -------
    tuple (x, y, z, dx)
        1‑D arrays for each axis and the uniform spacing.
    """
    Lx, Ly, Lz = cfg["domain"]["Lx"], cfg["domain"]["Ly"], cfg["domain"]["Lz"]
    Nx, Ny, Nz = cfg["grid"]["Nx"], cfg["grid"]["Ny"], cfg["grid"]["Nz"]

    dx = Lx / (Nx - 1)
    dy = Ly / (Ny - 1)
    dz = Lz / (Nz - 1)

    # For simplicity we enforce a cubic cell (dx = dy = dz). If they differ,
    # the smallest one is used for the stability limit.
    spacing = min(dx, dy, dz)

    x = np.linspace(0.0, Lx, Nx)
    y = np.linspace(0.0, Ly, Ny)
    z = np.linspace(0.0, Lz, Nz)

    return x, y, z, spacing
