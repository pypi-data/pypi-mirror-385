"""
Functions for plotting metadata of vertices in archetypes.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_archetype_contents(
    archetypes: pd.DataFrame,
    bar_col: str,
    count_col: str,
    qualified_only: bool = True,
    adt_key: tuple[str,...] | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Creates a grouped bar plot showing the count
    per archetype community and the values in that column.

    Parameters
    ----------
    archetypes
        :class:`DataFrame` containing the archetypes data.

    bar_col
        bar splitting variable

    count_col
        count variable

    qualified_only
        If ``True``, only include rows where ``'qualifies'`` is ``True``.

    Returns
    -------
    A :class:`tuple` containing:
        - :class:`matplotlib.figure.Figure`
        - :class:`matplotlib.axes.Axes`

    Examples
    --------
    .. code-block:: python

        import pyparti as parti

        archetypes = parti.archetype_alignment(adata_fit)
        fig, ax = parti.plot_archetype_contents(archetypes)

    """
    if adt_key:
        print(f"{adt_key}")

    # Compute the total number per group in bar_col (overall value)
    total_counts = archetypes.copy().groupby(bar_col, observed=False)[count_col].nunique().reset_index(name='overall_value')

    if qualified_only:
        df = archetypes[archetypes['qualifies']].copy()
    else:
        df = archetypes.copy()

    # Compute the counts per archetype and group in bar_col
    grouped_counts = df.groupby(['archetype', bar_col], observed=False)[count_col].nunique().reset_index(name='value')
    grouped_counts['overall.or.not'] = 'not_overall'

    # Create the overall data by duplicating the overall_value across all archetypes per patient
    unique_archetypes = grouped_counts['archetype'].unique()
    overall_data_list = []

    for group in total_counts[bar_col]:
        overall_value = total_counts.loc[total_counts[bar_col] == group, 'overall_value'].values[0]
        for archetype in unique_archetypes:
            overall_data_list.append({
                'archetype': archetype,
                bar_col: group,
                'value': overall_value,
                'overall.or.not': 'overall'
            })

    overall_data = pd.DataFrame(overall_data_list)

    # Combine the per-archetype counts with the overall data
    plot_df = pd.concat([grouped_counts, overall_data], ignore_index=True)

    # Create mapping from original archetype labels to new labels starting from 1
    archetypes_list = sorted(plot_df['archetype'].unique())
    archetype_mapping = {archetype: idx + 1 for idx, archetype in enumerate(archetypes_list)}
    archetype_to_pos = {archetype: idx for idx, archetype in enumerate(archetypes_list)}
    num_archetypes = len(archetypes_list)

    # Get list of unique values in bar_col
    col_values = sorted(plot_df[bar_col].unique())
    num_col_values = len(col_values)

    total_width = 0.8
    bar_width = total_width / num_col_values

    # Define colors for the unique values in col
    colors = sns.color_palette("husl", num_col_values)
    color_dict = dict(zip(col_values, colors))

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, col_value in enumerate(col_values):
        color = color_dict[col_value]
        x_offset = -total_width / 2 + bar_width / 2 + i * bar_width

        # Data for this col_value
        data_group = plot_df[plot_df[bar_col] == col_value]

        # Plot overall data first
        data_overall = data_group[data_group['overall.or.not'] == 'overall']
        x_positions_overall = [archetype_to_pos[a] + x_offset for a in data_overall['archetype']]
        ax.bar(
            x_positions_overall,
            data_overall['value'],
            width=bar_width,
            edgecolor='black',
            linewidth=0,
            color=color,
            alpha=0.2
        )

        # Plot per-archetype counts on top
        data_not_overall = data_group[data_group['overall.or.not'] == 'not_overall']
        x_positions_not_overall = [archetype_to_pos[a] + x_offset for a in data_not_overall['archetype']]
        ax.bar(
            x_positions_not_overall,
            data_not_overall['value'],
            width=bar_width,
            label=col_value,
            edgecolor='black',
            linewidth=0.5,
            color=color
        )

    # Set x-axis labels using the new archetype labels
    ax.set_xticks(range(num_archetypes))
    ax.set_xticklabels(
        [archetype_mapping[archetype] for archetype in archetypes_list],
        rotation=0,
        ha='center',
        fontsize=14,
        fontweight='bold',
    )
    ax.set_xlabel(None)
    ax.set_ylabel(f'Count ({count_col})', fontweight='bold', fontsize=16)

    # Modify y-axis ticks to only show integers
    ax.yaxis.get_major_locator().set_params(integer=True)

    # Adjust legend
    ax.legend(title=None, loc=6, bbox_to_anchor=(1,0.5), fontsize=14)

    # Customize plot aesthetics to match ggplot style
    ax.tick_params(axis='both', which='both', length=5, color='black', width=1)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    plt.yticks(fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.show()

    return fig, ax
