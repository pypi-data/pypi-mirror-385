"""
miso_plot
==========

A lightweight visualization package for clustered high-density data.

Example:
    >>> from miso_plot import miso_plot
    >>> ax = miso_plot(X, Y, labels, cmap="miso24", m=0.3, lam=20)
    >>> ax.figure.savefig("clusters.png", dpi=300)
"""

from .plotting import miso_plot
from .palettes import process_cmap, hex_to_rgb

__all__ = ["miso_plot", "process_cmap", "hex_to_rgb"]
__version__ = "0.1.0"
