"""
solver.py
---------

Implements the explicit forward‑Euler finite‑difference scheme for the 3‑D
heat equation with Dirichlet/Neumann boundaries.

Public Functions
----------------
explicit_solver(cfg: dict) -> dict
    Run the simulation and return the final temperature field and any
    intermediate snapshots requested by the configuration.
"""

from typing import List, Tuple

import numpy as np

from .utils import max_dt, compute_grid_vectors


def _apply_dirichlet_bc(T: np.ndarray, cfg: dict) -> None:
    """
    Enforce Dirichlet boundary conditions in‑place.

    Parameters
    ----------
    T : np.ndarray (shape = (Nx, Ny, Nz))
        Temperature field.
    cfg : dict
        Configuration dict containing boundary specifications.
    """
    # Helper to set a whole face to a constant value
    def set_face(slice_obj, value):
        T[slice_obj] = value

    bc = cfg["boundary"]
    # X‑faces
    if bc["x_min"]["type"] == "Dirichlet":
        set_face((0, slice(None), slice(None)), bc["x_min"]["value"])
    if bc["x_max"]["type"] == "Dirichlet":
        set_face((-1, slice(None), slice(None)), bc["x_max"]["value"])
    # Y‑faces
    if bc["y_min"]["type"] == "Dirichlet":
        set_face((slice(None), 0, slice(None)), bc["y_min"]["value"])
    if bc["y_max"]["type"] == "Dirichlet":
        set_face((slice(None), -1, slice(None)), bc["y_max"]["value"])
    # Z‑faces
    if bc["z_min"]["type"] == "Dirichlet":
        set_face((slice(None), slice(None), 0), bc["z_min"]["value"])
    if bc["z_max"]["type"] == "Dirichlet":
        set_face((slice(None), slice(None), -1), bc["z_max"]["value"])


def _initial_temperature(cfg: dict,
                         X: np.ndarray,
                         Y: np.ndarray,
                         Z: np.ndarray) -> np.ndarray:
    """
    Initialise the temperature field according to the `initial_condition` block.
    Currently only a Gaussian hotspot is supported.

    Parameters
    ----------
    cfg : dict
        Configuration dict.
    X, Y, Z : np.ndarray
        Meshgrid arrays returned by `np.meshgrid`.

    Returns
    -------
    np.ndarray
        Initial temperature field with shape (Nx, Ny, Nz).
    """
    ic = cfg["initial_condition"]
    if ic["type"] == "Gaussian":
        amp = ic["amplitude"]
        sigma = ic["sigma"]
        # Convert relative centre (0‑1) to physical coordinates
        Lx, Ly, Lz = cfg["domain"]["Lx"], cfg["domain"]["Ly"], cfg["domain"]["Lz"]
        cx = ic["center"][0] * Lx
        cy = ic["center"][1] * Ly
        cz = ic["center"][2] * Lz
        r2 = ((X - cx) ** 2 + (Y - cy) ** 2 + (Z - cz) ** 2)
        return amp * np.exp(-r2 / (2.0 * sigma ** 2))
    else:
        raise NotImplementedError(f"Initial condition type '{ic['type']}' not supported.")


def _laplacian_7point(T: np.ndarray, dx: float) -> np.ndarray:
    """
    Compute the discrete Laplacian using a 7‑point stencil.
    Interior points only; boundary points are left untouched (will be overwritten
    by boundary conditions after each step).

    Parameters
    ----------
    T : np.ndarray (Nx, Ny, Nz)
        Temperature field at the current time level.
    dx : float
        Uniform grid spacing (assumed equal in all directions).

    Returns
    -------
    np.ndarray
        Laplacian of T (same shape as T).
    """
    # Using NumPy slicing is much faster than explicit loops.
    lap = np.zeros_like(T)

    # Interior slice objects
    i = slice(1, -1)
    # Fixed by me after finding the bug: defined shifted slices strictly since slice+int is invalid
    ip1 = slice(2, None)
    im1 = slice(0, -2)

    lap[i, i, i] = (
        T[ip1, i, i] + T[im1, i, i] +
        T[i, ip1, i] + T[i, im1, i] +
        T[i, i, ip1] + T[i, i, im1] -
        6.0 * T[i, i, i]
    ) / (dx ** 2)

    return lap


def explicit_solver(cfg: dict) -> dict:
    """
    Run the explicit forward‑Euler solver.

    Parameters
    ----------
    cfg : dict
        Complete configuration dictionary.

    Returns
    -------
    dict
        {
            "final_field": np.ndarray (Nx, Ny, Nz),
            "snapshots": List[np.ndarray]   # may be empty
        }
    """
    # ------------------------------------------------------------------ #
    # 1️⃣ Grid construction
    # ------------------------------------------------------------------ #
    x, y, z, dx = compute_grid_vectors(cfg)
    Nx, Ny, Nz = cfg["grid"]["Nx"], cfg["grid"]["Ny"], cfg["grid"]["Nz"]

    # Create 3‑D meshgrid for the initial condition (index order = x, y, z)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # ------------------------------------------------------------------ #
    # 2️⃣ Initialise temperature
    # ------------------------------------------------------------------ #
    T = _initial_temperature(cfg, X, Y, Z)

    # Apply Dirichlet boundaries at t = 0
    _apply_dirichlet_bc(T, cfg)

    # ------------------------------------------------------------------ #
    # 3️⃣ Time stepping parameters
    # ------------------------------------------------------------------ #
    alpha = cfg["material"]["alpha"]
    t_final = cfg["time"]["t_final"]
    dt_user = cfg["time"]["dt"]
    dt = dt_user if dt_user is not None else max_dt(dx, alpha)

    # Safety check – warn the user if they supplied a dt larger than the limit
    dt_limit = max_dt(dx, alpha)
    if dt > dt_limit:
        print(
            f"Warning: supplied dt ({dt:.3e}) exceeds stability limit ({dt_limit:.3e})."
            " The solution may become unstable."
        )

    n_steps = int(np.ceil(t_final / dt))
    dt = t_final / n_steps  # adjust to hit t_final exactly

    output_every = cfg["time"].get("output_every", 0)

    # ------------------------------------------------------------------ #
    # 4️⃣ Time integration loop
    # ------------------------------------------------------------------ #
    snapshots: List[np.ndarray] = []
    for step in range(1, n_steps + 1):
        # Compute Laplacian (interior only)
        lap = _laplacian_7point(T, dx)

        # Forward Euler update
        T[1:-1, 1:-1, 1:-1] += dt * alpha * lap[1:-1, 1:-1, 1:-1]

        # Re‑apply Dirichlet boundaries (Neumann faces stay unchanged)
        _apply_dirichlet_bc(T, cfg)

        # Store snapshot if requested
        if output_every > 0 and step % output_every == 0:
            snapshots.append(T.copy())

    # ------------------------------------------------------------------ #
    # 5️⃣ Return results
    # ------------------------------------------------------------------ #
    return {"final_field": T, "snapshots": snapshots}
