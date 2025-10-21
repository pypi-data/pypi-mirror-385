"""
Functions for plotting results of parti.
"""

from .p_value import (
    plot_p_value_histogram,
)

from .contents import (
    plot_archetype_contents
)

from .expression import (
    plot_archetype_expression
)

from .gene_frequencies import (
    plot_gene_frequencies,
    display_gene_frequencies,
)

__all__ = [
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