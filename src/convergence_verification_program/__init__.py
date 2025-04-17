# src\convergence_verification_program\__init__.py

"""
Convergence Verification Program

This package provides tools for performing mesh convergence studies and estimating
numerical uncertainty in simulation results according to established standards such as
ASME V&V20 and NASA CFD2030.
"""

__version__ = "0.1.0"

from .mesh import MeshData
from .study import ConvergenceStudy
from .standards import AnalysisStandard, StandardRegistry, StandardValidator
from .validation import validate_mesh_sequence
from .report import export_as_txt, save_txt_report
from .exceptions import ConvergenceAnalysisError

__all__ = [
    "MeshData",
    "ConvergenceStudy",
    "AnalysisStandard",
    "StandardRegistry",
    "StandardValidator",
    "validate_mesh_sequence",
    "export_as_txt",
    "save_txt_report",
    "ConvergenceAnalysisError",
]