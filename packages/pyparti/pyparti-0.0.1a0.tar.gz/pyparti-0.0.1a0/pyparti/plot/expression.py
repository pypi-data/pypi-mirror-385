"""
Functions for plotting gene expression of archetypes.
"""
# pylint: disable=line-too-long

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import colormaps


def plot_archetype_expression(
    archetype_expression: pd.DataFrame,
    max_genes: int = 3,
    adt_key: tuple[str,...] | None = None,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """
    Plots the expression levels of genes across archetypes in a bar chart format.

    This function visualizes gene expression in archetypes based on 
    the output dataframe from :func:`archetype_expression`.

    Parameters
    ----------
    archetype_expression
        :class:`DataFrame` containing the following columns:
        - ``'gene_from_archetype'``: The archetype from which the gene originates.
        - ``'gene'``: The gene name.
        - ``'expression_in_archetype'``: The archetype where the expression is measured.
        - ``'expression_mean'``: The mean expression level of the gene.
        - ``'plot_order'``: Order of genes for plotting.

    max_genes
        The maximum number of genes to display per archetype.

    Returns
    -------
    A :class:`tuple` containing:
        - :class:`matplotlib.figure.Figure`
        - :class:`list` of :class:`matplotlib.axes.Axes`

    Notes
    -----
    Displays a set of bar plots where each subplot corresponds to a 'gene_from_archetype'. 
    The bars represent gene expression levels across archetypes, color-coded by archetype.

    - Each bar in the plot represents the expression level of a gene in a specific archetype.
    - The bar colors are dynamically assigned based on the archetype to which they belong.
    - Gene ordering within each subplot respects the 'plot_order' column from the input DataFrame.
    - Subplots include style and font adjustments for better visualization.

    Examples
    --------
    .. code-block:: python

        import pyparti as parti

        archetype_expression = parti.archetype_expression(adata)
        fig, axes = parti.plot_archetype_expression(archetype_expression)

    """
    if adt_key:
        print(f"{adt_key}")

    # Get unique 'gene_from' values
    gene_from_list = archetype_expression['gene_from_archetype'].unique()
    num_subplots = len(gene_from_list)

    # Create mapping from original archetype labels to new labels starting from 1
    unique_archetypes = sorted(archetype_expression['gene_from_archetype'].unique())
    archetype_mapping = {archetype: idx + 1 for idx, archetype in enumerate(unique_archetypes)}
    num_archetypes = len(unique_archetypes)

    # Generate dynamic colors based on the unique archetypes
    color_map = colormaps['tab20']
    archetype_colors = {archetype: color_map((archetype_mapping[archetype]-1) / num_archetypes) for archetype in unique_archetypes}

    # Create subplots
    fig, axes = plt.subplots(
        nrows=1,
        ncols=num_subplots,
        figsize=(6 * num_subplots, 6),
        squeeze=False,
    )

    for idx, gene_from in enumerate(gene_from_list):
        ax = axes[0, idx]

        # Select top N genes from this 'gene_from' based on 'plot_order'
        df_genes = archetype_expression[archetype_expression['gene_from_archetype'] == gene_from]
        df_genes = df_genes.sort_values('plot_order').head(max_genes)
        genes_from = df_genes['gene'].unique()

        # Filter data for these genes across all 'expression_in_archetype'
        df_sub = archetype_expression[archetype_expression['gene'].isin(genes_from)]

        # Pivot data: index='expression_in_archetype', columns='gene', values='expression_mean'
        df_pivot = df_sub.pivot_table(
            index='expression_in_archetype',
            columns='gene',
            values='expression_mean',
            aggfunc='mean'
        )

        # Ensure genes are ordered according to 'plot_order'
        gene_order = df_genes[['gene', 'plot_order']].drop_duplicates().set_index('gene').sort_values('plot_order').index
        df_pivot = df_pivot[gene_order]

        # Replace NaN with zeros if appropriate
        df_pivot = df_pivot.fillna(0)

        # Plotting
        x = np.arange(len(df_pivot.index))  # Number of archetypes
        total_width = 0.8
        num_genes = len(gene_order)
        width = total_width / num_genes

        bar_labels = []  # List to hold labels for each bar
        bar_positions = []  # List to hold positions for each bar

        for i, gene in enumerate(gene_order):
            expr_means = df_pivot[gene].values
            positions = x - total_width / 2 + i * width + width / 2  # Calculate positions
            # Assign colors dynamically based on archetype index
            colors = [archetype_colors[archetype] for archetype in df_pivot.index]
            ax.bar(    # Use dynamically assigned colors
                positions,
                expr_means,
                width=width,
                color=colors,
                edgecolor='black',
                linewidth=2,
            )
            bar_positions.extend(positions)  # Append all bar positions
            bar_labels.extend([gene] * len(positions))  # Append gene labels for each position

        # Set individual ticks and labels for each bar
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(
            bar_labels,
            rotation=90,
            ha='center',
            va='top',
            fontsize=14,
            fontweight='bold',
            family='Arial',
            color='black',
        )

        ax.set_xlabel('')

        # Set y-axis label only for the first subplot
        if idx == 0:
            ax.set_ylabel(
                'Raw Counts',
                fontsize=16,
                fontweight='bold',
                family='Arial',
                color='black',
            )
            ax.set_title(
                f'Expression of Genes from Archetype {archetype_mapping[gene_from]}',
                fontsize=16,
                fontweight='bold',
                family='Arial',
                color='black',
            )
        else:
            ax.set_title(
                f'Archetype {archetype_mapping[gene_from]}',
                fontsize=16,
                fontweight='bold',
                family='Arial',
                color='black',
            )

        # Style adjustments for grid, panel, and ticks
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1)
        ax.spines['bottom'].set_linewidth(1)
        ax.spines['left'].set_color('black')
        ax.spines['bottom'].set_color('black')
        ax.tick_params(axis='x', which='both', length=5, color='black', width=1)
        ax.tick_params(axis='y', which='both', length=5, color='black', width=1)
        ax.yaxis.set_tick_params(labelsize=14, labelcolor='black', direction='out', pad=0)
        ax.xaxis.set_tick_params(direction='out', pad=5)

        # Make ytick labels bold and set font family
        for label in ax.get_yticklabels():
            label.set_fontweight('bold')
            label.set_family('Arial')

        # Remove background grid
        ax.grid(False)

    # Overall layout and adjustments
    plt.tight_layout()
    plt.show()

    return fig, axes
