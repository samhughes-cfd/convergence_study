# src\convergence_verification_program\local_intra_tuple_convergence_utils.py

import numpy as np
from typing import Union, Tuple

from .numerics import (
    safe_division,
    safe_log,
    calculate_refinement_ratio,
    compute_local_order,
    compute_relative_difference,
    compute_absolute_difference,
    compute_gci
)
from .standards import StandardParameters

def build_refinement_ratios(
    node_counts: Union[np.ndarray, list],
    dim: int
) -> np.ndarray:
    """
    Construct a vector of refinement ratios between successive mesh resolutions.

    Parameters
    ----------
    node_counts : array-like of float
        Sequence of node counts for each mesh level (ascending in resolution).
    dim : int
        Spatial dimension of the mesh (1, 2, or 3).

    Returns
    -------
    np.ndarray
        Vector of refinement ratios (fine / coarse)^(1/dim).

    Raises
    ------
    ValueError
        If any node count is non-positive or dimension is invalid.
    """
    nc = np.asarray(node_counts, dtype=float)
    if np.any(nc <= 0):
        raise ValueError("All node counts must be positive.")
    if dim < 1:
        raise ValueError("Dimension must be at least 1.")
    return (nc[1:] / nc[:-1]) ** (1.0 / dim)

def build_romberg_table(
    values: Union[np.ndarray, list],
    R: np.ndarray
) -> np.ndarray:
    """
    Construct a full Richardson extrapolation (Romberg) table.

    Parameters
    ----------
    values : array-like of float
        Discrete numerical solutions across mesh levels.
    R : np.ndarray
        Refinement ratios (length N-1 for N mesh levels).

    Returns
    -------
    np.ndarray
        Richardson extrapolation table of shape (N, N), where
        E[k, i] is the extrapolated solution at level `k` and index `i`.

    Notes
    -----
    Extrapolation uses:
        E[k, i] = E[k-1, i+1] + (E[k-1, i+1] - E[k-1, i]) / (r^p - 1),
    where `p` is the locally estimated order of convergence.
    """
    v = np.asarray(values, dtype=float)
    n = v.shape[0]
    E = np.full((n, n), np.nan, dtype=float)
    E[0, :n] = v

    for k in range(1, n):
        for i in range(n - k):
            Ei = E[k-1, i]
            Ej = E[k-1, i+1]
            r = R[i]
            p = compute_local_order(Ei, Ej, r)
            denom = r**p - 1 if np.isfinite(p) else 0
            E[k, i] = Ej + (Ej - Ei) / denom if denom != 0 else np.nan
    return E

def build_extrapolation_bounds(E: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute absolute and relative extrapolation error bounds from Richardson table.

    Parameters
    ----------
    E : np.ndarray
        Richardson extrapolation table (N x N).

    Returns
    -------
    abs_err : np.ndarray
        Absolute errors: |E[k,i] - E[k-1,i+1]|.
    rel_err : np.ndarray
        Relative errors: |(E[k,i] - E[k-1,i+1]) / E[k,i]|.
    """
    n = E.shape[0]
    abs_err = np.full_like(E, np.nan)
    rel_err = np.full_like(E, np.nan)

    for k in range(1, n):
        for i in range(n - k):
            Ek_i = E[k, i]
            Ekm1_ip1 = E[k - 1, i + 1]
            if np.isfinite(Ek_i) and np.isfinite(Ekm1_ip1):
                abs_err[k, i] = compute_absolute_difference(Ek_i, Ekm1_ip1)
                rel_err[k, i] = compute_relative_difference(Ek_i, Ekm1_ip1)

    return abs_err, rel_err

def build_gci_confidence_bounds(
    E: np.ndarray,
    GCI: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Construct symmetric confidence intervals from GCI values.

    Parameters
    ----------
    E : np.ndarray
        Richardson table (N x N).
    GCI : np.ndarray
        Grid Convergence Index values in percent (N x N).

    Returns
    -------
    lower : np.ndarray
        Lower bound: E * (1 - GCI/100).
    upper : np.ndarray
        Upper bound: E * (1 + GCI/100).
    """
    lower = E * (1 - GCI / 100.0)
    upper = E * (1 + GCI / 100.0)
    return lower, upper

def build_order_table(
    E: np.ndarray,
    R: np.ndarray
) -> np.ndarray:
    """
    Build observed order-of-accuracy table from Richardson extrapolation data.

    Parameters
    ----------
    E : np.ndarray
        Richardson table.
    R : np.ndarray
        Local refinement ratios.

    Returns
    -------
    P : np.ndarray
        Table of observed orders of convergence.
    """
    n = E.shape[0]
    P = np.full_like(E, np.nan)

    for k in range(1, n):
        for i in range(n - k):
            P[k, i] = compute_local_order(E[k-1, i], E[k-1, i+1], R[i])
    return P

def build_gci_and_rel_eps(
    E: np.ndarray,
    R: np.ndarray,
    safety_factor: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute Grid Convergence Index (GCI) and relative error values from Richardson table.

    Parameters
    ----------
    E : np.ndarray
        Richardson table.
    R : np.ndarray
        Refinement ratios.
    safety_factor : float
        GCI safety multiplier (e.g., 1.25 or 3.0).

    Returns
    -------
    GCI : np.ndarray
        GCI table (% values).
    Rel : np.ndarray
        Relative error table.
    """
    n = E.shape[0]
    GCI = np.full_like(E, np.nan)
    Rel = np.full_like(E, np.nan)

    for k in range(1, n):
        for i in range(n - k):
            Ei = E[k-1, i]
            Ej = E[k-1, i+1]
            rel = compute_relative_difference(Ei, Ej)
            Rel[k, i] = rel
            p = compute_local_order(Ei, Ej, R[i])
            GCI[k, i] = compute_gci(safety_factor, rel, R[i], p)
    return GCI, Rel

def build_gci_ratio_table(
    GCI: np.ndarray
) -> np.ndarray:
    """
    Compute the GCI ratio between successive entries in each level.

    Parameters
    ----------
    GCI : np.ndarray
        GCI table (N x N).

    Returns
    -------
    GCI_ratio : np.ndarray
        Table of GCI[k, i+1] / GCI[k, i] values.
    """
    n = GCI.shape[0]
    GCI_ratio = np.full_like(GCI, np.nan)
    for k in range(1, n):
        for i in range(n - k - 1):
            GCI_ratio[k, i] = safe_division(GCI[k, i+1], GCI[k, i])
    return GCI_ratio

def build_level_flags(
    diffs: np.ndarray,
    gci_vals: np.ndarray,
    asymptotic_ratio: float
) -> Tuple[bool, bool, bool]:
    """
    Determine flags indicating convergence quality across levels.

    Parameters
    ----------
    diffs : np.ndarray
        Differences E[k-1,i] - E[k-1,i+1].
    gci_vals : np.ndarray
        GCI values for level k.
    asymptotic_ratio : float
        Tolerance threshold to assert asymptotic behavior.

    Returns
    -------
    monotonic : bool
        True if all differences share the same sign.
    sign_flip : bool
        True if there is any sign change between adjacent differences.
    asymptotic : bool
        True if GCI drops by a factor greater than asymptotic_ratio.
    """
    monotonic = np.all(diffs > 0) or np.all(diffs < 0)
    sign_flip = np.any(np.sign(diffs[:-1]) != np.sign(diffs[1:]))
    asymptotic = np.all(gci_vals[1:] < asymptotic_ratio * gci_vals[:-1]) if len(gci_vals) > 1 else False
    return monotonic, sign_flip, asymptotic