"""
This module contains the function to fit polytopes to adata, adata_dict, 
and filter the results to include only adata with significant polytopes.
"""

import numpy as np
import anndict as adt

from anndata import AnnData

from pyparti.utils import pca_with_metadata_removal_adata
from .algs import (
    sdvmm,
    sisal,
    pcha,
    # maxvoldual,
)
from .find_min_polytope import find_min_polytope_adata
from .significance import calculate_p_value


def fit_polytope(
    adata: AnnData,
    n_vertices: int = 6,
) -> AnnData:
    """
    function to find archetypes given adata
    """
    subset_column = '1k_subsample'
    if subset_column not in adata.obs:
        raise ValueError(f"adata.obs does not contain a {subset_column} column. \
            Please run preprocess_adata_subset_for_parti() before finding archetypes.")

    adata_subset = adata[adata.obs[subset_column]].copy()

    gene_subset_column = 'included_in_density_calculation'
    metadata_columns = ['pct_counts_artefact']

    #compute pca of the data
    pca_with_metadata_removal_adata(
        adata_subset,
        gene_subset_column,
        metadata_columns,
        correlation_threshold=0.3,
    )

    #find the minimal polytope and its volume
    polytope_func = sdvmm if (n_vertices > 2) else sisal #use the SDVMM if more than 2 archetypes, otherwise use Sisal
    min_polytope_coords, min_polytope_volume = find_min_polytope_adata(
        adata_subset,
        polytope_func,
        data_layer='X_pca_reduced',
        n_vertices=n_vertices,
    )

    #Sort ArchsMin columns by their magnitude (L2 norm)
    min_polytope_coords = min_polytope_coords[
        np.argsort(np.linalg.norm(min_polytope_coords, axis=1)),
        :,
    ]

    # return adata_subset, min_polytope_coords

    #Now, Calculate the p value of this fit
    p_value = calculate_p_value(
        adata=adata_subset,
        data_layer='X_pca_reduced',
        polytope_func=polytope_func,
        polytope_coords=min_polytope_coords,
        polytope_volume=min_polytope_volume,
    )

    #Here is where error bounds on the coords in min_polytope_coords would be calculated.
    #Not currently implemented.

    #store results in .uns, then return the adata
    adata_subset.uns['polytope'] = {
        'min_polytope_coords': min_polytope_coords,
        'p_value': p_value
    }

    return adata_subset


def fit_polytope_adata_dict(
    adata_dict: adt.AdataDict,
    n_vertices: int = 4,
) -> adt.AdataDict:
    """
    Finds the minimal polytope for each :class:`AnnData` in :class:`AdataDict`.

    Parameters
    ----------
    adata_dict
        An :class:`AdataDict` object.

    n_vertices
        Number of vertices in the polytope.

    Returns
    -------
    adata_dict
        :class:`AdataDict` object with the minimal polytope for each :class:`AnnData`
        object.
    """

    return adata_dict.fapply(
        fit_polytope,
        return_as_adata_dict=True,
        n_vertices=n_vertices,
    )
