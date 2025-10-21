"""
This module contains the function to calculate the volume of the convex hull of the data.
"""

import numpy as np
from scipy.spatial import ConvexHull # pylint: disable=no-name-in-module
from anndata import AnnData

def calculate_convex_hull_volume(
    adata: AnnData,
    data_layer: str = 'X_pca_reduced',
    n_vertices: int = 3
) -> float:
    """
    Calculates the volume of the convex hull of the data in adata.

    Parameters
    ----------
    adata
        An AnnData object containing your data.
    data_layer
        The data layer to use. Default is 'X_pca_reduced' in adata.obsm.
    n_vertices
        Number of archetypes.

    Returns
    -------
    volume
        The volume of the convex hull of the data.
    """
    # Extract data from the specified layer
    if data_layer in adata.obsm:
        data = np.array(adata.obsm[data_layer])
    elif data_layer == 'X':
        data = np.array(adata.X)
    else:
        raise ValueError(f"Data layer '{data_layer}' not found in adata.obsm or as 'X'.")

    # Determine the number of dimensions to use
    num_dimensions = min(n_vertices - 1, data.shape[1])
    if num_dimensions < 1:
        raise ValueError("Number of dimensions for convex hull must be at least 1.")

    # Compute the convex hull without assigning to a temporary variable
    volume = ConvexHull(data[:, :num_dimensions]).volume

    return volume
