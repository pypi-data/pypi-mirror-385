"""
This module contains the function to set the cells that represent 
each vertex (the top 5% of cells closest to each vertex).
"""
# pylint: disable=invalid-name

import numpy as np
import pandas as pd

from anndata import AnnData

def get_sort_orders(
    data: np.ndarray,
    coords: np.ndarray
) -> np.ndarray:
    """
    Compute the sort order (rank) of each index in data for distance to each point in coords.

    This function computes the Euclidean distance between each 
    sample in data and each point in coords,
    then returns the rank (sort order) of each sample with 
    respect to each coordinate point.

    Parameters
    ----------
    data
        :class:`numpy.ndarray` of shape (n_samples_in_adata, n_components)
        The data points to rank.

    coords
        :class:`numpy.ndarray` of shape (n_coords, n_components)
        The coordinate points to rank against.

    Returns
    -------
    ranks
        :class:`numpy.ndarray` of shape (n_samples_in_adata, n_coords)
        ranks[i, j] is the rank (sort order) of sample i in data with respect to coord j

    Examples
    --------
    .. code-block:: python

        # Compute ranks of samples with respect to coordinate points
        ranks = get_sort_orders(adata.obsm['X_pca'], coords)
    """
    # Compute the Euclidean distance matrix between adata points and coords
    D = np.linalg.norm(data[:, np.newaxis, :] - coords[np.newaxis, :, :], axis=2)

    # Compute the ranks by performing argsort twice
    ranks = np.argsort(np.argsort(D, axis=0), axis=0)

    return ranks


def get_top_indices(
    ranks: np.ndarray,
    portion: float = 0.05
) -> list[np.ndarray]:
    """
    Get the indices of the closest samples to each coord.

    This function identifies the top percentage of samples closest to each coordinate point
    based on the provided ranks. For example, portion = 0.05 returns the top 5% of indices.

    Parameters
    ----------
    ranks
        :class:`numpy.ndarray` of shape (n_samples_in_adata, n_coords)
        ranks[i, j] is the rank (sort order) of sample i in adata with respect to coord j

    portion
        The fraction of top samples to select (e.g., 0.05 for top 5%).
        Default: 0.05

    Returns
    -------
    top_indices
        :class:`list` of :class:`numpy.ndarray` arrays, where top_indices[j] contains the indices
        of the closest samples to coord j.

    Examples
    --------
    .. code-block:: python

        # Get top 5% of samples closest to each coordinate
        top_indices = get_top_indices(ranks, portion=0.05)
    """
    n_samples = ranks.shape[0]
    threshold = int(np.ceil(n_samples * portion))  # Calculate the top 5% threshold

    # Create a boolean mask where ranks are less than the threshold
    mask = ranks < threshold  # Shape: (n_samples, n_coords)

    # For each coord, get the indices where the mask is True
    # This gives us the indices of the top 5% closest samples for each coord
    top_indices = [np.where(mask[:, j])[0] for j in range(mask.shape[1])]

    return top_indices


def assign_top_cells_adata(
    adata: AnnData,
    top_indices: list[np.ndarray]
) -> None:
    """
    Assigns categorical columns in `adata.obs` for each coordinate, indicating if a cell is
    in the top 5% closest samples for that coordinate.

    This function modifies the AnnData object by adding categorical columns to adata.obs
    that indicate whether each cell is among the top samples closest to each coordinate point.

    Parameters
    ----------
    adata
        AnnData object with `obs` attribute.

    top_indices
        :class:`list` of :class:`numpy.ndarray` arrays, where top_indices[j] contains the indices
        of the top 5% closest samples to coord j.
    
    Modifies
    --------
    adata.obs
        Adds new categorical columns for each coordinate, named "represents_vertex_{j}".

    Examples
    --------
    .. code-block:: python

        # Assign top cell indicators to adata.obs
        assign_top_cells_adata(adata, top_indices)
    """
    n_obs = adata.n_obs
    n_coords = len(top_indices)

    # Create a boolean array with shape (n_obs, n_coords), initialized to False
    is_top_cell = np.zeros((n_obs, n_coords), dtype=bool)

    # Loop over top_indices and set the corresponding cells to True
    for j, indices in enumerate(top_indices):
        is_top_cell[indices, j] = True

    # Assign the boolean array to adata.obs with column names "represents_vertex_{j}"
    column_names = [f"represents_vertex_{j}" for j in range(n_coords)]
    adata.obs[column_names] = is_top_cell

    # Convert all columns to categorical
    adata.obs[column_names] = adata.obs[column_names].astype(pd.CategoricalDtype(categories=[False, True]))


def set_cells_that_represent_each_vertex(
    adata: AnnData,
    coords: np.ndarray,
    data_layer: str = 'X_pca_reduced'
) -> None:
    """
    Set the cells that represent each vertex by identifying the top 5% closest cells.

    This function performs a complete workflow to identify and mark the cells that are closest
    to each coordinate point (vertex). It computes distances, ranks cells, identifies the top 5%,
    and assigns categorical indicators to the AnnData object.

    Parameters
    ----------
    adata
        :class:`AnnData` object containing the data to analyze.

    coords
        :class:`numpy.ndarray` of shape (n_coords, n_components)
        The coordinate points representing vertices.

    data_layer
        The key in adata.obsm to use for distance calculations.
        Default: 'X_pca_reduced'

    Modifies
    --------
    adata.obs
        Adds categorical columns "represents_vertex_{j}" for each coordinate.

    Examples
    --------
    .. code-block:: python

        # Set cells representing each vertex using PCA-reduced data
        set_cells_that_represent_each_vertex(adata, coords, data_layer='X_pca_reduced')
    """

    if adata.obsm[data_layer] is None:
        raise ValueError(f"{data_layer} not found in adata.obsm")

    #get sort orders of data
    n = coords.shape[1]  # Get the number of columns in coords
    ranks = get_sort_orders(adata.obsm[data_layer][:, :n], coords)

    #get top 5 percent of indices
    top_indices = get_top_indices(ranks, portion=0.05)

    #assign this to adata
    assign_top_cells_adata(adata, top_indices)
