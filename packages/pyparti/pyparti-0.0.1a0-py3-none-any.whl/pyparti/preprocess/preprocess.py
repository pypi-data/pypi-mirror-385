"""
This module contains the preprocessing functions for the pyparti package.
"""
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import csv
import gc
import warnings

from importlib import resources

import numpy as np
import scanpy as sc
from anndata import AnnData

from anndict import (
    adata_dict_fapply,
    AdataDict,
    pca_density_filter_main,
)

from .utils import filter_adata_by_percentiles

#get artefact gene list
genes_artefact_path = resources.files('pyparti').joinpath(
    'dat/genes_affected_by_dissociation_and_processing_time.csv'
)
with open(genes_artefact_path, 'r', encoding='utf-8') as file:
    genes_artefact = list(csv.reader(file, delimiter=','))
genes_artefact = [i[0] for i in genes_artefact[1:]]  #skip first line because it is column header


#load list of protein-coding genes
protein_coding_path = resources.files('pyparti').joinpath(
    'dat/protein_coding_genes_list.csv'
)
with open(protein_coding_path, 'r', encoding='utf-8') as file:
    protein_coding = list(csv.reader(file, delimiter=','))
protein_coding = [i[6] for i in protein_coding[1:] if i[6]] #extra if at the end removes empty genes (i.e. "") from the list


def preprocess_entire_adata_for_parti( # pylint: disable=dangerous-default-value
    adata: AnnData,
    cols_percentiles: dict[str, tuple[float | int, str]] = {
        'pct_counts_mt': (90, 'upper'),
        'pct_counts_artefact': (90, 'upper'),
        'n_genes': (90, 'upper'),
        'total_counts': (90, 'upper'),
        'n_counts_UMIs': (90, 'upper')
    },
) -> AnnData:
    """
    This is a preprocessing function to run on an overall study's adata before running parti.

    This function should be run on adata before running
    :func:`preprocess_adata_for_parti` on subsets of the overall adata.

    Parameters
    ----------
    adata
        The :class:`AnnData` object to preprocess.

    cols_percentiles
        A dictionary mapping column names to a tuple of (percentile, direction), where
        ``percentile`` is a float or int (0-100), and ``direction`` is either ``'upper'``
         (remove cells above the threshold) or ``'lower'`` (remove cells below the threshold).

    Returns
    -------
    The filtered :class:`AnnData` object, with cells not meeting the percentile criteria removed.

    Examples
    --------
    .. code-block:: python
        # Filter adata using default percentiles and qc metrics
        adata = preprocess_entire_adata_for_parti(adata)

        # Filter adata using custom percentiles for selected columns
        adata = preprocess_entire_adata_for_parti(adata, cols_percentiles={
            'pct_counts_mt': (95, 'upper'),
            'n_genes': (85, 'upper')
        })

    """

    if 'raw_counts' not in adata.layers.keys():
        raise ValueError("adata does not have a 'raw_counts' layer. \
                         Please add a raw counts layer to the adata object \
                         before running this function.")

    #set adata to use to be raw counts
    adata.X = adata.layers['raw_counts'].copy()

    #do preprocess workflow
    sc.pp.filter_genes(adata, min_cells = 5)

    #add annotation to artefact genes
    # global genes_artefact
    adata.var['artefact'] = [(i in genes_artefact) for i in adata.var_names]

    #add annotaiton to mitochondrial genes
    adata.var['mt'] = adata.var_names.str.startswith("MT-")

    #calculate mitochondrial and artefact score
    sc.pp.calculate_qc_metrics(
        adata,
        qc_vars=['mt','artefact'],
        percent_top=None,
        log1p=False,
        inplace=True,
        layer = 'raw_counts',
    )

    #define qc cutoffs based on percentiles and remove cells outside of these cutoffs
    adata = filter_adata_by_percentiles(adata, cols_percentiles)

    #run line to avoid unknown error: ValueError: could not convert integer scalar
    adata = adata.copy()

    #set adata to use to be raw counts
    adata.X = adata.layers['raw_counts'].copy()

    #add key to dat.var to indicate whether gene is protein-coding
    # global protein_coding
    adata.var['protein_coding'] = [(i in protein_coding) for i in adata.var_names]

    #add key to adata.var to indicate whether gene is protein-coding and not (mitochondrial or artefact)
    adata.var['protein_coding_not_mt_artefact'] = [(i in protein_coding) and (not j) for i,j in zip(adata.var_names, adata.var.mt | adata.var.artefact)]

    #caluculate total counts per cell for protein-coding (and not mt or artefact) genes only
    adata.obs['total_counts_protein_coding'] = adata[:,adata.var['protein_coding_not_mt_artefact']].X.sum(axis=1)

    # Filter out cells with low protein-coding gene expression
    adata = adata[adata.obs['total_counts_protein_coding'] > 100, :]

    #count normalize data using only protein_coding_not_mt_artefact genes
    subset_column = 'protein_coding_not_mt_artefact'

    # Step 1: Filter the AnnData object to only include the genes in the subset
    subset_genes = adata[:, adata.var[subset_column]].copy()

    # Step 2: Normalize the total counts to a target sum of 1e4 for the subset
    sc.pp.normalize_total(subset_genes, target_sum=1e4)

    adata = adata.copy()

    # Step 3: Replace the counts in the original adata with the normalized values from the subset
    adata_X_lil = adata.X.tolil()
    adata_X_lil[:, adata.var[subset_column]] = subset_genes.X.tolil()
    adata.X = adata_X_lil.tocsr()

    gc.collect()
    print('normalized raw counts')

    return adata

def preprocess_adata_subset_for_parti(
    adata: AnnData,
    adt_key: tuple[str, ...] | None = None,
) -> AnnData | None:
    """
    This function is a preprocessing pipeline to be run on subsets of adata, directly before parti analysis.

    The design is to first run :func:`preprocess_entire_adata_for_parti` first on the entire data, 
    then run :func:`preprocess_adata_subset_for_parti` on subsets of the adata (i.e. separately on donor-tissue-celltypes).

    Parameters
    ----------
    adata
        The :class:`AnnData` object to preprocess.

    adt_key
        Optional key used internally to identify the adata object.

    Returns
    -------
    The filtered :class:`AnnData` object, with cells not meeting the percentile criteria removed.

    Notes
    -----
    If the adata contains fewer than 50 cells before or after pca-density filtering, this function will return ``None``. 
    This is to avoid running parti on datasets that are too small to reliably detect significant polytopes.

    Examples
    --------
    .. code-block:: python

        adata = preprocess_adata_subset_for_parti(adata)
    """

    if adata.n_obs < 50:
        warnings.warn(f"adata {adt_key} contains fewer than 50 cells. \
            We require at least 50 cells. Returning ``None`` for this adata.")
        return None

    subset_column = 'protein_coding_not_mt_artefact'  # This is the column name in adata.var that indicates which genes to use for PCA

    if subset_column not in adata.var.columns:
        raise ValueError(f"adata.var does not have a {subset_column} column. Please run preprocess_overall_adata_for_parti()")

    # Identify the subset of genes
    subset_genes = adata[:, adata.var[subset_column]].copy()

    # Create an array to map subset_genes indices to original adata indices
    original_indices = np.where(adata.var[subset_column])[0]

    subset_genes.X = subset_genes.X.toarray()

    adata = adata.copy()

    adata.X = adata.X.toarray()

    gc.collect()

    # Add density of points on pca to data
    density, cutoff, genes_included_indices = pca_density_filter_main(subset_genes.X)

    # Map genes_included_indices back to the original indices in adata
    included_original_indices = original_indices[genes_included_indices]

    # Create a new column in adata.var to indicate which genes were included
    adata.var['included_in_density_calculation'] = False  # initialize all as False
    adata.var.loc[adata.var.index[included_original_indices], 'included_in_density_calculation'] = True

    if density is None:
        raise ValueError("All variables are constant protein-coding genes are constant")

    # Continue with processing if pca_data is valid
    adata.obs['pca_density'] = density

    # Filter out low-density cells
    temp = adata[adata.obs['pca_density'] > cutoff, :].copy()
    adata = temp
    del temp

    #only return if there are more than 50 cells post-pca-filtering
    if adata.n_obs < 50:
        warnings.warn(f"After pca filtering, adata {adt_key} contains fewer than 50 cells. \
            We require at least 50 cells. Returning ``None`` for this adata.")
        return None

    gc.collect()

    #define a 1k cell subsample without replacement
    # Check if there are more than 1000 cells
    if adata.n_obs > 1000:
        # Initialize all cells as False for the '1k_subsample' column
        adata.obs['1k_subsample'] = False

        # Randomly select 1000 cells without replacement
        subsampled_indices = np.random.choice(adata.obs_names, 1000, replace=False)

        # Set True for the selected 1000 cells
        adata.obs.loc[subsampled_indices, '1k_subsample'] = True
    else:
        # If there are 1000 or fewer cells, mark all cells as part of the subsample
        adata.obs['1k_subsample'] = True

    return adata


def preprocess_adata_dict_for_parti(
    adata_dict: AdataDict,
    **kwargs,
) -> AdataDict:
    """
    This function is a preprocessing pipeline to be run on a dictionary of adata objects,
    directly before parti analysis.

    Parameters
    ----------
    adata_dict
        The :class:`AdataDict` object to preprocess.

    kwargs
        Additional keyword arguments to pass to :func:`preprocess_adata_subset_for_parti`.

    Returns
    -------
    The filtered :class:`AdataDict` object, with cells not meeting the percentile criteria removed.

    Examples
    --------
    .. code-block:: python

        filtered_preprocessed_adata_dict = preprocess_adata_dict_for_parti(adata_dict)
    """

    #preprocess each adata in adata_dict
    adata_dict = adata_dict_fapply(
        adata_dict,
        preprocess_adata_subset_for_parti,
        return_as_adata_dict=True,
        **kwargs,
    )

    #drop empty adata (they didn't make it through the filters)
    mask = adata_dict.fapply(lambda adata: isinstance(adata, AnnData))
    adata_dict.index_bool(mask, inplace=True) # This returns `None`
    return adata_dict
