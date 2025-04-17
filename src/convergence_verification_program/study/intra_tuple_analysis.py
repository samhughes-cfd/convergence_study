# src\convergence_verification_program\study\intra_tuple_analysis.py

from typing import List, Dict, Tuple
import numpy as np

from ..mesh import MeshData
from ..numerics import safe_division
from ..local_intra_tuple_convergence_utils import (
    build_refinement_ratios,
    build_romberg_table,
    build_order_table,
    build_gci_and_rel_eps,
    build_level_flags,
    build_gci_ratio_table,
    build_extrapolation_bounds,
    build_gci_confidence_bounds
)

def classify_convergence_type(
    asymptotic: bool,
    sign_flip: bool,
    order: float,
    order_tol: float
) -> str:
    """
    Classify convergence based on asymptotic trend, oscillation, and order agreement.

    Parameters
    ----------
    asymptotic : bool
        True if GCI ratio indicates asymptotic convergence.
    sign_flip : bool
        True if sign change observed between solution differences.
    order : float
        Observed convergence order.
    order_tol : float
        Tolerance for deviation from nearest integer order.

    Returns
    -------
    str
        One of 'asymptotic', 'oscillatory', or 'uncertain'.
    """
    if asymptotic and not sign_flip and abs(order - round(order)) < order_tol:
        return "asymptotic"
    if sign_flip:
        return "oscillatory"
    return "uncertain"

def analyze_parameter(
    meshes: List[MeshData],
    parameter: str,
    tuple_size: int,
    safety_factor: float,
    asymptotic_ratio: float
) -> List[Dict]:
    """
    Analyze convergence behavior of a given parameter across all mesh tuples.

    Parameters
    ----------
    meshes : List[MeshData]
        Mesh data objects sorted by increasing resolution.
    parameter : str
        Parameter to analyze (e.g., velocity, pressure).
    tuple_size : int
        Number of meshes to include per analysis tuple.
    safety_factor : float
        Safety factor used in GCI estimation.
    asymptotic_ratio : float
        Ratio threshold used to detect asymptotic convergence.

    Returns
    -------
    List[Dict]
        List of dictionaries containing convergence results per mesh tuple.
    """
    n = tuple_size
    results: List[Dict] = []

    for start in range(len(meshes) - n + 1):
        subset = meshes[start:start + n]
        vals = np.array([m.parameters[parameter] for m in subset], dtype=float)
        if np.any(np.isnan(vals)):
            continue

        r = build_refinement_ratios([m.node_count for m in subset], subset[0].dim)
        R = build_romberg_table(vals, r)
        p = build_order_table(R, r)
        GCI, rel_eps = build_gci_and_rel_eps(R, r, safety_factor)
        GCI_ratio = build_gci_ratio_table(GCI)
        abs_err, rel_err = build_extrapolation_bounds(R)
        gci_lower, gci_upper = build_gci_confidence_bounds(R, GCI)

        monotonic_flags, signflip_flags, asymp_flags = {}, {}, {}
        for lvl in range(1, n):
            diffs = R[lvl-1, :n-lvl] - R[lvl-1, 1:n-lvl+1]
            gci_vals = GCI[lvl, :n-lvl]
            mono, sf, asym = build_level_flags(diffs, gci_vals, asymptotic_ratio)
            monotonic_flags[lvl] = mono
            signflip_flags[lvl] = sf
            asymp_flags[lvl] = asym

        lvl = 1
        order_fp = p[lvl, n-lvl-1]
        order_avg = float(np.nanmean(p[lvl, :n-lvl]))
        gci_fp = GCI[lvl, n-lvl-1]
        gci_start = GCI[lvl, 0]
        global_gci = float(safe_division(gci_fp, gci_start)) if gci_start else None

        results.append({
            "mesh_tuple": [m.identifier for m in subset],
            "local_intra_tuple": {
                "r_table": r,
                "R_table": R,
                "p_table": p,
                "GCI_table": GCI,
                "rel_eps_table": rel_eps,
                "GCI_ratio_table": GCI_ratio,
                "abs_extrapolation_error": abs_err,
                "rel_extrapolation_error": rel_err,
                "confidence_interval_lower": gci_lower,
                "confidence_interval_upper": gci_upper,
                "monotonic_table": monotonic_flags,
                "signflip_table": signflip_flags,
                "asymptotic_table": asymp_flags,
            },
            "global_intra_tuple": {
                "order_finest_pair": float(round(order_fp, 3)),
                "order_tuple_avg": float(round(order_avg, 3)),
                "gci_finest_pair": float(round(gci_fp, 3)),
                "global_gci_ratio": global_gci
            }
        })

    return results