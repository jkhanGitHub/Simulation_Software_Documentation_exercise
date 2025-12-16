"""
io_utils.py
-----------

Utility functions for writing results to disk and (optionally) creating a
quick visualisation of a central slice.

Public Functions
----------------
save_field(field: np.ndarray, path: pathlib.Path) -> None
    Write a 3‑D array to a NumPy .npy file.

plot_slice(field: np.ndarray, out_path: pathlib.Path, cfg: dict) -> None
    Save a PNG image of a single z‑mid slice (useful for quick checks).
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np


def save_field(field: np.ndarray, path: pathlib.Path) -> None:
    """
    Save the temperature field as a binary NumPy file.

    Parameters
    ----------
    field : np.ndarray
        3‑D temperature array.
    path : pathlib.Path
        Destination file (must end with `.npy`).
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, field)


def plot_slice(field: np.ndarray,
               out_path: pathlib.Path,
               cfg: dict,
               slice_index: int | None = None) -> None:
    """
    Plot a central (or user‑specified) xy‑slice of the temperature field.

    Parameters
    ----------
    field : np.ndarray
        3‑D temperature data.
    out_path : pathlib.Path
        Destination file for the PNG image.
    cfg : dict
        Configuration dictionary (used to fetch domain extents for axis labels).
    slice_index : int, optional
        Index along the z‑axis to plot. If ``None`` the middle slice is used.
    """
    Nz = field.shape[2]
    if slice_index is None:
        slice_index = Nz // 2

    # Extract the slice
    slice_data = field[:, :, slice_index]

    # Physical extents for axis tick labels
    Lx, Ly = cfg["domain"]["Lx"], cfg["domain"]["Ly"]
    extent = [0, Lx, 0, Ly]  # left, right, bottom, top

    plt.figure(figsize=(6, 5))
    im = plt.imshow(
        slice_data.T,   # transpose because imshow expects (Y, X)
        origin="lower",
        extent=extent,
        cmap="inferno",
        interpolation="nearest",
    )
    plt.colorbar(im, label="Temperature")
    plt.title(f"Temperature slice (z-index = {slice_index})")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
