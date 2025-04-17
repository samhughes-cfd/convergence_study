# src\convergence_verification_program\numerics.py

import numpy as np
import warnings
from typing import Union
from .config import STRICT_MODE

# If in strict mode, convert warnings to errors globally
if STRICT_MODE:
    warnings.simplefilter("error", RuntimeWarning)

def safe_division(
    numerator: Union[float, np.ndarray],
    denominator: Union[float, np.ndarray],
    eps: float = 1e-12
) -> Union[float, np.ndarray]:
    """
    Perform numerically stable division for scalars or arrays, avoiding division by near-zero denominators.

    Parameters
    ----------
    numerator : float or ndarray
        Numerator(s) of the division.
    denominator : float or ndarray
        Denominator(s) of the division.
    eps : float, optional
        Threshold below which denominators are considered near-zero (default: 1e-12).

    Returns
    -------
    float or ndarray
        Quotient(s) with `inf` where denominator is too small.

    Raises
    ------
    ValueError
        If any input is not finite.
    RuntimeWarning or RuntimeError
        Triggered for near-zero denominators depending on STRICT_MODE.
    """
    num = np.asarray(numerator, dtype=float)
    den = np.asarray(denominator, dtype=float)

    if not np.all(np.isfinite(num)) or not np.all(np.isfinite(den)):
        raise ValueError("Inputs to safe_division must be finite.")

    small = np.abs(den) < eps
    if np.any(small):
        msg = f"Division by near-zero detected: denominator abs<{eps}"
        if STRICT_MODE:
            raise RuntimeError(msg)
        warnings.warn(msg, RuntimeWarning)

    result = np.empty_like(num, dtype=float)
    mask = ~small
    result[mask] = num[mask] / den[mask]
    result[small] = np.sign(num[small]) * np.inf

    return result.item() if result.shape == () else result

def safe_log(
    value: Union[float, np.ndarray],
    eps: float = 1e-12
) -> Union[float, np.ndarray]:
    """
    Compute natural logarithm of input(s), flooring values below `eps` to prevent log(0).

    Parameters
    ----------
    value : float or ndarray
        Input value(s) to compute the natural logarithm of.
    eps : float, optional
        Minimum allowable argument for log computation (default: 1e-12).

    Returns
    -------
    float or ndarray
        log(max(value, eps)) for stability.

    Raises
    ------
    ValueError
        If any input is non-positive or non-finite.
    RuntimeWarning or RuntimeError
        If flooring occurs, depending on STRICT_MODE.
    """
    v = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(v)):
        raise ValueError("Inputs to safe_log must be finite.")
    if np.any(v <= 0):
        raise ValueError("Inputs to safe_log must be positive.")

    floor_mask = v < eps
    if np.any(floor_mask):
        msg = f"Values below eps={eps} floored for log stability."
        if STRICT_MODE:
            raise RuntimeError(msg)
        warnings.warn(msg, RuntimeWarning)
    v_clipped = np.where(floor_mask, eps, v)
    result = np.log(v_clipped)
    return result.item() if result.shape == () else result

def calculate_refinement_ratio(
    coarse_nodes: Union[int, float, np.ndarray],
    fine_nodes: Union[int, float, np.ndarray],
    dim: int
) -> Union[float, np.ndarray]:
    """
    Compute the mesh refinement ratio (fine / coarse)^(1/dim).

    Parameters
    ----------
    coarse_nodes : int, float, or ndarray
        Node counts for the coarser mesh level.
    fine_nodes : int, float, or ndarray
        Node counts for the finer mesh level.
    dim : int
        Spatial dimension (1, 2, or 3).

    Returns
    -------
    float or ndarray
        Refinement ratio(s) for each mesh pair.

    Raises
    ------
    ValueError
        If node counts are non-positive or dimension is invalid.
    """
    c = np.asarray(coarse_nodes, dtype=float)
    f = np.asarray(fine_nodes, dtype=float)
    if np.any(c <= 0) or np.any(f <= 0):
        raise ValueError("Node counts must be strictly positive.")
    if dim < 1:
        raise ValueError("Spatial dimension must be at least 1.")

    ratio = (f / c) ** (1.0 / dim)
    return ratio.item() if ratio.shape == () else ratio

def compute_local_order(Ei: float, Ej: float, r: float, eps: float = 1e-12) -> float:
    """
    Estimate the observed order of convergence between two mesh levels.

    Parameters
    ----------
    Ei : float
        Solution on coarser mesh.
    Ej : float
        Solution on finer mesh.
    r : float
        Local refinement ratio.
    eps : float, optional
        Threshold for difference magnitude (default: 1e-12).

    Returns
    -------
    float
        Observed order `p`, or NaN if invalid.
    """
    if r > 0 and abs(Ei - Ej) > eps:
        return safe_log(abs(Ei - Ej), eps) / safe_log(r, eps)
    return np.nan

def compute_relative_difference(a: float, b: float, eps: float = 1e-12) -> float:
    """
    Compute the relative difference |a - b| / |b| with division safety.

    Parameters
    ----------
    a : float
        First value.
    b : float
        Second value (typically the reference).
    eps : float, optional
        Stability threshold (default: 1e-12).

    Returns
    -------
    float
        Relative difference.
    """
    return safe_division(abs(a - b), abs(b), eps)

def compute_absolute_difference(a: float, b: float) -> float:
    """
    Compute the absolute difference |a - b|.

    Parameters
    ----------
    a : float
        First value.
    b : float
        Second value.

    Returns
    -------
    float
        Absolute difference.
    """
    return abs(a - b)

def compute_gci(safety_factor: float, rel_error: float, r: float, p: float) -> float:
    """
    Compute the Grid Convergence Index (GCI) for a given refinement step.

    Parameters
    ----------
    safety_factor : float
        User-defined safety multiplier (e.g. 1.25 or 3.0).
    rel_error : float
        Relative error between coarse and fine mesh levels.
    r : float
        Refinement ratio between the meshes.
    p : float
        Observed order of convergence.

    Returns
    -------
    float
        GCI as a percentage, or NaN if denominator is invalid.
    """
    denom = r ** p - 1
    if denom == 0:
        return np.nan
    return safety_factor * rel_error / denom * 100