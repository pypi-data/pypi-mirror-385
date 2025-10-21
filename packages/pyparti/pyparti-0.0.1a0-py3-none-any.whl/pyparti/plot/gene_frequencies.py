"""
Functions for displaying and plotting gene frequencies.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib import gridspec


def display_gene_frequencies(
    archetype_stats_df: pd.DataFrame,
    min_frequency: int = 2,
    max_genes: int | None = None,
    adt_key: tuple[str,...] | None = None,
) -> str:
    """
    Display gene frequencies for each archetype, labeled by archetype annotation.
    
    Parameters
    ----------
    archetype_stats_df
        :class:`DataFrame` output from :func:`archetype_statistics`, containing:
        - ``'gene_frequency'`` column with dictionaries of gene frequencies
        - ``'archetype annotation'`` column with archetype labels

    min_frequency
        Minimum frequency threshold for genes to display

    max_genes
        Maximum number of genes to display per archetype. If ``None``, shows all genes.

    Returns
    -------
    A :class:`str` containing gene frequencies for each archetype.

    Examples
    --------
    .. code-block:: python

        import pyparti as parti

        archetype_stats_df = parti.archetype_statistics(adata)
        print(parti.display_gene_frequencies(archetype_stats_df))
    """
    if adt_key:
        print(f"{adt_key}")

    output_lines = []

    # Create mapping from original archetype labels to new labels starting from 1
    archetypes_list = sorted(archetype_stats_df['archetype'].unique())
    archetype_mapping = {archetype: idx + 1 for idx, archetype in enumerate(archetypes_list)}

    for _, row in archetype_stats_df.iterrows():
        # Get archetype, annotation, and gene frequency dictionary
        archetype = row['archetype']
        annotation = row.get(    # Fallback if column missing
            'archetype_annotation',
            f'Archetype {archetype}',
        )  
        gene_freq = row['gene_frequency']

        # Sort genes by frequency in descending order
        sorted_genes = sorted(
            gene_freq.items(),
            key=lambda x: (x[1], x[0]),  # Sort by frequency first, then gene name
            reverse=True
        )

        # Filter by minimum frequency
        filtered_genes = [
            (gene, freq) for gene, freq in sorted_genes
            if freq >= min_frequency
        ]

        # Apply max_genes limit if specified
        if max_genes is not None:
            filtered_genes = filtered_genes[:max_genes]

        # Skip if no genes to display
        if not filtered_genes:
            continue

        # Format the archetype header with new labels
        new_archetype_label = archetype_mapping[archetype]
        header = f"Archetype {new_archetype_label}: {annotation}"
        output_lines.append(f"\n{header}")
        output_lines.append("-" * max(40, len(header)))

        # Format gene frequencies
        for gene, freq in filtered_genes:
            output_lines.append(f"{gene:<20} {freq:>5}")

    # Join all lines with newlines
    return "\n".join(output_lines)


def plot_gene_frequencies(
    archetype_stats_df: pd.DataFrame,
    min_frequency: int = 2,
    max_genes: int | None = None,
    adt_key: tuple[str,...] | None = None,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """
    Plot gene frequencies for each archetype, labeled by archetype annotation.
    
    Parameters
    ----------
    archetype_stats_df
        :class:`DataFrame` output from :func:`archetype_statistics`, containing:
        - ``'gene_frequency'`` column with dictionaries of gene frequencies
        - ``'archetype annotation'`` column with archetype labels

    min_frequency
        Minimum frequency threshold for genes to display

    max_genes
        Maximum number of genes to display per archetype. If ``None``, shows all genes.

    adt_key
        Used when this function is called from :func:`adata_dict_fapply`.
        If provided, ``adt_key`` is printed.

    Returns
    -------
    A :class:`tuple` containing:
        - :class:`matplotlib.figure.Figure`
        - :class:`list` of :class:`matplotlib.axes.Axes`

    Examples
    --------
    .. code-block:: python

        import pyparti as parti

        archetype_stats_df = parti.archetype_statistics(adata)
        fig, axes = parti.plot_gene_frequencies(archetype_stats_df)

    """

    if adt_key:
        print(f"{adt_key}")

    # Prepare the data for plotting
    data_list = []

    for _, row in archetype_stats_df.iterrows():
        archetype = row['archetype']
        annotation = row.get('archetype_annotation', f'Archetype {archetype}')
        gene_freq = row['gene_frequency']

        # Filter and sort genes
        gene_freq_items = [
            (gene, freq) for gene, freq in gene_freq.items() if freq >= min_frequency
        ]
        gene_freq_items.sort(key=lambda x: (x[1], x[0]), reverse=True)

        if max_genes is not None:
            gene_freq_items = gene_freq_items[:max_genes]

        if not gene_freq_items:
            # Add a placeholder if no genes meet the threshold
            data_list.append({
                'archetype': archetype,
                'annotation': annotation,
                'gene': 'No genes',
                'frequency': 0,
                'rank': 1
            })
        else:
            for rank, (gene, freq) in enumerate(gene_freq_items, start=1):
                data_list.append({
                    'archetype': archetype,
                    'annotation': annotation,
                    'gene': gene.replace('_', ' '),
                    'frequency': freq,
                    'rank': rank
                })

    plot_df = pd.DataFrame(data_list)

    # Get unique archetypes and annotations
    archetypes = plot_df['archetype'].unique()
    num_archetypes = len(archetypes)

    # Create mapping from original archetype labels to new labels starting from 1
    archetype_mapping = {archetype: idx + 1 for idx, archetype in enumerate(sorted(archetypes))}

    # Create a GridSpec to allocate space for the colorbar
    fig = plt.figure(figsize=(8, num_archetypes * 2))
    # Create a GridSpec with an extra column for the colorbar
    gs = gridspec.GridSpec(
        num_archetypes,
        2,
        width_ratios=[20, 1],
        height_ratios=[1]*num_archetypes,
        wspace=0.05,
        hspace=0.5,
    )
    axes = []
    for i in range(num_archetypes):
        ax = fig.add_subplot(gs[i, 0])  # Plot in the first column
        axes.append(ax)

    # Create color palette and normalization shared across all subplots
    vmin = plot_df['frequency'].min()
    vmax = plot_df['frequency'].max()
    cmap = sns.color_palette("Blues", as_cmap=True)

    # Create a ScalarMappable for the colorbar
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Only needed for matplotlib < 3.1

    for ax, archetype in zip(axes, archetypes):
        # Filter data for the current archetype
        data = plot_df[plot_df['archetype'] == archetype].copy()
        data = data.sort_values('rank')

        # Get the corresponding annotation
        annotation = data['annotation'].iloc[0]

        # Build a DataFrame with a single row for the archetype
        data_pivot = pd.DataFrame(
            [data['frequency'].values],
            columns=data['gene'],
            index=[archetype],
        )

        # Create an array of gene names for annotations
        annot_array = np.array([data['gene'].values])

        # Plot heatmap for frequency with gene names as annotations
        sns.heatmap(
            data_pivot, ax=ax, cmap=cmap,
            cbar=False,  # Do not create individual colorbars
            annot=annot_array, annot_kws={"weight": "bold"},
            fmt='',  # Ensures that the annotations are displayed as strings
            linewidths=0.5, linecolor="black", center=1,
            vmin=vmin, vmax=vmax,  # Explicitly set color scaling
            yticklabels=True
        )

        # Adjust axis labels
        ax.set_xticks([])
        ax.set_ylabel('')  # Remove the default y-axis label
        ax.set_xlabel('')  # Remove the default x-axis label

        # Set y-axis tick labels to the new archetype labels
        ax.set_yticklabels([archetype_mapping[archetype]], rotation=0, fontsize=12, weight='bold')

        # Set the title as the archetype_annotation (adjusted if needed)
        ax.set_title(annotation, fontsize=14, weight="bold")

    # Add a single colorbar to the right of all subplots
    # Create an axis for the colorbar in the extra column
    cax = fig.add_subplot(gs[:, 1])  # Use all rows in the last column

    # Add the colorbar
    cbar = plt.colorbar(sm, cax=cax)
    cbar.set_label("Frequency", weight="bold")
    # Set color bar tick labels to bold
    for label in cbar.ax.get_yticklabels():
        label.set_weight("bold")

    plt.show()
    return fig, axes
