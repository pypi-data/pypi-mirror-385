"""
This module contains the function to find the minimal or maximal volume polytope.
"""

from typing import Any, Callable, Optional, Tuple
from math import factorial

import numpy as np

from anndata import AnnData


def find_min_polytope_adata(
    adata: AnnData,
    polytope_func: Callable,
    data_layer: str = 'X_pca_reduced',
    n_vertices: int = 3,
    num_iter: int = 1000,
    r: Optional[float] = None,
    **polytope_func_kwargs: Any
) -> Tuple[np.ndarray, float]:
    """
    Finds the minimal or maximal volume polytope using a specified polytope identification function.

    Parameters
    ----------
    adata
        An AnnData object.

    polytope_func
        The polytope identification function to use (e.g., sisal, SDVMM).

    data_layer
        The data layer to use. Default is 'X_pca_reduced' in adata.obsm.

    num_iter
        Number of iterations. Default is 1000.

    n_vertices
        Number of archetypes. Default is 3.

    r
        Back-off tolerance parameter for SDVMM. Default is None.

    **polytope_func_kwargs
        Additional keyword arguments to pass to the polytope function.

    Returns
    -------
    archs_min
        The archetypes that form the polytope with minimal or maximal volume.

    vol_arch_real
        The volume of the best fitting polytope.

    """
    # Extract data from the specified layer
    if data_layer in adata.obsm:
        data_pca = adata.obsm[data_layer]
    # elif data_layer == 'X':
    #     DataPCA = adata.X
    else:
        raise ValueError(f"data_layer '{data_layer}' not found in adata.obsm or as 'X'")

    # Ensure DataPCA is a numpy array
    data_pca = np.array(data_pca)

    return find_min_polytope_main(data_pca, polytope_func, n_vertices, num_iter, r, **polytope_func_kwargs)


def find_min_polytope_main(
    data: np.ndarray,
    polytope_func: Callable,
    n_vertices: int = 3,
    num_iter: int = 1000,
    r: Optional[float] = None,
    **polytope_func_kwargs: Any
) -> Tuple[np.ndarray, float]:
    """
    Finds the minimal or maximal volume polytope using a specified polytope identification function.

    Parameters
    ----------
    data
        The data to use.

    polytope_func
        The polytope identification function to use (e.g., sisal, SDVMM).

    n_vertices
        Number of archetypes. Default is 3.

    num_iter
        Number of iterations. Default is 1000.

    r
        Back-off tolerance parameter for SDVMM. Default is None.

    **polytope_func_kwargs
        Additional keyword arguments to pass to the polytope function.

    Returns
    -------
    archs_min
        The archetypes that form the polytope with minimal or maximal volume.

    vol_arch_real
        The volume of the best fitting polytope.
    """

    # Initialize lists to store volumes and archetypes
    vol_arch = []
    min_archs_iter = []

    # Perform iterations to find the minimal or maximal volume polytope
    for i in range(num_iter):
        try:
            if polytope_func.__name__ == 'sisal':
                # Data preparation for sisal
                # Select all samples and the first n_vertices features (columns), then transpose
                y = data[:, :n_vertices].T  # Shape: (n_vertices x n_samples)

                # Run sisal
                archs, _, _, _ = polytope_func(y, n_vertices, VERBOSE=0, **polytope_func_kwargs)

                if not np.isnan(archs).any():
                    # Calculate the volume of the polytope
                    # Subtract the last column from all columns
                    arch1_red = archs - archs[:, [n_vertices - 1]]

                    # Take submatrix excluding the last row and last column
                    arch1_red_sub = arch1_red[:-1, :-1]

                    # Compute the determinant
                    vol = abs(np.linalg.det(arch1_red_sub) / factorial(n_vertices - 1))

                    vol_arch.append(vol)
                    # Save the archetypes
                    min_archs_iter.append(archs[:-1, :n_vertices])
                else:
                    vol_arch.append(np.nan)
                    min_archs_iter.append(np.nan)
            else:
                # Data preparation for SDVMM
                # Select all samples and the first n_vertices - 1 features (columns), then transpose
                y = data[:, :n_vertices - 1].T  # Shape: (n_vertices - 1 x n_samples)

                # Run SDVMM
                if r is None:
                    r = 0  # As per MATLAB code, r is set to 0
                archs, _ = polytope_func(y, n_vertices, r, **polytope_func_kwargs)

                if not np.isnan(archs).any():
                    # Calculate the volume of the polytope
                    # Subtract the last column from all columns
                    arch1_red = archs - archs[:, [n_vertices - 1]]

                    # Take all rows and columns except the last one
                    arch1_red_sub = arch1_red[:, :-1]

                    # Compute the determinant
                    vol = abs(np.linalg.det(arch1_red_sub) / factorial(n_vertices - 1))

                    vol_arch.append(vol)
                    # Save the archetypes
                    min_archs_iter.append(archs)
                else:
                    vol_arch.append(np.nan)
                    min_archs_iter.append(np.nan)
        except Exception as e: # pylint: disable=broad-exception-caught
            # Handle exceptions from the polytope function
            vol_arch.append(np.nan)
            min_archs_iter.append(np.nan)
            print(f"Iteration {i + 1}: polytope function failed with error '{e}'")

    # Find the minimal or maximal volume polytope
    vol_arch = np.array(vol_arch)

    if np.all(np.isnan(vol_arch)):
        raise ValueError("All iterations resulted in NaN volumes. \
            Check your data or polytope function parameters.")

    if polytope_func.__name__ == 'sisal':
        # For sisal, find the minimum volume
        vol_arch_real = np.nanmin(vol_arch)
        min_index = np.nanargmin(vol_arch)
        archs_min = min_archs_iter[min_index]
    else:
        # For SDVMM, find the maximum volume
        vol_arch_real = np.nanmax(vol_arch)
        max_index = np.nanargmax(vol_arch)
        archs_min = min_archs_iter[max_index]

    # ArchsMin up to this point is handled such that each column is an archetype. Therefore, transpose it before returning
    return archs_min.T, vol_arch_real





#faster implementation of main:from __future__ import annotations
# from typing import Callable, Any, Optional, Tuple
# from math import factorial
# from joblib import Parallel, delayed
# import numpy as np


# # ---------- NEW: worker utilities (moved outside main) ----------
# def _sisal_worker(
#     y: np.ndarray,
#     n_vertices: int,
#     det_scale: float,
#     polytope_func: Callable,
#     polytope_kwargs: dict[str, Any],
# ) -> Tuple[float, Optional[np.ndarray]]:
#     """One SISAL iteration (executes in a separate process)."""
#     try:
#         archs, *_ = polytope_func(y, n_vertices, VERBOSE=0, **polytope_kwargs)
#         if np.isnan(archs).any():
#             return np.nan, None
#         arch1_red = archs - archs[:, [n_vertices - 1]]
#         vol = abs(np.linalg.det(arch1_red[:-1, :-1]) / det_scale)
#         return vol, archs[:-1, :n_vertices]
#     except Exception:  # noqa: BLE001  # CHANGED: catch-all stays inside the worker
#         return np.nan, None


# def _sdvmm_worker(
#     y: np.ndarray,
#     n_vertices: int,
#     det_scale: float,
#     polytope_func: Callable,
#     r: float,
#     polytope_kwargs: dict[str, Any],
# ) -> Tuple[float, Optional[np.ndarray]]:
#     """One SDVMM iteration (executes in a separate process)."""
#     try:
#         archs, _ = polytope_func(y, n_vertices, r, **polytope_kwargs)
#         if np.isnan(archs).any():
#             return np.nan, None
#         arch1_red = archs - archs[:, [n_vertices - 1]]
#         vol = abs(np.linalg.det(arch1_red[:, :-1]) / det_scale)
#         return vol, archs
#     except Exception:  # noqa: BLE001
#         return np.nan, None


# # ---------- CHANGED: main API ----------
# def find_min_polytope(
#     data: np.ndarray,
#     polytope_func: Callable,
#     n_vertices: int = 3,
#     num_iter: int = 1000,
#     r: Optional[float] = None,
#     n_jobs: int = -1,                      # NEW: parallelism knob
#     **polytope_func_kwargs: Any,
# ) -> Tuple[np.ndarray, float]:
#     """Parallel, constant-hoisted version of the original routine."""

#     det_scale = factorial(n_vertices - 1)  # CHANGED: pre-compute
#     is_sisal = polytope_func.__name__ == "sisal"

#     # CHANGED: slice data once
#     if is_sisal:
#         y = data[:, :n_vertices].T
#         worker = delayed(_sisal_worker)
#         worker_args = (y, n_vertices, det_scale, polytope_func, polytope_func_kwargs)
#     else:
#         y = data[:, : n_vertices - 1].T
#         worker = delayed(_sdvmm_worker)
#         worker_args = (
#             y,
#             n_vertices,
#             det_scale,
#             polytope_func,
#             0 if r is None else r,          # CHANGED: default r handled once
#             polytope_func_kwargs,
#         )

#     # ---------- NEW: parallel execution ----------
#     results = Parallel(n_jobs=n_jobs, backend="loky")(
#         worker(*worker_args) for _ in range(num_iter)
#     )

#     vols, archs_list = map(np.array, zip(*results))          # CHANGED: vector output

#     if np.all(np.isnan(vols)):
#         raise ValueError(
#             "All iterations produced NaN volumes; check the data or polytope parameters."
#         )

#     # CHANGED: one pass to pick best
#     idx = np.nanargmin(vols) if is_sisal else np.nanargmax(vols)
#     best_archs = archs_list[idx]
#     best_vol = vols[idx]

#     if best_archs is None:
#         raise RuntimeError("Best volume corresponds to invalid archetypes (NaNs)")

#     return best_archs.T, best_vol
