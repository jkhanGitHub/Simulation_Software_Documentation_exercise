"""
heat3d package
--------------

Exports the most useful public functions so they can be imported directly
from `heat3d` if desired.

>>> from heat3d import explicit_solver, load_config
"""

from .config_parser import load_config
from .solver import explicit_solver
from .io_utils import save_field, plot_slice
