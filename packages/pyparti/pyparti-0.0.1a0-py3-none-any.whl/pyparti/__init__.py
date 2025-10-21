"""
Main module for pyparti.
"""

__version__ = "0.0.1"
__author__ = "ggit12"

#import pyparti namespace
from . import preprocess
from . import fit_polytope
from . import get_genes
from . import align_archetypes
from . import plot

from .preprocess import (
    filter_adata_by_percentiles,
    preprocess_entire_adata_for_parti,
    preprocess_adata_subset_for_parti,
    preprocess_adata_dict_for_parti,
    protein_coding,
    genes_artefact,
)

from .fit_polytope import (
    sdvmm,
    # sisal,
    pcha,
    # maxvoldual,
    calculate_convex_hull_volume,
    find_min_polytope_adata,
    find_min_polytope_main,
    calculate_p_value,
    fit_polytope,
    fit_polytope_adata_dict,
    get_significant_fits_adata_dict,
)

from .get_genes import (
    median_difference,
    get_genes_from_simplex,
    get_genes_from_simplex_adata_dict,
)

from .align_archetypes import (
    aggregate_enriched_genes,
    build_adjacency_matrix,
    create_graph_from_adjacency_matrix,
    determine_resolution,
    align_vertices,
    filter_vertices,
    archetype_alignment,
    archetype_statistics,
    archetype_annotation,
    archetype_expression,
)

from .plot import (
    plot_p_value_histogram,
    plot_archetype_contents,
    plot_archetype_expression,
    plot_gene_frequencies,
    display_gene_frequencies,
)


__all__ = [

    # ------- preprocess -------
    # utils
    "filter_adata_by_percentiles",

    # preprocess
    "preprocess_entire_adata_for_parti",
    "preprocess_adata_subset_for_parti",
    "preprocess_adata_dict_for_parti",

    # dat (gene lists)
    "protein_coding",
    "genes_artefact",

    # ------- fit_polytope -------
    # algs
    "sdvmm",
    # "sisal",
    "pcha",
    # "maxvoldual",

    # calculate_hull_volume
    "calculate_convex_hull_volume",

    # find_min_polytope
    "find_min_polytope_adata",
    "find_min_polytope_main",

    # significance
    "calculate_p_value",

    # fit_polytope
    "fit_polytope",
    "fit_polytope_adata_dict",

    # filter_fits
    "get_significant_fits_adata_dict",

    # ------- get_genes -------
    # differential_expression
    'median_difference',

    # get_genes
    'get_genes_from_simplex',
    'get_genes_from_simplex_adata_dict',

    # ------- align_archetypes -------
    # cluster_vertices
    'aggregate_enriched_genes',
    'build_adjacency_matrix',
    'create_graph_from_adjacency_matrix',
    'determine_resolution',
    'align_vertices',
    'filter_vertices',
    'archetype_alignment',

    # interpret_clusters
    'archetype_statistics',
    'archetype_annotation',
    'archetype_expression',

    # ------- plot -------
    # p_value
    'plot_p_value_histogram',

    # contents
    'plot_archetype_contents',

    # expression
    'plot_archetype_expression',

    # gene_frequencies
    'plot_gene_frequencies',
    'display_gene_frequencies',

]
