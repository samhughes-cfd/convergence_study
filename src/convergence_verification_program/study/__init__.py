"""
study/__init__.py

This module provides unified access to all convergence study routines, including:
- Intra-tuple analysis (Romberg extrapolation, GCI, order estimation)
- Inter-tuple analysis (deltas, trend tracking)

This package assumes that all mesh and parameter validation has been handled externally.
"""

from .intra_tuple_analysis import classify_convergence_type, analyze_parameter

__all__ = [
    "classify_convergence_type",
    "analyze_parameter"
]
