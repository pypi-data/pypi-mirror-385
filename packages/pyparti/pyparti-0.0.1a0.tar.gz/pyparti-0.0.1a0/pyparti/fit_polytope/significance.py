"""
This module contains the function to calculate significance of a polytopal fit.
"""

from typing import Any, Callable
from math import factorial

import numpy as np
import scipy

from scipy.spatial import ConvexHull # pylint: disable=no-name-in-module
from sklearn.decomposition import PCA
from anndata import AnnData

from .calculate_hull_volume import calculate_convex_hull_volume


def calculate_polytope_t_ratios_adata(
    adata: AnnData,
    polytope_func: Callable,
    data_layer: str = "X_pca_reduced",
    n_vertices: int = 3,
    max_runs: int = 100,
    num_iter: int = 50,
    **polytope_kwargs: Any,
) -> np.ndarray:
    """
    Wrapper for :pyfunc:`calculate_polytope_t_ratios` that works directly on an
    :class:`AnnData` object.

    Parameters
    ----------
    adata
        Annotated single-cell or spatial object with PCA‐reduced coordinates
        stored in :pyattr:`~AnnData.obsm`.

    polytope_func
        Polytope-finding routine (e.g. ``sisal`` or ``SDVMM``).

    data_layer
        Key in :pyattr:`~AnnData.obsm` containing the coordinates to use.

    n_vertices
        Number of archetypes (polytope vertices).

    max_runs
        Number of random shuffles (bootstrap iterations).

    num_iter
        Number of polytope fits per shuffle.

    **polytope_kwargs
        Extra keyword arguments forwarded to *polytope_func*.

    Returns
    -------
    numpy.ndarray
        Minimum (``sisal``) or maximum (``SDVMM``) T-ratios across all shuffles.
    """
    if data_layer not in adata.obsm:
        raise ValueError(
            f"The specified data_layer '{data_layer}' does not exist in adata.obsm."
        )

    return calculate_polytope_t_ratios(
        adata.obsm[data_layer],
        polytope_func,
        n_vertices,
        max_runs=max_runs,
        num_iter=num_iter,
        **polytope_kwargs,
    )


def calculate_polytope_t_ratios(
    data_points: np.ndarray,
    polytope_func: Callable,
    n_vertices: int,
    max_runs: int = 10_000,
    num_iter: int = 50,
    **polytope_kwargs: Any,
) -> np.ndarray:
    """
    Compute T-ratios for a polytope fit to *data_points* using randomised
    bootstrapping.

    Parameters
    ----------
    data_points
        Observations (samples × dimensions) after dimensionality reduction.

    polytope_func
        Polytope-finding routine (``sisal`` or ``SDVMM`` expected).

    n_vertices
        Number of archetypes (polytope vertices).

    max_runs
        Number of random shuffles (bootstrap iterations).

    num_iter
        Number of polytope fits per shuffle.

    **polytope_kwargs
        Extra keyword arguments forwarded to *polytope_func*.

    Returns
    -------
    numpy.ndarray
        Minimum (``sisal``) or maximum (``SDVMM``) T-ratios across all shuffles.
    """
    dim = n_vertices - 1
    min_rand_arch_vol = np.zeros(max_runs)
    min_rand_arch_ratio = np.zeros(max_runs)
    vol_conv_rand = np.zeros(max_runs)

    for m in range(max_runs):
        polytope_rand1 = np.zeros_like(data_points)

        # Shuffle each dimension independently
        for i in range(data_points.shape[1]):
            shuffle_idx = np.random.permutation(data_points.shape[0])
            polytope_rand1[:, i] = data_points[shuffle_idx, i]

        # Convex-hull volume
        try:
            hull = ConvexHull(polytope_rand1[:, :dim])
            vol_conv_rand[m] = hull.volume
        except scipy.spatial.qhull.QhullError:
            vol_conv_rand[m] = np.nan

        vol_arch_rand = np.zeros(num_iter)
        rand_data_ratios = np.zeros(num_iter)

        for k in range(num_iter):
            if polytope_func.__name__ == "sisal":
                y = polytope_rand1[:, :n_vertices].T
                try:
                    archs, *_ = polytope_func(y, n_vertices, VERBOSE=0, **polytope_kwargs)
                    if not np.isnan(archs).any():
                        arch_red = archs - archs[:, [n_vertices - 1]]
                        arch_sub = arch_red[:-1, :-1]
                        vol = abs(np.linalg.det(arch_sub) / factorial(dim))
                        vol_arch_rand[k] = vol
                        rand_data_ratios[k] = vol_arch_rand[k] / vol_conv_rand[m]
                    else:
                        vol_arch_rand[k] = np.nan
                        rand_data_ratios[k] = np.nan
                except Exception:  # pylint: disable=broad-exception-caught
                    vol_arch_rand[k] = np.nan
                    rand_data_ratios[k] = np.nan
            elif polytope_func.__name__ == "SDVMM":
                y = polytope_rand1[:, :dim].T
                r = 0
                try:
                    archs, _ = polytope_func(y, n_vertices, r, **polytope_kwargs)
                    if not np.isnan(archs).any():
                        arch_red = archs - archs[:, [n_vertices - 1]]
                        arch_sub = arch_red[:, :-1]
                        vol = abs(np.linalg.det(arch_sub) / factorial(dim))
                        vol_arch_rand[k] = vol
                        rand_data_ratios[k] = vol_arch_rand[k] / vol_conv_rand[m]
                    else:
                        vol_arch_rand[k] = np.nan
                        rand_data_ratios[k] = np.nan
                except Exception:  # pylint: disable=broad-exception-caught
                    vol_arch_rand[k] = np.nan
                    rand_data_ratios[k] = np.nan
            else:
                raise ValueError(
                    f"polytope finding function {polytope_func.__name__} not supported. "
                    "Use ``SDVMM`` or ``sisal``."
                )

        if polytope_func.__name__ == "sisal":
            min_rand_arch_vol[m] = np.nanmin(vol_arch_rand)
            min_rand_arch_ratio[m] = np.nanmin(rand_data_ratios)
        elif polytope_func.__name__ == "SDVMM":
            min_rand_arch_vol[m] = np.nanmax(vol_arch_rand)
            min_rand_arch_ratio[m] = np.nanmax(rand_data_ratios)

    return min_rand_arch_ratio


def calculate_lineness_ratios(
    data_points: np.ndarray,
    max_runs: int = 10_000,
) -> np.ndarray:
    """
    Compute line-ness ratios (PC1 / PC2 variance) for shuffled data.

    Parameters
    ----------
    data_points
        Original data matrix.

    max_runs
        Number of random shuffles (bootstrap iterations).

    Returns
    -------
    numpy.ndarray
        Line-ness ratios for each shuffle.
    """
    lineness_ratios = np.zeros(max_runs)

    for i in range(max_runs):
        polytope_rand = np.zeros_like(data_points)

        for j in range(data_points.shape[1]):
            shuffle_idx = np.random.permutation(data_points.shape[0])
            polytope_rand[:, j] = data_points[shuffle_idx, j]

        pca = PCA()
        pca.fit(polytope_rand)
        variances_rand = pca.explained_variance_
        lineness_ratios[i] = variances_rand[0] / variances_rand[1]

    return lineness_ratios


def calculate_lineness_ratios_adata(
    adata: AnnData,
    max_runs: int = 100,
) -> np.ndarray:
    """
    Convenience wrapper for :pyfunc:`calculate_lineness_ratios` operating on
    :class:`AnnData`.

    Parameters
    ----------
    adata
        Annotated data object containing reduced PCA coordinates.

    max_runs
        Number of random shuffles (bootstrap iterations).

    Returns
    -------
    numpy.ndarray
        Line-ness ratios for each shuffle.
    """
    reduced_score = adata.obsm["X_pca_reduced"]
    reduced_coeff = adata.varm["PCs_reduced"]
    mu = adata.uns["pca_reduced"]["mean"]

    data_points = np.dot(reduced_score, reduced_coeff.T) + mu

    return calculate_lineness_ratios(data_points, max_runs=max_runs)


def calculate_p_value(
    adata: AnnData,
    data_layer: str,
    polytope_func: Callable,
    polytope_coords: np.ndarray,
    polytope_volume: float,
) -> float:
    """
    Compute a p-value for the polytope (or line) fit stored in *polytope_coords*.

    The test statistic is the T-ratio (``n_vertices > 2``) or line-ness ratio
    (``n_vertices == 2``) of the real data compared with shuffled data.

    Parameters
    ----------
    adata
        An :class:`AnnData` object.

    data_layer
        Key in :pyattr:`~AnnData.obsm` containing the coordinates used.

    polytope_func
        Polytope-fitting function used to obtain ``polytope_coords``.

    polytope_coords
        Coordinates of the fitted polytope (archetypes).

    polytope_volume
        Volume of the fitted polytope.

    Returns
    -------
    float
        Empirical p-value.
    """
    n_vertices = polytope_coords.shape[0]

    if n_vertices > 2:
        real_data_volume = calculate_convex_hull_volume(
            adata, data_layer=data_layer, n_vertices=n_vertices
        )
        real_data_t_ratio = polytope_volume / real_data_volume

        shuffled_t_ratios = calculate_polytope_t_ratios_adata(
            adata,
            polytope_func,
            data_layer=data_layer,
            n_vertices=n_vertices,
        )

        if polytope_func.__name__ == "SDVMM":
            p_value = np.sum(shuffled_t_ratios > real_data_t_ratio) / len(
                shuffled_t_ratios
            )
        elif polytope_func.__name__ == "sisal":
            p_value = np.sum(shuffled_t_ratios < real_data_t_ratio) / len(
                shuffled_t_ratios
            )
        else:
            raise ValueError(
                f"polytope finding function {polytope_func.__name__} not supported. "
                "Use SDVMM or sisal."
            )

    elif n_vertices == 2:
        if adata.uns["pca_reduced"]:
            explained = adata.uns["pca_reduced"]["explained_variance"]
            real_data_ratio = explained[0] / explained[1]
        else:
            raise ValueError(
                "PCA results not found in `adata.uns['pca_reduced']`. "
                "Run PCA before calling this function."
            )

        shuffled_ratios = calculate_lineness_ratios_adata(adata)
        p_value = np.sum(shuffled_ratios > real_data_ratio) / len(shuffled_ratios)

    else:
        raise ValueError("n_vertices must be ≥ 2.")

    return p_value















#this is a version of the function that isn't faster than the one above.
# def calculate_polytope_t_ratios(DataPoints, polytope_func, n_vertices, maxRuns=10000, numIter=50, **polytope_kwargs):
#     """
#     Optimized version of calculate_polytope_t_ratios using parallelization and vectorization.
#     """
#     dim = n_vertices - 1  # dimension

#     # Function to process each run
#     def process_run(m):
#         PolytopeRand1 = np.apply_along_axis(np.random.permutation, 0, DataPoints)

#         # Compute the Convex Hull volume
#         try:
#             hull = ConvexHull(PolytopeRand1[:, :dim])
#             VolConvRand_m = hull.volume
#         except Exception:
#             VolConvRand_m = np.nan

#         VolArchRand = np.zeros(numIter)
#         RandDataRatios = np.zeros(numIter)

#         def process_iter(k):
#             if polytope_func.__name__ == 'sisal':
#                 Y = PolytopeRand1[:, :n_vertices].T
#                 try:
#                     Archs, _, _, _ = polytope_func(Y, n_vertices, VERBOSE=0, **polytope_kwargs)
#                     if not np.isnan(Archs).any():
#                         ArchRandRed = Archs - Archs[:, [n_vertices - 1]]
#                         ArchRandRed_sub = ArchRandRed[:-1, :-1]
#                         vol = abs(np.linalg.det(ArchRandRed_sub) / factorial(n_vertices - 1))
#                         ratio = vol / VolConvRand_m
#                     else:
#                         vol = np.nan
#                         ratio = np.nan
#                 except Exception:
#                     vol = np.nan
#                     ratio = np.nan
#             else:
#                 Y = PolytopeRand1[:, :dim].T
#                 r = 0
#                 try:
#                     Archs, _ = polytope_func(Y, n_vertices, r, **polytope_kwargs)
#                     if not np.isnan(Archs).any():
#                         ArchRandRed = Archs - Archs[:, [n_vertices - 1]]
#                         ArchRandRed_sub = ArchRandRed[:, :-1]
#                         vol = abs(np.linalg.det(ArchRandRed_sub) / factorial(n_vertices - 1))
#                         ratio = vol / VolConvRand_m
#                     else:
#                         vol = np.nan
#                         ratio = np.nan
#                 except Exception:
#                     vol = np.nan
#                     ratio = np.nan
#             return vol, ratio

#         results_iter = [process_iter(k) for k in range(numIter)]
#         VolArchRand[:], RandDataRatios[:] = zip(*results_iter)

#         if polytope_func.__name__ == 'sisal':
#             minRandArchVol_m = np.nanmin(VolArchRand)
#             minRandArchRatio_m = np.nanmin(RandDataRatios)
#         else:
#             minRandArchVol_m = np.nanmax(VolArchRand)
#             minRandArchRatio_m = np.nanmax(RandDataRatios)

#         return minRandArchVol_m, minRandArchRatio_m
    
#     from joblib import Parallel, delayed, cpu_count

#     # Print how many cores it's about to use
#     num_cores = cpu_count()
#     print(f"Using {num_cores} cores")

#     # Parallel execution of the outer loop
#     results = Parallel(n_jobs=-1)(
#         delayed(process_run)(m) for m in range(maxRuns)
#     )

#     # Extract the results
#     minRandArchVol, minRandArchRatio = zip(*results)
#     minRandArchVol = np.array(minRandArchVol)
#     minRandArchRatio = np.array(minRandArchRatio)

#     return minRandArchRatio
