import numpy as np
from typing import Union

def safe_division(numerator: float, denominator: float, eps: float = 1e-12) -> float:
    """
    Perform a stabilized division to prevent division by very small values.

    Parameters
    ----------
    numerator : float
        The numerator of the division.
    denominator : float
        The denominator of the division.
    eps : float, optional
        Threshold below which the denominator is considered too small (default is 1e-12).

    Returns
    -------
    float
        The result of the division, or ±infinity if the denominator is too small.
    
    Raises
    ------
    ValueError
        If numerator or denominator is not finite.
    """
    if not np.isfinite(numerator) or not np.isfinite(denominator):
        raise ValueError("Inputs must be finite numbers.")

    if abs(denominator) < eps:
        return np.inf if numerator >= 0 else -np.inf
    return numerator / denominator

def safe_log(value: float, eps: float = 1e-12) -> float:
    """
    Compute the logarithm of a value, stabilized against near-zero input.

    Parameters
    ----------
    value : float
        The value to compute the logarithm of.
    eps : float, optional
        The minimum threshold for log input to avoid singularity (default is 1e-12).

    Returns
    -------
    float
        The natural logarithm of the stabilized input.

    Raises
    ------
    ValueError
        If the input is not positive or not finite.
    """
    if not np.isfinite(value):
        raise ValueError("Input must be a finite number.")
    if value <= 0:
        raise ValueError("Log input must be positive.")
    return np.log(max(value, eps))

def calculate_refinement_ratio(coarse_nodes: Union[int, float], fine_nodes: Union[int, float], dim: int) -> float:
    """
    Compute the dimension-aware refinement ratio between two mesh resolutions.

    Parameters
    ----------
    coarse_nodes : int or float
        Node count of the coarse mesh.
    fine_nodes : int or float
        Node count of the fine mesh.
    dim : int
        Number of spatial dimensions (e.g., 2 or 3).

    Returns
    -------
    float
        The geometric refinement ratio.

    Raises
    ------
    ValueError
        If inputs are not strictly positive or if dim < 1.
    """
    if coarse_nodes <= 0 or fine_nodes <= 0:
        raise ValueError("Node counts must be strictly positive.")
    if dim < 1:
        raise ValueError("Dimension must be at least 1.")
    return (fine_nodes / coarse_nodes) ** (1 / dim)