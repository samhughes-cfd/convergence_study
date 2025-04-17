# src\convergence_verification_program\config.py

"""
Global configuration for convergence verification program.

This module centralizes shared runtime settings like strictness,
verbosity, and numerical tolerances. It can be imported anywhere
in the codebase for consistent behavior.
"""

# === Runtime Modes ===
STRICT_MODE: bool = True
"""Promote warnings (e.g., near-zero division/log) to runtime errors."""

VERBOSE_OUTPUT: bool = True
"""Enable console printouts during validation and analysis phases."""

# === Numerical Tolerances ===
EPSILON: float = 1e-12
"""Threshold for treating values as near-zero in division/logarithm."""

# === Precision Settings ===
REPORT_FLOAT_PRECISION: int = 6
"""Number of decimal places used in plain text or markdown output."""

# === Future-Proofing Placeholder ===
ENABLE_LOGGING: bool = False
"""Enable detailed log file output (planned feature)."""

# === Convergence Report Float Precision ===
REPORT_FLOAT_PRECISION: int = 6
"""Number of decimal places to use in all report output (TXT, JSON, Markdown, LaTeX)."""

# === Convergence Report Format ===
REPORT_FORMAT: str = "txt"  # Options: "txt", "md", "tex"
"""Output format for saved reports."""