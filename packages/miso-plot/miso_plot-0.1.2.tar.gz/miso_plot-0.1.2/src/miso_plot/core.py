import numpy as np
import matplotlib.pyplot as plt

def smooth1D(Y, lam):
    m, n = Y.shape
    E = np.eye(m)
    D1 = np.diff(E, axis=0)
    D2 = np.diff(D1, axis=0)
    P = lam**2 * D2.T @ D2 + 2 * lam * D1.T @ D1
    Z = np.linalg.solve(E + P, Y)
    return Z


def compute_density(X, Y, thr=0.5, lam=20):
    n = len(X)
    
    minx, maxx = np.min(X), np.max(X)
    miny, maxy = np.min(Y), np.max(Y)

    nbins_x = min(len(np.unique(X)), 200)
    nbins_y = min(len(np.unique(Y)), 200)

    edges1 = np.linspace(minx, maxx, nbins_x + 1)
    edges1 = np.concatenate(([-np.inf], edges1[1:-1], [np.inf]))

    edges2 = np.linspace(miny, maxy, nbins_y + 1)
    edges2 = np.concatenate(([-np.inf], edges2[1:-1], [np.inf]))

    bin_x = np.digitize(X, edges1)
    bin_y = np.digitize(Y, edges2)

    H = np.zeros((nbins_y, nbins_x))
    for i in range(n):
        if 1 <= bin_y[i] <= nbins_y and 1 <= bin_x[i] <= nbins_x:
            H[bin_y[i]-1, bin_x[i]-1] += 1
    H /= n

    G = smooth1D(H, nbins_y / lam)
    F = smooth1D(G.T, nbins_x / lam).T
    F = F / np.max(F)

    idx_flat = (bin_y - 1) * nbins_x + (bin_x - 1)
    F_flat = F.flatten()
    col = F_flat[idx_flat]

    X2 = X[col >= thr]
    Y2 = Y[col >= thr]
    col = col[col >= thr]

    if len(col) == 0:
        return None

    return col, X2, Y2


def miso_cluster_plot(X, Y, color, thr, lam, ax, alpha=0.3, marker='s', size=10):

    col, X2, Y2 = compute_density(X, Y, thr=thr, lam=lam)
    col_2 = np.tile(color, (len(col), 1)) * col[:, np.newaxis]

    if np.any(col):
        ax.scatter(X2, Y2, s=size, c=col_2, marker=marker, edgecolors='none', alpha=alpha)