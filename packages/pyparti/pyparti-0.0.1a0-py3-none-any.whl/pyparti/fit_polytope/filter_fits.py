"""
This module contains the functions for filtering ``adata_dict`` 
based on results from :func:`fit_polytope_adata_dict`.
"""

from anndata import AnnData
from anndict import AdataDict


def get_significant_fits_adata_dict(
    adata_dict: AdataDict,
    alpha: float = 0.05,
    inplace: bool = False,
) -> AdataDict:
    """
    Filters :class:`AdataDict` to only include :class:`AnnData` objects with a p-value
    less than ``alpha``.

    Parameters
    ----------
    adata_dict
        :class:`AdataDict` object.

    alpha
        Significance level.

    inplace
        Whether to modify the :class:`AdataDict` in place. If ``False``, a new
        :class:`AdataDict` is returned.

    Returns
    -------
    adata_dict
        :class:`AdataDict` object with only :class:`AnnData` objects with a p-value
        less than ``alpha``.
    """
    def check_p_value(adata: AnnData) -> bool:
        return adata.uns['polytope']['p_value'] < alpha

    mask = adata_dict.fapply(check_p_value)

    return adata_dict.index_bool(mask, inplace=inplace)
