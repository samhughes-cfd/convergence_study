class ConvergenceAnalysisError(Exception):
    """
    Base exception for all convergence analysis errors.

    This should be used as the root class for exception handling in convergence pipelines.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Parameters
        ----------
        message : str
            Description of the error.
        details : dict, optional
            Additional structured data to help with debugging (e.g., parameter values, indices).
        """
        super().__init__(message)
        self.details = details or {}

    def __str__(self):
        base = super().__str__()
        if self.details:
            return f"{base} | Details: {self.details}"
        return base


class InvalidRefinementSequenceError(ConvergenceAnalysisError):
    """
    Raised when mesh refinement ratios are out of allowed bounds.
    """


class NonMonotonicConvergenceError(ConvergenceAnalysisError):
    """
    Raised when observed convergence order shows irregular (non-monotonic) behavior.
    """


class AsymptoticConvergenceFailure(ConvergenceAnalysisError):
    """
    Raised when the computed GCI values fail to meet the asymptotic convergence criteria.
    """


class InvalidMeshParameterError(ConvergenceAnalysisError):
    """
    Raised when mesh parameters are missing or contain invalid (non-numeric or None) values.
    """


class InsufficientMeshCountError(ConvergenceAnalysisError):
    """
    Raised when the number of provided mesh levels is insufficient for triplet-based analysis.
    """


class UnstableGCICalculationError(ConvergenceAnalysisError):
    """
    Raised when GCI computation fails due to singularities, numerical instability, or invalid order.
    """