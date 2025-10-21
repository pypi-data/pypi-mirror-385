"""
This module contains utility functions for preprocessing.
"""

import numpy as np
from anndata import AnnData

def filter_adata_by_percentiles(
    adata: AnnData,
    cols_percentiles: dict[str, tuple[float, str]]
) -> AnnData:
    """
    Filter an AnnData object by applying percentile cutoffs to specified columns in ``adata.obs``.

    This function computes percentile thresholds for each specified column and removes cells
    that fall above or below these thresholds, depending on the direction specified for each column.
    All thresholds are calculated before any filtering is performed.

    Parameters
    ----------
    adata
        The AnnData object containing single-cell data. 
        Filtering is performed on columns in ``adata.obs``.

    cols_percentiles
        A dictionary mapping column names to a tuple of (percentile, direction), where
        ``percentile`` is a float or int (0-100), and ``direction`` is either ``'upper'`` 
        (remove cells above the threshold) or ``'lower'`` (remove cells below the threshold).

    Returns
    -------
    The filtered AnnData object, with cells not meeting the percentile criteria removed.

    Examples
    --------
    .. code-block:: python

        # Remove cells in the top 10% of pct_counts_mt and n_genes
        adata_filtered = filter_adata_by_percentiles(
            adata,
            cols_percentiles={
                'pct_counts_mt': (90, 'upper'),
                'n_genes': (90, 'upper')
            }
        )

    """

    # Extract relevant columns once
    cols = list(cols_percentiles.keys())
    obs_df = adata.obs[cols]

    # Calculate thresholds
    thresholds = {
        col: (
            np.percentile(obs_df[col].values, percentile),
            direction
        )
        for col, (percentile, direction) in cols_percentiles.items()
    }

    # Prepare comparison functions
    direction_funcs = {'upper': np.less, 'lower': np.greater}

    # Build masks using list comprehension and logical_and.reduce
    masks = [
        direction_funcs[direction](obs_df[col].values, cutoff)
        for col, (cutoff, direction) in thresholds.items()
    ]

    # Combine masks using logical AND
    if masks:
        combined_mask = np.logical_and.reduce(masks)
    else:
        combined_mask = np.ones(obs_df.shape[0], dtype=bool)

    # Filter the adata object
    adata = adata[combined_mask, :]

    return adata
