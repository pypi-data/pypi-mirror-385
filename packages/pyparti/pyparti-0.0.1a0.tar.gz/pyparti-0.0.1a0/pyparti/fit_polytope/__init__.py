"""
This module contains the polytopal fitting algorithms.
"""

from .algs import (  # type: ignore
    sdvmm,
    sisal,
    pcha,
    # maxvoldual,
)

from .calculate_hull_volume import calculate_convex_hull_volume

from .find_min_polytope import (
    find_min_polytope_adata,
    find_min_polytope_main,
)

from .significance import calculate_p_value

from .fit_polytope import (
    fit_polytope,
    fit_polytope_adata_dict,
)

from .filter_fits import get_significant_fits_adata_dict

__all__ = [
    # algs
    "sdvmm",
    "sisal",
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
]
