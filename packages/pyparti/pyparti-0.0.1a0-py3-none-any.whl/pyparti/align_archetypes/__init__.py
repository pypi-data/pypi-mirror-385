"""
Functions for clustering vertices to identify archetypes and interpret their biological meaning.
"""

from .cluster_vertices import (
    aggregate_enriched_genes,
    build_adjacency_matrix,
    create_graph_from_adjacency_matrix,
    determine_resolution,
    align_vertices,
    filter_vertices,
    archetype_alignment,
)

from .interpret_clusters import (
    archetype_statistics,
    archetype_annotation,
    archetype_expression,
)

__all__ = [
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
]