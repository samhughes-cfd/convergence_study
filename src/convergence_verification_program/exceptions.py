# src\convergence_verification_program\exceptions.py

class ConvergenceAnalysisError(Exception):
    """
    Base exception for all convergence analysis errors.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Parameters
        ----------
        message : str
            Description of the error.
        details : dict, optional
            Structured debugging metadata (e.g., failed indices, values).
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        base = super().__str__()
        if self.details:
            return f"{base} | Details: {self.details}"
        return base

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"details={self.details!r})"
        )


class InvalidRefinementSequenceError(ConvergenceAnalysisError):
    """
    Raised when mesh refinement ratios are out of bounds or improperly defined.
    """


class NonMonotonicConvergenceError(ConvergenceAnalysisError):
    """
    Raised when observed convergence order exhibits oscillation or irregular jumps.
    """


class AsymptoticConvergenceFailure(ConvergenceAnalysisError):
    """
    Raised when GCI values fail to meet the required asymptotic convergence criteria.
    """


class InvalidMeshParameterError(ConvergenceAnalysisError):
    """
    Raised when mesh parameters are missing or contain invalid values.
    """


class InsufficientMeshCountError(ConvergenceAnalysisError):
    """
    Raised when fewer than three mesh levels are provided.
    """


class UnstableGCICalculationError(ConvergenceAnalysisError):
    """
    Raised when GCI calculation fails due to instability or singularity.
    """