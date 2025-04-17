# src\convergence_verification_program\study.py

from typing import List, Dict, Optional
import warnings

from .mesh import MeshData
from .standards import StandardValidator, AnalysisStandard
from .validation import validate_mesh_sequence
from .config import STRICT_MODE
from study.intra_tuple_analysis import performance_analysis

def classify_convergence_type(
    asymptotic: bool,
    sign_flip: bool,
    order: float,
    order_tol: float
) -> str:
    """
    Classify convergence behavior based on observed convergence trends.

    Parameters
    ----------
    asymptotic : bool
        Flag indicating whether the convergence is asymptotic, determined by
        successive decreases in the Grid Convergence Index (GCI).
    sign_flip : bool
        True if any sign change occurs in the error differences, indicating
        potential oscillatory or non-monotonic behavior.
    order : float
        Observed convergence order for the finest resolution mesh pair.
    order_tol : float
        Numerical tolerance used to determine proximity to an expected integer
        order of convergence.

    Returns
    -------
    str
        A string classification of the convergence type. One of:
        - 'asymptotic'
        - 'oscillatory'
        - 'uncertain'
    """
    if asymptotic and not sign_flip and abs(order - round(order)) < order_tol:
        return "asymptotic"
    if sign_flip:
        return "oscillatory"
    return "uncertain"


class ConvergenceStudy:
    """
    Orchestrates intra-tuple convergence analysis for a mesh sequence.

    This class performs tuple-wise Richardson extrapolation, GCI analysis,
    and convergence classification for each scalar parameter in a CFD or
    numerical simulation study. It validates against a predefined standard,
    and reports summary metrics such as observed order, extrapolation error,
    and asymptotic convergence indicators.

    Parameters
    ----------
    meshes : List[MeshData]
        A list of MeshData objects, sorted in ascending mesh resolution.
    standard : AnalysisStandard
        The convergence analysis standard (e.g., ASME, ISO) specifying GCI
        safety factors, asymptotic thresholds, and reporting behavior.
    tuple_size : int, optional
        Number of meshes per tuple for local convergence analysis. Default is 3.

    Attributes
    ----------
    meshes : List[MeshData]
        Sorted list of input meshes.
    validator : StandardValidator
        Validator with standard-specific numerical thresholds and tolerances.
    tuple_size : int
        Number of meshes to include in each analysis tuple.
    results : Optional[Dict]
        Final structured report produced by the analysis.
    """

    def __init__(
        self,
        meshes: List[MeshData],
        standard: AnalysisStandard,
        tuple_size: int = 3
    ):
        if len(meshes) < tuple_size:
            raise ValueError(f"Require at least {tuple_size} meshes, got {len(meshes)}.")
        self.meshes = sorted(meshes, key=lambda m: m.node_count)
        self.validator = StandardValidator.from_standard(standard)
        self.tuple_size = tuple_size
        self.results: Optional[Dict] = None
        if STRICT_MODE:
            warnings.simplefilter("error", RuntimeWarning)

    def perform_analysis(self) -> Dict:
        """
        Execute convergence analysis across all mesh tuples and parameters.

        Returns
        -------
        Dict
            Structured report containing:
            - analysis standard identifier
            - tuple size used
            - mesh identifiers in the study
            - parameter-wise convergence results per tuple

        Raises
        ------
        ValueError
            If mesh sequence fails standard compliance checks.
        RuntimeWarning or RuntimeError
            If STRICT_MODE is active and numerical anomalies are detected.
        """
        validate_mesh_sequence(
            self.meshes,
            self.validator.parameters,
            strict=True
        )

        report: Dict = {
            "standard": self.validator.standard.value,
            "tuple_size": self.tuple_size,
            "meshes": [m.identifier for m in self.meshes],
            "parameters": {}
        }

        for param in self.meshes[0].parameters:
            report["parameters"][param] = {
                "tuples": analyze_parameter(
                    meshes=self.meshes,
                    parameter=param,
                    tuple_size=self.tuple_size,
                    safety_factor=self.validator.parameters.safety_factor,
                    asymptotic_ratio=self.validator.parameters.asymptotic_ratio
                )
            }

        self.results = report
        return report