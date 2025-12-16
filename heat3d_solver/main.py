#!/usr/bin/env python
"""
main.py
---------

Purpose
-------
Entry point of the 3‑D heat‑equation solver. It parses command‑line arguments,
loads the configuration, calls the solver, and writes the results.

Usage
-----
    python main.py               # uses default config.yaml
    python main.py -c my.yaml    # use a custom configuration file

Public Functions
----------------
run(config_path: str) -> None
    Executes the whole workflow for a given configuration file.
"""

import argparse
import pathlib
import sys

from heat3d import config_parser, solver, io_utils


def run(config_path: str) -> None:
    """
    Run the whole simulation workflow.

    Parameters
    ----------
    config_path : str
        Path to a YAML configuration file.
    """
    # ------------------------------------------------------------------ #
    # 1️⃣ Load & validate configuration
    # ------------------------------------------------------------------ #
    cfg = config_parser.load_config(config_path)

    # ------------------------------------------------------------------ #
    # 2️⃣ Prepare output directory
    # ------------------------------------------------------------------ #
    out_dir = pathlib.Path(cfg["output"]["folder"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # 3️⃣ Run the explicit finite‑difference solver
    # ------------------------------------------------------------------ #
    result = solver.explicit_solver(cfg)

    # ------------------------------------------------------------------ #
    # 4️⃣ Write final field (and optional snapshots) to disk
    # ------------------------------------------------------------------ #
    io_utils.save_field(result["final_field"],
                        out_dir / cfg["output"]["final_field"])

    # Save any intermediate snapshots (if the user requested them)
    for idx, snap in enumerate(result["snapshots"]):
        snap_name = f"{cfg['output']['snapshot_prefix']}{idx:04d}.npy"
        io_utils.save_field(snap, out_dir / snap_name)

    # ------------------------------------------------------------------ #
    # 5️⃣ Optional quick slice plot for visual sanity check
    # ------------------------------------------------------------------ #
    if cfg["output"].get("plot_slice", False):
        io_utils.plot_slice(result["final_field"],
                            out_dir / "final_slice.png",
                            cfg)

    print("\nSimulation completed.")
    print(f"Final field saved to: {out_dir / cfg['output']['final_field']}")
    if result["snapshots"]:
        print(f"{len(result['snapshots'])} snapshots saved.")
    else:
        print("No intermediate snapshots requested.")


def _parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="3D heat equation solver (explicit FD).")
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml).")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_cli()
    if not pathlib.Path(args.config).is_file():
        print(f"Configuration file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    run(args.config)
