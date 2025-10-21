"""
This module contains the functions to get the genes enriched at each vertex.
"""

from typing import Callable

import numpy as np
import pandas as pd
import anndict as adt

from anndata import AnnData

from .differential_expression import (
    median_difference,
    compute_differential_expression,
    sort_differential_expression,
)
from .set_top_cells import set_cells_that_represent_each_vertex


def extract_enriched_genes(
    adata: AnnData,
    alpha: float = 0.10,
    adt_key: tuple[str,...] | None = None
) -> None:
    """
    Extracts enriched genes from an AnnData object that has been processed by 
    :func:`compute_differential_expression` and returns a :class:`pandas.DataFrame`. 
    If ``adt_key`` is provided, it adds ``'stratum'`` and ``'stratum_vertex'`` columns.

    Parameters
    ----------
    adata
        :class:`AnnData` object containing the data to analyze.

    alpha
        :class:`float`
        The alpha level for the Benjamini-Hochberg correction.

    adt_key
        :class:`tuple` of :class:`str`
        The key in ``adata.uns`` to use for the differential expression results.

    Returns
    -------
    ``None``

    Notes
    -----
    This function extracts enriched genes from the differential expression results in 
    ``adata.uns['vertex_defining_genes']`` and stores the results in 
    ``adata.uns['genes_enriched_at_each_vertex']``.
    """
    # Initialize an empty list to store the rows of the DataFrame
    enriched_genes_data = []

    # Access the differential expression results in `adata.uns['vertex_defining_genes']`
    diff_expr_results = adata.uns['vertex_defining_genes']

    # Loop over each mask column (vertex)
    for column in diff_expr_results:
        # The vertex number can be extracted from the column name
        # assuming the column names are 'represents_vertex_{j}'
        vertex_num = int(column.replace('represents_vertex_', ''))

        # Extract the DE results for the 'True' group
        de_result = diff_expr_results[column]
        group = 'True'  # 'True' is the category of interest
        pvals_adj = np.array(de_result['pvals_adj'][group])
        gene_names = np.array(de_result['names'][group])

        # Filter genes based on the Benjamini-Hochberg corrected p-values and alpha cutoff
        significant_genes_mask = pvals_adj < alpha
        significant_genes = gene_names[significant_genes_mask]

        # Prepare the data for this row
        row_data = {
            'vertex': vertex_num,
            'genes': list(significant_genes)
        }

        # If adt_key is provided, add 'stratum' and 'stratum_vertex' columns
        if adt_key is not None:
            row_data['stratum'] = adt_key
            row_data['stratum_vertex'] = f"{adt_key}_{vertex_num}"

        # Append the row to the list
        enriched_genes_data.append(row_data)

    # Convert the list of rows into a pandas DataFrame
    enriched_genes_df = pd.DataFrame(enriched_genes_data)

    # **Sort the DataFrame by the 'vertex' column**
    enriched_genes_df = enriched_genes_df.sort_values('vertex').reset_index(drop=True)

    # Assign to .uns of adata
    adata.uns['genes_enriched_at_each_vertex'] = enriched_genes_df

    return # enriched_genes_df


def get_genes_from_simplex(
    adata: AnnData,
    order_func: Callable = median_difference,
    expression_data_layer: str = None,
    adt_key: tuple[str,...] | None = None
) -> None:
    """
    function to find enriched genes at each archetype.

    Parameters
    ----------
    adata
        :class:`AnnData` object containing the data to analyze.
    order_func
        :class:`Callable`
        The function to use to order the differential expression results.
        Default: :func:`median_difference`
    expression_data_layer
        :class:`str`
        The layer in `adata.layers` to use for differential expression.
        Default: None

    Returns
    -------
    ``None``

    Notes
    -----
    This function computes differential expression, sorts the results, and extracts 
    enriched genes, store them in adata.uns['genes_enriched_at_each_vertex'].

    See Also
    --------
    :func:`compute_differential_expression`
    :func:`sort_differential_expression`
    :func:`extract_enriched_genes`
    """
    if 'simplex' not in adata.uns:
        raise ValueError("'simplex' not found in adata.uns. \
            Please run ``fit_simplex()`` before extracting genes.")

    coords = adata.uns['simplex']['min_simplex_coords']

    #get cells that represent each vertex
    set_cells_that_represent_each_vertex(adata, coords, data_layer='X_pca_reduced')

    #calculate enrichment of genes at each archetype
    mask_columns = adt.get_adata_columns(adata, starts_with=['represents_vertex'])
    compute_differential_expression(adata, mask_columns, layer=None) #layer=None uses adata.X

    #sort the differential expression by median difference, using .X
    sort_differential_expression(
        adata,
        mask_columns, order_func=order_func, layer=expression_data_layer)

    #extract the enriched genes and return as a pd df
    # enriched_genes_df = extract_enriched_genes(adata, adt_key=adt_key)

    #extract enriched genes. The dataframe is stored directly in adata.uns
    extract_enriched_genes(adata, adt_key=adt_key)

    return # enriched_genes_df

def get_genes_from_simplex_adata_dict(
    adata_dict: dict[str, AnnData],
    **kwargs
) -> None:
    """
    function to get the genes enriched at each vertex for a dictionary of :class:`AnnData` objects.

    Parameters
    ----------
    adata_dict
        An :class:`anndict.AnnDict`.

    **kwargs
        Additional keyword arguments to pass to :func:`get_genes_from_simplex`.

    Returns
    -------
    ``None``

    Notes
    -----
    This function applies :func:`get_genes_from_simplex` to each :class:`AnnData` 
    object in ``adata_dict``, modifying them in-place.

    See Also
    --------
    :func:`get_genes_from_simplex`
    """
    adata_dict.fapply(get_genes_from_simplex, **kwargs)

    return # adata_dict
