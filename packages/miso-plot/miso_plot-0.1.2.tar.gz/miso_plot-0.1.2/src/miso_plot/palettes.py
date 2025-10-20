import numpy as np
import matplotlib as mpl
import seaborn as sns


MISO_24 = ['#bd2466', '#ffc001', '#064081', '#29830a','#ff7103', '#187591', '#ff80b1','#43d5c9',
           '#ff1604',  '#ffdf80', '#4a1092', '#a6ffe6',  '#b2940b', '#ff9080', '#1b4d2e', '#e1ffab',
           '#63a4ff',  '#a033c1', '#77830a', '#943716', '#ff0365', '#7eff0a','#0027ff', '#82222f']

def hex_to_rgb(hex_color, scale_255=True):
    hex_color = hex_color.lstrip('#')
    rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    return rgb if scale_255 else [c / 255.0 for c in rgb]

def process_cmap(cmap, n_clusters):
    """
    Returns a color palette (list of RGB values in the range [0,1]) 
    with a length greater than or equal to n_clusters.

    Parameters:
        cmap (str | list):
            - name of the built-in palette ('miso24')
            - name of a matplotlib/seaborn palette ('viridis', 'tab10', 'deep', etc.)
            - list of hex color codes (e.g. ['#ff0000', '#00ff00', '#0000ff'])
        n_clusters (int): number of required colors
    """
    # Built in palettes
    if cmap == 'miso24':
        colors = MISO_24
    # List of hex colors from user
    elif isinstance(cmap, list) and all(isinstance(c, str) and c.startswith('#') for c in cmap):
        colors = cmap
    # matplotlib/seaborn palettes
    elif isinstance(cmap, str):
        try:
            mpl_cmap = mpl.colormaps[cmap]
            colors = [mpl_cmap(i / max(1, n_clusters - 1)) for i in range(n_clusters)]
            colors = [mpl.colors.to_hex(c) for c in colors]
        except KeyError:
            try:
                colors = sns.color_palette(cmap, n_clusters).as_hex()
            except ValueError as e:
                raise ValueError(f"Unknown colormap '{cmap}'") from e
    else:
        raise ValueError(f"Invalid colormap input: {cmap}")

    if len(colors) < n_clusters:
        raise ValueError(f"Colormap has {len(colors)} colors but needs {n_clusters}")

    # Convert to RGB (0-1)
    rgb_colors = np.array([hex_to_rgb(c, False) for c in colors])
    return rgb_colors
