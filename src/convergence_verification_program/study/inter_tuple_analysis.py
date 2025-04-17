# src\convergence_verification_program\study\inter_tuple_analysis.py

from typing import List, Dict, Optional
import numpy as np

def compute_inter_tuple_metrics(
    all_results: List[Dict]
) -> List[Dict]:
    """
    Compute changes in convergence metrics between adjacent mesh tuples.

    Parameters
    ----------
    all_results : List[Dict]
        List of convergence results from intra-tuple analysis. Each entry must contain
        a "global_intra_tuple" dictionary with keys 'order_finest_pair' and 'gci_finest_pair'.

    Returns
    -------
    List[Dict]
        A new list of dictionaries with "mesh_tuple", "local_inter_tuple", and "global_inter_tuple"
        entries populated for each index i >= 1. The first entry is skipped since no prior tuple exists.
    """
    inter_results: List[Dict] = []

    for i in range(1, len(all_results)):
        prev = all_results[i - 1]["global_intra_tuple"]
        curr = all_results[i]["global_intra_tuple"]

        order_prev = prev["order_finest_pair"]
        order_curr = curr["order_finest_pair"]
        gci_prev = prev["gci_finest_pair"]
        gci_curr = curr["gci_finest_pair"]

        delta_order = round(order_curr - order_prev, 3)
        delta_gci = round(gci_curr - gci_prev, 3)

        rel_order = round(abs(delta_order / order_prev), 3) if order_prev else None
        rel_gci = round(abs(delta_gci / gci_prev), 3) if gci_prev else None

        inter_results.append({
            "mesh_tuple": all_results[i]["mesh_tuple"],
            "local_inter_tuple": {
                "delta_order_vs_prev_tuple": delta_order,
                "delta_gci_vs_prev_tuple": delta_gci
            },
            "global_inter_tuple": {
                "relative_order_change": rel_order,
                "relative_gci_change": rel_gci
            }
        })

    return inter_results
