# src\convergence_verification_program\standards.py

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple, List, Union
from types import MappingProxyType
from pydantic import BaseModel


class AnalysisStandard(Enum):
    """Supported verification standards."""
    ASME_VV20_2009 = "ASME V&V20-2009"
    NASA_CFD2030 = "NASA CFD Vision 2030"
    CUSTOM = "User-defined"


@dataclass(frozen=True)
class StandardParameters:
    """
    Numerical parameters for a specific analysis standard.

    Attributes
    ----------
    min_refinement : float
        Minimum allowed refinement ratio.
    max_refinement : float
        Maximum allowed refinement ratio.
    asymptotic_ratio : float
        Factor to check for asymptotic convergence.
    safety_factor : float
        Safety factor for numerical uncertainty.
    order_tolerance : float
        Acceptable tolerance in order of accuracy.
    residual_tol : float
        Default residual tolerance.
    """
    min_refinement: float
    max_refinement: float
    asymptotic_ratio: float
    safety_factor: float
    order_tolerance: float
    residual_tol: float = 1e-6

    def to_dict(self) -> Dict[str, float]:
        """
        Convert parameters to dictionary form.

        Returns
        -------
        Dict[str, float]
            Dictionary representation of the parameters.
        """
        return {
            "min_refinement": self.min_refinement,
            "max_refinement": self.max_refinement,
            "asymptotic_ratio": self.asymptotic_ratio,
            "safety_factor": self.safety_factor,
            "order_tolerance": self.order_tolerance,
            "residual_tol": self.residual_tol,
        }


class StandardRegistry:
    """
    Central registry for standard configurations.
    Supports default and dynamically added custom standards.
    """

    _PARAMETERS = {
        AnalysisStandard.ASME_VV20_2009: StandardParameters(
            min_refinement=1.1,
            max_refinement=3.0,
            asymptotic_ratio=0.3,
            safety_factor=1.25,
            order_tolerance=0.1
        ),
        AnalysisStandard.NASA_CFD2030: StandardParameters(
            min_refinement=1.3,
            max_refinement=2.0,
            asymptotic_ratio=0.25,
            safety_factor=1.15,
            order_tolerance=0.05
        )
    }

    @classmethod
    def get_parameters(cls, standard: Union[AnalysisStandard, str]) -> StandardParameters:
        """
        Retrieve parameters for specified standard.

        Parameters
        ----------
        standard : AnalysisStandard or str
            The selected verification standard.

        Returns
        -------
        StandardParameters
            Numerical parameters associated with the standard.

        Raises
        ------
        KeyError
            If the standard is not registered.
        """
        key = standard if isinstance(standard, AnalysisStandard) else AnalysisStandard(standard)
        if key not in cls._PARAMETERS:
            raise KeyError(f"Standard '{key}' not registered.")
        return cls._PARAMETERS[key]

    @classmethod
    def register_custom_standard(cls, name: str, params: Dict[str, float]) -> None:
        """
        Register a custom standard.

        Parameters
        ----------
        name : str
            Name of the custom standard.
        params : Dict[str, float]
            Dictionary with required keys matching StandardParameters.

        Raises
        ------
        ValueError
            If required parameters are missing or invalid.
        """
        try:
            standard_enum = AnalysisStandard(name) if name in AnalysisStandard.__members__ else AnalysisStandard.CUSTOM
        except ValueError:
            standard_enum = AnalysisStandard.CUSTOM

        cls._PARAMETERS[standard_enum] = StandardParameters(**params)


class StandardValidator(BaseModel):
    """
    Performs standards-compliant validation checks.

    Attributes
    ----------
    standard : AnalysisStandard
        Verification standard being used.
    parameters : StandardParameters
        Numerical parameters associated with the standard.
    """
    standard: AnalysisStandard
    parameters: StandardParameters

    @classmethod
    def from_standard(cls, standard: Union[AnalysisStandard, str]) -> "StandardValidator":
        """
        Initialize validator from a standard.

        Parameters
        ----------
        standard : AnalysisStandard or str
            The selected verification standard.

        Returns
        -------
        StandardValidator
            A validator instance with fetched parameters.
        """
        return cls(
            standard=standard if isinstance(standard, AnalysisStandard) else AnalysisStandard(standard),
            parameters=StandardRegistry.get_parameters(standard)
        )

    def validate_refinement(self, ratio: float) -> Tuple[bool, str]:
        """
        Check refinement ratio compliance.

        Parameters
        ----------
        ratio : float
            The refinement ratio to validate.

        Returns
        -------
        Tuple[bool, str]
            Compliance flag and explanatory message.
        """
        if not (self.parameters.min_refinement <= ratio <= self.parameters.max_refinement):
            return False, (
                f"Ratio {ratio:.2f} outside allowed range "
                f"[{self.parameters.min_refinement}, {self.parameters.max_refinement}]"
            )
        return True, "Valid refinement ratio"

    def is_asymptotic(self, previous_gci: float, current_gci: float) -> bool:
        """
        Check asymptotic convergence criteria.

        Parameters
        ----------
        previous_gci : float
            GCI value from coarser grid.
        current_gci : float
            GCI value from finer grid.

        Returns
        -------
        bool
            True if convergence is asymptotic.
        """
        return current_gci < self.parameters.asymptotic_ratio * previous_gci


class ComplianceReport:
    """
    Generates standards-compliant documentation.
    """

    def __init__(self, standard: AnalysisStandard):
        """
        Initialize the compliance report.

        Parameters
        ----------
        standard : AnalysisStandard
            The selected verification standard.
        """
        self.validator = StandardValidator.from_standard(standard)

    def generate_section(self, analysis_data: Dict[str, List[float]]) -> str:
        """
        Produces Markdown-formatted compliance section.

        Parameters
        ----------
        analysis_data : Dict[str, List[float]]
            Dictionary containing 'ratios', 'gci', and 'orders'.

        Returns
        -------
        str
            Markdown text summarizing compliance.
        """
        required_keys = ['ratios', 'gci', 'orders']
        for key in required_keys:
            if key not in analysis_data:
                raise KeyError(f"Missing required key in analysis_data: '{key}'")

        return (
            f"## {self.validator.standard.value} Compliance\n"
            f"**Refinement Validation:** {self._format_refinement(analysis_data['ratios'])}\n"
            f"**Asymptotic Convergence:** {self._format_asymptotic(analysis_data['gci'])}\n"
            f"**Order Consistency:** {self._format_order(analysis_data['orders'])}"
        )

    def _format_refinement(self, ratios: List[float]) -> str:
        messages = [self.validator.validate_refinement(ratio)[1] for ratio in ratios]
        return "; ".join(messages)

    def _format_asymptotic(self, gci: List[float]) -> str:
        flags = [
            self.validator.is_asymptotic(gci[i - 1], gci[i])
            for i in range(1, len(gci))
        ]
        return "Convergent" if all(flags) else "Non-asymptotic behavior detected"

    def _format_order(self, orders: List[float]) -> str:
        avg_order = sum(orders) / len(orders)
        delta = abs(avg_order - round(avg_order))
        return (
            f"Average order: {avg_order:.2f} "
            f"({'Acceptable' if delta < self.validator.parameters.order_tolerance else 'Uncertain'})"
        )
