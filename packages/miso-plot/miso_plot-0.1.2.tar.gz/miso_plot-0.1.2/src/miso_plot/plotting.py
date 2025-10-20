# src/miso_plot/plotting.py
import matplotlib.pyplot as plt
import numpy as np
from .core import miso_cluster_plot
from .palettes import process_cmap

def miso_plot(X, Y, labels, cmap="miso24", m=0.5, lam=20, ax=None,
              alpha=0.3, marker='s', size=10):
    """
    Plot clustered high-density 2D data using adaptive smoothing.

    Args:
        X (np.array): X-coordinates.
        Y (np.array): Y-coordinates.
        labels (np.array): Cluster labels for each point.
        cmap (str | list, optional): Colormap or list of hex colors.
        m (float, optional): Density threshold. Defaults to 0.5.
        lam (int, optional): Smoothing parameter. Defaults to 20.
        ax (matplotlib.axes.Axes, optional): Existing Axes. Defaults to None.
        alpha (float, optional): Point transparency. Defaults to 0.3.
        marker (str, optional): Marker style. Defaults to 's'.
        size (int, optional): Point size. Defaults to 10.

    Returns:
        matplotlib.axes.Axes: The Axes with plotted clusters.
    """
    
    if ax is None:
        fig, ax = plt.subplots()
    labels = np.array(labels)
    clusters = np.unique(labels)
    colors = process_cmap(cmap, len(clusters))
    for i, cluster in enumerate(clusters):
        mask = labels == cluster
        miso_cluster_plot(X[mask], Y[mask], colors[i], m, lam, ax, alpha, marker, size)
    return ax
