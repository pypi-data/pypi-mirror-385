import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from miso_plot import miso_plot
from miso_plot.palettes import hex_to_rgb, process_cmap
import pytest

def test_hex_to_rgb_255():
    assert hex_to_rgb("#ffffff") == [255, 255, 255]
    assert hex_to_rgb("#000000") == [0, 0, 0]

def test_hex_to_rgb_normalized():
    rgb = hex_to_rgb("#808080", scale_255=False)
    assert all(0 <= v <= 1 for v in rgb)

def test_process_cmap_builtin():
    cmap = process_cmap("miso24", 3)
    assert cmap.shape[1] == 3
    assert cmap.shape[0] >= 3

def test_process_cmap_invalid_name():
    with pytest.raises(ValueError):
        process_cmap("nonexistent_palette", 3)

def test_import_package():
    import miso_plot
    assert hasattr(miso_plot, "__package__")

def test_miso_plot_clusters(tmp_path):
    data, labels = make_blobs(n_samples=20000, 
                              centers=4, 
                              n_features=2, 
                              random_state=42)
    X, Y = data[:, 0], data[:, 1]
    fig, ax = plt.subplots()
    ax = miso_plot(X, Y, labels, cmap="tab10", 
                   m=0.2, lam=10, ax=ax)
    outfile = tmp_path / "example_clusters.png"
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    assert outfile.exists()
