"""
Functions for interpreting clusters of vertices (also called archetypes).
"""
# pylint: disable=line-too-long

import numpy as np
import pandas as pd
import anndict as adt

from anndict import AdataDict
from scipy.sparse import issparse


def archetype_statistics(
    vertex_metadata: pd.DataFrame,
    cols: list[str],
    qualified_only: bool = True,
    n_top_genes: int | None = 10,
) -> pd.DataFrame:
    """
    Compute statistical summaries and gene frequency tables 
    for each archetype in ``vertex_metadata``.

    Parameters
    ----------
    vertex_metadata
        A DataFrame that contains the metadata, including a ``'archetype'`` 
        column and a ``'genes'`` column (which holds lists of genes for each row).

    cols
        A list of column names (from ``vertex_metadata``) for which unique 
        value counts are computed.

    qualified_only
        If ``True``, only consider rows where the ``'qualifies'`` column is ``True``.

    n_top_genes
        If not ``None``, only up to the first ``n_top_genes`` genes are taken 
        from each vertex (row) in the ``'genes'`` column.

    Returns
    -------
    A new :class:`DataFrame` where each row represents a unique archetype and 
    contains the following columns:
        - ``'archetype'``: The identifier for the archetype.
        - ``'unique_{col}_all'``: The number of unique values in the entire 
        ``vertex_metadata[col]`` column.
        - ``'unique_{col}_in_archetype'``: The number of unique values in the 
        ``vertex_metadata[col]`` for that archetype.
        - ``'gene_frequency'``: A dictionary representing the frequency of genes 
        in the archetype, sorted in descending order.
    """
    # Filter by qualified_only if specified
    df = vertex_metadata.copy()
    if qualified_only and 'qualifies' in df.columns:
        df = df[df['qualifies']]

    # Limit genes per vertex if n_top_genes is specified
    if n_top_genes is not None:
        df['genes'] = df['genes'].apply(lambda genes: genes[:n_top_genes])

    archetypes = df['archetype'].unique()
    result_data = []

    # Process each archetype
    for arch in archetypes:
        archetype_data = {'archetype': arch}

        # Compute gene frequencies for this archetype
        arch_genes = (
            df[df['archetype'] == arch]['genes']
            .explode()
            .value_counts()
            .sort_values(ascending=False)
            .to_dict()
        )
        archetype_data['gene_frequency'] = arch_genes

        # Compute statistics for each requested column
        for col in cols:
            if col in df.columns:
                # Total unique values across all archetypes
                archetype_data[f'unique_{col}_all'] = df[col].nunique()

                # Unique values within this archetype
                archetype_data[f'unique_{col}_in_archetype'] = (
                    df[df['archetype'] == arch][col].nunique()
                )

        result_data.append(archetype_data)

    # Convert to DataFrame
    archetype_stats_df = pd.DataFrame(result_data)

    # Ensure consistent column ordering
    column_order = ['archetype']
    for col in cols:
        column_order.extend([f'unique_{col}_all', f'unique_{col}_in_archetype'])
    column_order.append('gene_frequency')

    # Reorder columns and sort by archetype
    archetype_stats_df = archetype_stats_df[column_order].sort_values('archetype').reset_index(drop=True)

    return archetype_stats_df



def archetype_annotation(
    archetype_stats_df: pd.DataFrame,
    new_col_name: str = "archetype_annotation",
) -> pd.DataFrame:
    """
    Process each row of archetype statistics DataFrame by running biological process analysis
    on frequent genes and add results to a new column.
    
    Parameters
    ----------
    archetype_stats_df
        :class:`DataFrame` output from :func:`archetype_statistics`, containing a ``'gene_frequency'`` 
        column with dictionaries of gene frequencies

    new_col_name
        Name of the new column to add containing biological process analysis results.

    Returns
    -------
    A :class:`DataFrame` with a new column containing biological process analysis results.
    """
    def process_gene_list(gene_freq_dict):
        # Sort genes by frequency in descending order and filter for freq > 1
        frequent_genes = [
            gene for gene, freq in sorted(
                gene_freq_dict.items(),
                key=lambda x: x[1],
                reverse=True
            ) if freq > 1
        ]

        # Return None if no genes meet criteria
        if not frequent_genes:
            return None

        # Run biological process analysis
        try:
            return adt.ai_biological_process(frequent_genes)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error processing genes: {e}")
            return None

    # Create a copy of the input DataFrame
    annotated_archetype_stats_df = archetype_stats_df.copy()

    # Apply the processing function to each row's gene frequency dictionary
    annotated_archetype_stats_df[new_col_name] = annotated_archetype_stats_df['gene_frequency'].apply(process_gene_list)

    return annotated_archetype_stats_df


def archetype_expression(
    archetypes: pd.DataFrame,
    archetype_stats: pd.DataFrame,
    adata_fit: AdataDict,
    expression_layer: str = "raw_counts",
) -> pd.DataFrame:
    """
    Calculate and organize gene expression statistics across archetypes and strata.

    This function processes gene expression data for a set of archetypes and their associated strata,
    calculating statistics such as mean expression, standard deviation, and the number of cells. 
    It also organizes the relationships between genes, archetypes, and their frequencies/ranks for 
    further analysis and visualization.

    Parameters
    ----------
    archetypes
        :class:`DataFrame` containing archetype information with the following columns:
        - ``'archetype'``: Identifier for each archetype.
        - ``'stratum'``: Stratum associated with the archetype.
        - ``'cell_indices'``: List of cell IDs belonging to the stratum for the given archetype.

    archetype_stats
        :class:`DataFrame` containing gene statistics for each archetype, with columns:
        - ``'archetype'``: Identifier for each archetype.
        - ``'gene_frequency'``: Dictionary mapping genes to their frequency in the archetype.

    adata_fit
        An :class:`AdataDict` object with polytopal fits.

    Returns
    -------
    A :class:`DataFrame` containing the following columns:
        - ``'gene'``: Gene name.
        - ``'expression_mean'``: Mean expression value for the gene in the archetype.
        - ``'expression_sd'``: Standard deviation of the expression values.
        - ``'n_cells'``: Number of cells contributing to the calculation.
        - ``'gene_frequency'``: Frequency of the gene in the archetype.
        - ``'gene_rank'``: Rank of the gene in the archetype based on frequency.
        - ``'gene_from_archetype'``: Archetype associated with the gene frequency and rank.
        - ``'expression_in_archetype'``: Archetype where the gene's expression was measured.
        - ``'plot_order'``: Sequential order for visualization, based on sorting.

    Notes
    ------
    - The input ``archetypes`` is filtered to include 
    only valid archetypes present in ``archetype_stats``.
    - Gene frequencies and ranks are computed for each archetype based on ``archetype_stats``.
    - Expression statistics are computed for each gene across 
    all strata associated with an archetype.
    - The resulting :class:`DataFrame` is sorted by ``'gene_from_archetype'``, 
    ``'expression_in_archetype'``, and ``'gene_rank'``, and includes a ``'plot_order'`` 
    column for visualization.
    """
    #ensure expression layer is in data


    # Step 0: Filter archetypes based on archetype_stats
    valid_archetypes = set(archetype_stats['archetype'])
    archetypes = archetypes[archetypes['archetype'].isin(valid_archetypes)]

    # Step 1: Build mapping from archetype to cells per stratum
    archetype_to_cells = {}
    for _, row in archetypes.iterrows():
        archetype = row['archetype']
        stratum = row['stratum']
        cell_ids = row['cell_indices']
        if archetype not in archetype_to_cells:
            archetype_to_cells[archetype] = {}
        if stratum not in archetype_to_cells[archetype]:
            archetype_to_cells[archetype][stratum] = []
        archetype_to_cells[archetype][stratum].extend(cell_ids)

    # Step 2: Build mappings for gene to archetypes, gene_frequency, gene_rank
    gene_to_archetypes = {}
    gene_archetype_frequency = {}  # (gene, archetype) -> frequency
    gene_archetype_rank = {}       # (gene, archetype) -> rank
    all_genes = set()
    for _, row in archetype_stats.iterrows():
        archetype = row['archetype']
        gene_frequency = row['gene_frequency']
        # Rank genes based on frequency
        ranked_genes = sorted(gene_frequency.items(), key=lambda x: x[1], reverse=True)
        gene_rank = {gene: rank + 1 for rank, (gene, _) in enumerate(ranked_genes)}
        for gene, freq in gene_frequency.items():
            all_genes.add(gene)
            # Update gene_to_archetypes
            gene_to_archetypes.setdefault(gene, set()).add(archetype)
            # Store gene frequency and rank
            gene_archetype_frequency[(gene, archetype)] = freq
            gene_archetype_rank[(gene, archetype)] = gene_rank[gene]

    # Step 3: Generate all combinations of genes and archetypes with uniqueness
    result_rows = []
    for archetype, cells_per_stratum in archetype_to_cells.items():
        # Process all genes
        for gene in all_genes:
            gene_expr_values = []
            for stratum, cell_ids in cells_per_stratum.items():
                adata = adata_fit.get(stratum)
                if adata is None:
                    continue
                if expression_layer not in adata.layers.keys():
                    raise ValueError(f"adata_fit[{stratum}] does not \
                        contain the layer {expression_layer}")
                # Map cell IDs to indices
                cell_mask = adata.obs_names.isin(cell_ids)
                cell_indices = np.where(cell_mask)[0]
                if len(cell_indices) == 0:
                    continue
                # Process expression for the gene
                if gene not in adata.var_names:
                    continue
                gene_index = adata.var_names.get_loc(gene)
                if issparse(adata.layers[expression_layer]):
                    expr_values = adata.layers[expression_layer][cell_indices, gene_index].toarray().flatten()
                else:
                    expr_values = adata.layers[expression_layer][cell_indices, gene_index].flatten()
                gene_expr_values.extend(expr_values)
            # Calculate mean and sd
            if gene_expr_values:
                expression_mean = np.mean(gene_expr_values)
                expression_sd = np.std(gene_expr_values, ddof=1)
                n_cells = len(gene_expr_values)
            else:
                expression_mean = np.nan
                expression_sd = np.nan
                n_cells = 0
            # For each gene_from_archetype, append a separate row
            gene_from_archetypes = gene_to_archetypes.get(gene, set())
            if not gene_from_archetypes:
                # If the gene is not associated with any archetype, handle it
                result_rows.append({
                    'gene': gene,
                    'expression_mean': expression_mean,
                    'expression_sd': expression_sd,
                    'n_cells': n_cells,
                    'gene_frequency': np.nan,
                    'gene_rank': np.nan,
                    'gene_from_archetype': np.nan,
                    'expression_in_archetype': archetype
                })
            else:
                for gene_from_archetype in gene_from_archetypes:
                    # Get gene_frequency and gene_rank for this gene in this gene_from_archetype
                    gene_frequency = gene_archetype_frequency.get((gene, gene_from_archetype), np.nan)
                    gene_rank = gene_archetype_rank.get((gene, gene_from_archetype), np.nan)
                    # Append the result
                    result_rows.append({
                        'gene': gene,
                        'expression_mean': expression_mean,
                        'expression_sd': expression_sd,
                        'n_cells': n_cells,
                        'gene_frequency': gene_frequency,
                        'gene_rank': gene_rank,
                        'gene_from_archetype': gene_from_archetype,
                        'expression_in_archetype': archetype
                    })
    # Create the DataFrame
    result_df = pd.DataFrame(result_rows)

    # Convert 'gene_from' and 'expression_in_archetype' to string types
    result_df['gene_from_archetype'] = result_df['gene_from_archetype'].astype(str)
    result_df['expression_in_archetype'] = result_df['expression_in_archetype'].astype(str)

    # Ensure 'gene_rank' is numeric for sorting
    result_df['gene_rank'] = pd.to_numeric(result_df['gene_rank'], errors='coerce')

    # Sort the DataFrame according to 'gene_from_archetype', 'expression_in_archetype', and 'gene_rank'
    result_df.sort_values(by=['gene_from_archetype', 'expression_in_archetype', 'gene_rank'], inplace=True)

    # Assign 'plot_order' based on the sorted DataFrame
    result_df['plot_order'] = range(1, len(result_df) + 1)

    return result_df
