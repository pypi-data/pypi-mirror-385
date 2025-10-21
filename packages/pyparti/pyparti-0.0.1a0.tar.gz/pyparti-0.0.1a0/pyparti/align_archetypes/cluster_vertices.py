"""
This module contains the functions to cluster the vertices. These clusters are called archetypes.
"""
# pylint: disable=line-too-long

import numpy as np
import pandas as pd
import anndict as adt
import igraph

from igraph import Graph
from anndict import AdataDict


def aggregate_enriched_genes(
    adata_dict: AdataDict,
    cols: list[str],
) -> pd.DataFrame:
    """
    Aggregate enriched genes across all :class:`AnnData` in ``adata_dict``, 
    combining them with metadata based on specified columns. Additionally, include 
    a column with the list of cell indices that represent each vertex.

    Parameters
    ----------
    adata_dict
        A dictionary where keys are identifiers and values are :class:`AnnData` objects.

    cols
        A list of columns from ``adata.obs`` that should uniquely define metadata for 
        each :class:`AnnData` object.

    Returns
    -------
        A DataFrame where each row contains a gene, its associated metadata, and 
        the list of cell indices representing the vertex, concatenated from all the 
        :class:`AnnData` objects in ``adata_dict``.

    Raises
    ------
    :class:`ValueError`
        If the combination of columns in ``cols`` does not result in a unique row 
        for a given :class:`AnnData` object.
    """

    def get_genes_from_adata(adata):
        return adata.uns['genes_enriched_at_each_vertex']

    def get_metadata_from_adata(adata, cols):
        # Get the unique rows based on the specified columns
        df = adata.obs[cols].drop_duplicates().reset_index(drop=True)

        # Check if there's exactly one unique row
        if df.shape[0] != 1:
            raise ValueError(f"The combination of columns {cols} in adata.obs \
                does not have a single unique row")

        # Return the unique row as a DataFrame
        return df

    def get_cell_indices_per_vertex(adata):
        # Get columns that start with 'represents_vertex'
        mask_columns = adt.get_adata_columns(adata, starts_with=['represents_vertex'])

        vertex_cell_indices_list = []
        for col in mask_columns:
            vertex_number = int(col.replace('represents_vertex_', ''))
            cell_indices = adata.obs.index[adata.obs[col]].tolist()
            vertex_cell_indices_list.append({'vertex': vertex_number, 'cell_indices': cell_indices})

        # Return as a DataFrame
        return pd.DataFrame(vertex_cell_indices_list)

    enriched_genes_dict = adata_dict.fapply(get_genes_from_adata)
    metadata_dict = adata_dict.fapply(get_metadata_from_adata, cols=cols)
    cell_indices_dict = adata_dict.fapply(get_cell_indices_per_vertex)

    # Perform cross join and merge on 'vertex' to include cell indices
    vertex_metadata = pd.concat(
        [
            enriched_genes_dict[key]
            .merge(metadata_dict[key], how='cross')
            .merge(cell_indices_dict[key], on='vertex')
            for key in enriched_genes_dict.keys()
        ],
        ignore_index=True
    )

    return vertex_metadata


def build_adjacency_matrix(
    enriched_genes_df: pd.DataFrame,
    n_top_genes: int,
) -> np.ndarray:
    """
    Builds an adjacency matrix in a vectorized manner that defines the connectedness of each row
    in ``enriched_genes_df``. The connectedness is calculated as the length of the intersection 
    of the top ``n_top_genes`` between each pair of rows.

    Parameters
    ----------
    enriched_genes_df
        A :class:`DataFrame` with ``'vertex'`` and ``'genes'`` columns, 
        where ``'genes'`` contains the list of enriched genes for each vertex.

    n_top_genes
        Number of top genes to consider for each vertex.

    Returns
    -------
        An adjacency matrix where the value at (i, j) represents the length of the
        intersection of the top ``n_top_genes`` genes between row i and row j.
    """
    # Extract the top n genes for each vertex
    top_genes_list = [set(row['genes'][:n_top_genes]) for _, row in enriched_genes_df.iterrows()]

    # Create a unique list of all genes in the top N genes
    unique_genes = sorted(set.union(*top_genes_list))

    # Create a binary matrix where each row is a binary vector indicating the presence of a gene
    binary_matrix = np.array([[1 if gene in gene_set else 0 for gene in unique_genes] for gene_set in top_genes_list])

    # Compute the adjacency matrix as the intersection size (dot product of binary vectors)
    adjacency_matrix = binary_matrix.dot(binary_matrix.T)

    # Convert to pandas DataFrame for readability
    # adjacency_df = pd.DataFrame(adjacency_matrix, index=enriched_genes_df['vertex'], columns=enriched_genes_df['vertex'])

    return adjacency_matrix


def create_graph_from_adjacency_matrix(
    adjacency_matrix: np.ndarray,
) -> igraph.Graph:
    """
    Create an undirected graph from an adjacency matrix.

    Parameters
    ----------
    adjacency_matrix
        An adjacency matrix where the value at (i, j) represents the length of the
        intersection of the top ``n_top_genes`` genes between row i and row j.

    Returns
    -------
        An undirected graph where the value at (i, j) represents the length of the
        intersection of the top ``n_top_genes`` genes between row i and row j.

    Examples
    --------

    .. code-block:: python

        import numpy as np

        adjacency_matrix = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
        graph = create_graph_from_adjacency_matrix(adjacency_matrix)

    """

    #For original R behaviour
    # # Ensure the adjacency matrix is of integer type
    # adjacency_matrix = adjacency_matrix.astype(int)

    # # Remove diagonal entries to avoid self-loops
    # np.fill_diagonal(adjacency_matrix, 0)

    # edge_list = []
    # num_nodes = adjacency_matrix.shape[0]

    # # Iterate over the upper triangle of the adjacency matrix
    # for i in range(num_nodes):
    #     for j in range(i+1, num_nodes):
    #         n_edges = adjacency_matrix[i, j]
    #         if n_edges > 0:
    #             # Add multiple edges between nodes i and j
    #             edges = [(i, j)] * n_edges
    #             edge_list.extend(edges)

    # # Create an undirected multigraph from the edge list
    # G = Graph(edges=edge_list, directed=False)

    # return G

    # Streamlined behaviour for python

    # Convert the numpy array to a list of lists for igraph compatibility
    # Create the graph without self-loops
    g = Graph.Weighted_Adjacency(adjacency_matrix.tolist(), mode=igraph.ADJ_UNDIRECTED, attr='weight', loops=False)

    return g


def determine_resolution(
    vertex_graph: igraph.Graph,
    vertex_metadata: pd.DataFrame,
    repro_cols: list[str] | None = None,
) -> float:
    """
    Determines an optimal resolution for the Leiden algorithm to achieve a target number of communities (archetypes).

    Parameters
    ----------
    vertex_graph
        The graph on which community detection is performed.

    vertex_metadata
        Metadata for vertices, including a ``"stratum"`` and ``"qualifies"`` column to filter and count archetypes.

    Returns
    -------
    A resolution value.
    """

    resolution = 0.1
    step_size = 0.1
    max_iterations = 20

    # Set the target number of archetypes based on the average number of vertices per stratum
    target_archetypes = vertex_metadata.groupby("stratum")["vertex"].max().add(1).mean()

    previous_resolution = resolution
    previous_num_archetypes = None

    for _ in range(max_iterations):
        # Perform community detection
        aligned_vertices = vertex_graph.community_leiden(weights='weight', resolution=resolution)

        # Filter the vertex metadata to include only qualifying vertices
        filtered_vertex_metadata = filter_vertices(
            aligned_vertices,
            vertex_metadata=vertex_metadata,
            repro_cols=repro_cols,
        )
        num_archetypes = filtered_vertex_metadata[filtered_vertex_metadata["qualifies"]]["archetype"].nunique()

        # Check if the target number of archetypes is reached
        if num_archetypes <= target_archetypes:
            break  # Stop if the current number of archetypes is close enough to the target

        # Check if increasing the resolution has caused num_archetypes to start decreasing
        if previous_num_archetypes is not None and num_archetypes < previous_num_archetypes:
            resolution = previous_resolution  # Revert to the previous resolution
            break

        # Update previous values and increase the resolution parameter
        previous_resolution = resolution
        previous_num_archetypes = num_archetypes
        resolution += step_size

    return resolution


def align_vertices(
    vertex_metadata: pd.DataFrame,
    resolution: float | None = None,
    repro_cols: list[str] | None = None,
) -> igraph.Graph:
    """
    Clusters vertices based on their enriched genes.

    Parameters
    ----------
    vertex_metadata
        Metadata for vertices, including a ``"stratum"`` and ``"qualifies"`` 
        column to filter and count archetypes.

    resolution
        The resolution parameter for the Leiden algorithm. If ``None``, 
        the resolution is determined automatically.

    repro_cols
        Columns to use for reproducibility filtering. If ``None``, 
        no reproducibility filtering is performed.

    Returns
    -------
    A graph where vertices are grouped based on their enriched genes.
    """

    # Construct the adjacency matrix
    adjacency_matrix = build_adjacency_matrix(vertex_metadata, n_top_genes=10)

    # Create a graph from the adjacency matrix
    vertex_graph = create_graph_from_adjacency_matrix(adjacency_matrix)

    #determine cluster resolution if not supplied
    if resolution is None:
        resolution = determine_resolution(vertex_graph, vertex_metadata, repro_cols=repro_cols)

    # Perform Leiden clustering
    aligned_vertices = vertex_graph.community_leiden(weights='weight', resolution=resolution)

    return aligned_vertices


def filter_vertices(
    aligned_vertices: igraph.Graph,
    vertex_metadata: pd.DataFrame,
    repro_cols: list[str] | None = None,
    repro_thresh: float = 2/3,
) -> pd.DataFrame:
    """
    Filter vertices based on uniqueness criteria within archetypes.

    Parameters
    ----------
    aligned_vertices
        Object containing membership information for vertices

    vertex_metadata
        DataFrame containing metadata for vertices

    Returns
    -------
    Input DataFrame with added ``'archetype'`` and ``'qualifies'`` columns.
    ``'qualifies'`` is ``True`` for archetypes that contain at least 2/3 of all possible unique values
    for each column in the dataset.
    """
    #if repro cols is None, no reproducibility filter is desired, so return all vertices
    if repro_cols is None:
        return vertex_metadata

    # Create a copy to avoid modifying the input
    filtered_vertex_metadata = vertex_metadata.copy()

    # Add the archetype index to vertex_metadata
    filtered_vertex_metadata['archetype'] = aligned_vertices.membership

    # Calculate total unique values for each column in the entire dataset
    total_uniques = vertex_metadata[repro_cols].nunique()

    # Group by archetype and compute ratio of unique values compared to total possible uniques
    group_stats = filtered_vertex_metadata.groupby('archetype')[repro_cols].apply(
        lambda group: (
            # For each column, count unique values and divide by total possible uniques
            (group.nunique() > 1) &
            (group.nunique() >= round((repro_thresh) * total_uniques))
        )  # Drop archetype column from computation
    )

    # Determine if all columns qualify for each archetype
    qualifies_series = group_stats.all(axis=1)

    # Map the qualification results back to the original rows
    filtered_vertex_metadata['qualifies'] = filtered_vertex_metadata['archetype'].map(qualifies_series)

    return filtered_vertex_metadata


def archetype_alignment(
    adata_dict: AdataDict,
    repro_cols: list[str] | None = None,
    addtl_metadata_cols: list[str] | None = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Aligns vertices based on their enriched genes.

    Parameters
    ----------
    adata_dict
        A dictionary where keys are identifiers and values are :class:`AnnData` objects.

    repro_cols
        Columns to use for reproducibility filtering. If ``None``, no 
        reproducibility filtering is performed.

    addtl_metadata_cols
        Additional columns to include in the metadata. If ``None``, no additional metadata 
        is included.

    Returns
    -------
    A DataFrame with the archetype index and whether it qualifies for each vertex.
    """

    #get vertices and their metadata. the df below has 1 row per vertex.
    vertex_metadata = aggregate_enriched_genes(
        adata_dict=adata_dict,
        cols=repro_cols + addtl_metadata_cols,
    )

    #align the vertices
    resolution = kwargs.pop('resolution', None) # Default behaviour is to set resolution to None to determine value automatically
    aligned_vertices = align_vertices(
        vertex_metadata=vertex_metadata,
        resolution=resolution,
        repro_cols=repro_cols,
    )

    #filter the vertices and return as metadata
    repro_thresh = kwargs.pop('repro_thresh', 2/3) # set default at 2/3
    vertex_metadata = filter_vertices(
        aligned_vertices=aligned_vertices,
        vertex_metadata=vertex_metadata,
        repro_cols=repro_cols,
        repro_thresh=repro_thresh,
    )

    return vertex_metadata
