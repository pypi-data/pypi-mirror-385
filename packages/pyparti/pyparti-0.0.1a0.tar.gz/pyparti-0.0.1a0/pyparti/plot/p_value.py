"""
Functions for plotting p-values.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_p_value_histogram(adata_dict, alpha = 0.05):
    """
    Plots a histogram of p-values extracted from ``adata.uns['simplex']['p_value']``
    for each :class:`AnnData` object in the provided dictionary, matching the style of ggplot2.

    Parameters
    ----------
    adata_dict
        An :class:`AdataDict`.

    Returns
    -------
    ``None``

    Notes
    -----
    This function plots a histogram of p-values extracted from ``adata.uns['simplex']['p_value']``
    across all :class:`AnnData` objects in ``adata_dict``.
    """
    p_values = []

    for adata in adata_dict.values():
        p_value = adata.uns['simplex']['p_value']
        p_values.append(p_value)

    # Define bins with binwidth 0.05 and centered at 0.025
    bins = np.arange(0, 1.05, 0.05)

    # Plotting the histogram
    plt.figure(figsize=(4, 4))
    counts, _, _ = plt.hist(
        p_values,
        bins=bins,
        edgecolor='black',
        color='#595A5A',
        align='mid'  # Centers bins at 0.025, 0.075, ..., 0.975
    )

    # Add vertical line at x=0.05
    plt.axvline(x=alpha, color='red')

    # Set x-axis limits
    plt.xlim(0, 1)

    # Adjust y-axis limits to add 10 units to the upper limit
    max_count = counts.max()
    plt.ylim(0, max_count + 10)

    # Set labels with specified styles
    plt.xlabel('P-value', fontweight='bold', fontsize=16, fontfamily='Arial')
    plt.ylabel('Count', fontweight='bold', fontsize=16, fontfamily='Arial')

    # Customize tick parameters
    plt.xticks(
        fontsize=14,
        fontweight='bold',
        fontfamily='Arial',
        color='black'
    )
    plt.yticks(
        fontsize=14,
        fontweight='bold',
        fontfamily='Arial',
        color='black'
    )

    # Apply theme_classic style by removing top and right spines
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')

    # Set axis ticks color
    ax.tick_params(axis='both', colors='black', which='both', length=5)

    # Adjust the plot layout
    plt.tight_layout()

    # Display the plot
    plt.show()
