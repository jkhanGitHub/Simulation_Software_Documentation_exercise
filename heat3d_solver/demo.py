#!/usr/bin/env python
"""
demo.py
---------

A short demonstration that loads the final temperature field produced by
`main.py` and visualises it.

Features
--------
* Plot a static xy‑slice through the centre of the domain.
* Create an animated GIF that sweeps a slice in the z‑direction.
* (Optional) Produce a simple 3‑D scatter/voxel view of the field.

Usage
-----
    python demo.py                # uses the default config → results/
    python demo.py -d results/    # point to a different output folder
    python demo.py -g gif         # choose animation format (gif or mp4)

The script will write:
    - `slice_center.png`      – static central slice
    - `slice_animation.gif`   – animated sweep (or .mp4 if requested)
    - `volume_view.png`       – 3‑D scatter view (only for grids ≤ 30³)

Dependencies
------------
numpy, matplotlib, imageio

Both are listed in ``requirements.txt`` and can be installed with:
    pip install -r requirements.txt
"""

import argparse
import pathlib

import imageio
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------- #
def load_field(folder: pathlib.Path) -> np.ndarray:
    """Load the final temperature field saved by the solver."""
    field_path = folder / "temperature_final.npy"
    if not field_path.is_file():
        raise FileNotFoundError(f"Result file not found: {field_path}")
    return np.load(field_path)


def plot_central_slice(field: np.ndarray,
                       cfg: dict,
                       out_path: pathlib.Path) -> None:
    """
    Produce a PNG of the xy‑slice at the centre of the domain.

    Parameters
    ----------
    field : np.ndarray
        3‑D temperature data (shape = (Nx, Ny, Nz)).
    cfg   : dict
        Configuration dictionary (used for physical extents).
    out_path : pathlib.Path
        Destination PNG file.
    """
    Nz = field.shape[2]
    mid_z = Nz // 2
    slice_data = field[:, :, mid_z]

    Lx, Ly = cfg["domain"]["Lx"], cfg["domain"]["Ly"]
    extent = [0, Lx, 0, Ly]  # left, right, bottom, top

    plt.figure(figsize=(6, 5))
    im = plt.imshow(slice_data.T, origin="lower", extent=extent,
                    cmap="inferno", interpolation="nearest")
    plt.colorbar(im, label="Temperature")
    plt.title(f"Central slice (z-index = {mid_z})")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def animate_slices(field: np.ndarray,
                   cfg: dict,
                   out_path: pathlib.Path,
                   fmt: str = "gif") -> None:
    """
    Create an animation that moves a slice through the z‑direction.

    Parameters
    ----------
    field : np.ndarray
        3‑D temperature data.
    cfg   : dict
        Configuration dictionary (for axis limits).
    out_path : pathlib.Path
        Destination file (GIF or MP4).
    fmt   : {"gif", "mp4"}
        Desired output format.
    """
    Lx, Ly = cfg["domain"]["Lx"], cfg["domain"]["Ly"]
    extent = [0, Lx, 0, Ly]

    frames = []
    # Create a Matplotlib figure only once – we will reuse its canvas.
    fig, ax = plt.subplots(figsize=(6, 5))
    for k in range(field.shape[2]):   # sweep through z
        ax.clear()
        im = ax.imshow(field[:, :, k].T, origin="lower", extent=extent,
                       cmap="inferno", interpolation="nearest")
        ax.set_title(f"z-index = {k}")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        # Draw the canvas and grab the RGBA buffer
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(),
                              dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(image)

    plt.close(fig)

    if fmt == "gif":
        imageio.mimsave(out_path, frames, fps=10)
    elif fmt == "mp4":
        # imageio needs the 'ffmpeg' writer for mp4
        writer = imageio.get_writer(out_path, fps=10, codec='libx264')
        for frame in frames:
            writer.append_data(frame)
        writer.close()
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Use 'gif' or 'mp4'.")


def plot_volume_view(field: np.ndarray,
                    cfg: dict,
                    out_path: pathlib.Path,
                    threshold: float = 0.01) -> None:
    """
    Very simple 3‑D scatter plot of points whose temperature exceeds a
    user‑defined threshold (as a fraction of the maximum temperature).

    This visualisation is only practical for modest grid sizes
    (≈ 30³ or smaller). For larger data you would normally use a dedicated
    visualiser such as ParaView or VisIt.

    Parameters
    ----------
    field     : np.ndarray
        3‑D temperature data.
    cfg       : dict
        Configuration dictionary (for axis limits).
    out_path  : pathlib.Path
        Destination PNG file.
    threshold : float
        Fraction of the global maximum temperature that defines which
        points are plotted. Default 0.01 → plot points > 1 % of max.
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3‑D)

    max_T = field.max()
    mask = field > (threshold * max_T)

    if not np.any(mask):
        print("No points exceed the threshold – skipping volume view.")
        return

    # Get coordinates of the selected points
    xs = np.linspace(0, cfg["domain"]["Lx"], field.shape[0])[mask[:, 0, 0]]
    ys = np.linspace(0, cfg["domain"]["Ly"], field.shape[1])
    zs = np.linspace(0, cfg["domain"]["Lz"], field.shape[2])

    # Build meshgrid and then flatten only the masked entries
    X, Y, Z = np.meshgrid(
        np.linspace(0, cfg["domain"]["Lx"], field.shape[0]),
        np.linspace(0, cfg["domain"]["Ly"], field.shape[1]),
        np.linspace(0, cfg["domain"]["Lz"], field.shape[2]),
        indexing="ij"
    )
    X = X[mask]
    Y = Y[mask]
    Z = Z[mask]
    T = field[mask]

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(X, Y, Z, c=T, cmap='inferno', marker='o', s=15,
                    depthshade=True)
    fig.colorbar(sc, label='Temperature')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_zlabel('z [m]')
    ax.set_title('3‑D temperature cloud (threshold {:.0%})'.format(threshold))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


# --------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Demo script for visualising the 3‑D heat‑equation results.")
    parser.add_argument(
        "-d", "--directory",
        default="results",
        help="Folder that contains the solver output (default: results).")
    parser.add_argument(
        "-g", "--gif-format",
        choices=["gif", "mp4"],
        default="gif",
        help="Format of the slice animation (gif or mp4).")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.directory)
    if not out_dir.is_dir():
        raise NotADirectoryError(f"Output folder not found: {out_dir}")

    # ----------------------------------------------------------------- #
    # Load configuration (so that we have domain extents)
    # ----------------------------------------------------------------- #
    from heat3d import config_parser
    cfg = config_parser.load_config("config.yaml")   # defaults are fine

    # ----------------------------------------------------------------- #
    # Load the final temperature field
    # ----------------------------------------------------------------- #
    field = load_field(out_dir)

    # ----------------------------------------------------------------- #
    # 1) Static central slice
    # ----------------------------------------------------------------- #
    slice_png = out_dir / "slice_center.png"
    plot_central_slice(field, cfg, slice_png)
    print(f"• Central slice saved to {slice_png}")

    # ----------------------------------------------------------------- #
    # 2) Animated sweep through z
    # ----------------------------------------------------------------- #
    anim_path = out_dir / f"slice_animation.{args.gif_format}"
    animate_slices(field, cfg, anim_path, fmt=args.gif_format)
    print(f"• Slice animation saved to {anim_path}")

    # ----------------------------------------------------------------- #
    # 3) Optional 3‑D volume view (only for small grids)
    # ----------------------------------------------------------------- #
    if max(field.shape) <= 30:
        volume_png = out_dir / "volume_view.png"
        plot_volume_view(field, cfg, volume_png, threshold=0.02)
        print(f"• 3‑D volume view saved to {volume_png}")
    else:
        print("• Grid too large for the simple 3‑D scatter view – skipped.")


if __name__ == "__main__":
    main()
