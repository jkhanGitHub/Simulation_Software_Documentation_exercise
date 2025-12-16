"""
config_parser.py
----------------

Purpose
-------
Read a YAML configuration file, validate required fields and provide sensible
defaults for missing optional entries.

Public Functions
----------------
load_config(path: str) -> dict
    Returns a fully‑validated configuration dictionary.
"""

import pathlib
from typing import Any, Dict

import yaml


# ---------------------------------------------------------------------- #
# Default values used when a key is missing from the user file
# ---------------------------------------------------------------------- #
_DEFAULTS: Dict[str, Any] = {
    "domain": {"Lx": 1.0, "Ly": 1.0, "Lz": 1.0},
    "grid": {"Nx": 30, "Ny": 30, "Nz": 30},
    "material": {"alpha": 1.0},
    "time": {"t_final": 0.1, "dt": None, "output_every": 10},
    "boundary": {
        "x_min": {"type": "Dirichlet", "value": 0.0},
        "x_max": {"type": "Dirichlet", "value": 0.0},
        "y_min": {"type": "Dirichlet", "value": 0.0},
        "y_max": {"type": "Dirichlet", "value": 0.0},
        "z_min": {"type": "Dirichlet", "value": 0.0},
        "z_max": {"type": "Dirichlet", "value": 0.0},
    },
    "initial_condition": {
        "type": "Gaussian",
        "amplitude": 1.0,
        "center": [0.5, 0.5, 0.5],
        "sigma": 0.1,
    },
    "output": {
        "folder": "results",
        "final_field": "temperature_final.npy",
        "snapshot_prefix": "snapshot_",
        "plot_slice": True,
    },
}


def _deep_update(original: Dict[str, Any], updates: Dict[str, Any]) -> None:
    """
    Recursively update the `original` dictionary with the values from `updates`.
    Missing sub‑keys are added, existing ones are overwritten.
    """
    for key, value in updates.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            _deep_update(original[key], value)
        else:
            original[key] = value


def _validate(cfg: Dict[str, Any]) -> None:
    """
    Perform minimal sanity checks – raises `ValueError` if something is obviously wrong.
    """
    # Grid must contain at least 3 points per direction (to have an interior)
    for dim in ("Nx", "Ny", "Nz"):
        if cfg["grid"][dim] < 3:
            raise ValueError(f"{dim} must be >= 3 (got {cfg['grid'][dim]}).")

    # Diffusivity must be positive
    if cfg["material"]["alpha"] <= 0.0:
        raise ValueError("Thermal diffusivity alpha must be > 0.")

    # Time step must be positive if supplied
    if cfg["time"]["dt"] is not None and cfg["time"]["dt"] <= 0.0:
        raise ValueError("time.dt must be > 0 when given.")

    # Boundary types must be either Dirichlet or Neumann
    for face, data in cfg["boundary"].items():
        if data["type"] not in ("Dirichlet", "Neumann"):
            raise ValueError(f"Invalid boundary type for {face}: {data['type']}")


def load_config(path: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file, merge it with defaults and validate it.

    Parameters
    ----------
    path : str
        Path to the YAML file.

    Returns
    -------
    dict
        Fully populated configuration dictionary.
    """
    cfg_path = pathlib.Path(path)
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with cfg_path.open("r") as f:
        user_cfg = yaml.safe_load(f) or {}

    # Start from defaults and override with user‑provided values
    cfg = {}
    _deep_update(cfg, _DEFAULTS)   # copy defaults
    _deep_update(cfg, user_cfg)    # apply overrides

    _validate(cfg)
    return cfg
