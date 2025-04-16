from typing import List, Dict, Optional
from .mesh import MeshData
from .standards import StandardValidator, AnalysisStandard
from .numerics import calculate_refinement_ratio, safe_division, safe_log
from .validation import validate_mesh_sequence
import numpy as np


class ConvergenceStudy:
    """
    Performs a convergence study using mesh data and a specified verification standard.
    Presents intra-triplet (local) and inter-triplet (trend) convergence metrics,
    including monotonicity checks, normalized residuals, and error sign propagation.
    """

    def __init__(self, meshes: List[MeshData], standard: AnalysisStandard):
        if len(meshes) < 3:
            raise ValueError("At least 3 meshes are required for a convergence study.")
        self.meshes = sorted(meshes, key=lambda x: x.node_count)
        self.validator = StandardValidator.from_standard(standard)
        self.results: Optional[Dict] = None

    def perform_analysis(self) -> Dict:
        dim = getattr(self.validator.parameters, 'dim', 3)
        validate_mesh_sequence(self.meshes, self.validator.parameters, dim=dim, strict=True)

        report = {
            "standard": self.validator.standard.value,
            "meshes": [m.identifier for m in self.meshes],
            "parameters": {}
        }

        for param in self.meshes[0].parameters:
            triplet_data = self._analyze_parameter(param)
            report["parameters"][param] = {
                "triplets": triplet_data
            }

        self.results = report
        return report

    def _analyze_parameter(self, parameter: str) -> List[Dict]:
        triplet_data = []
        dim = getattr(self.validator.parameters, 'dim', 3)

        for i in range(len(self.meshes) - 2):
            m1, m2, m3 = self.meshes[i:i + 3]
            v1, v2, v3 = m1.parameters.get(parameter), m2.parameters.get(parameter), m3.parameters.get(parameter)

            if any(v is None for v in [v1, v2, v3]):
                continue

            try:
                r21 = calculate_refinement_ratio(m1.node_count, m2.node_count, dim)
                r32 = calculate_refinement_ratio(m2.node_count, m3.node_count, dim)

                eps21 = v1 - v2
                eps32 = v2 - v3

                p = safe_log(abs(safe_division(eps21, eps32))) / safe_log(r21)

                gci21 = self.validator.parameters.safety_factor * abs(safe_division(v2 - v1, v2)) / (r21 ** p - 1) * 100
                gci32 = self.validator.parameters.safety_factor * abs(safe_division(v3 - v2, v3)) / (r32 ** p - 1) * 100
                gci_ratio = safe_division(gci32, gci21)

                richardson_ext = v3 + (v3 - v2) / (r32 ** p - 1)

                monotonic = (v1 > v2 > v3) or (v1 < v2 < v3)
                rel_eps21 = safe_division(abs(eps21), abs(v2))
                rel_eps32 = safe_division(abs(eps32), abs(v3))
                sign_flip = np.sign(eps21) != np.sign(eps32)

                prev = triplet_data[-1] if triplet_data else None
                delta_order = p - prev["order"] if prev else None
                delta_gci = gci32 - prev["gci_32"] if prev else None
                asymptotic = self.validator.is_asymptotic(prev["gci_32"], gci32) if prev else False

                triplet_data.append({
                    "mesh_triplet": [m1.identifier, m2.identifier, m3.identifier],
                    "refinement_ratios": {"r21": round(r21, 3), "r32": round(r32, 3)},
                    "order": round(p, 3),
                    "gci_21": round(gci21, 3),
                    "gci_32": round(gci32, 3),
                    "gci_ratio": round(gci_ratio, 3),
                    "richardson_extrapolated": round(richardson_ext, 6),
                    "intra_triplet": {
                        "asymptotic": asymptotic,
                        "monotonic": monotonic,
                        "rel_eps21": round(rel_eps21, 6),
                        "rel_eps32": round(rel_eps32, 6),
                        "sign_flip": sign_flip
                    },
                    "inter_triplet": {
                        "delta_order": round(delta_order, 3) if delta_order is not None else None,
                        "delta_gci": round(delta_gci, 3) if delta_gci is not None else None
                    }
                })

            except Exception as e:
                triplet_data.append({
                    "mesh_triplet": [m1.identifier, m2.identifier, m3.identifier],
                    "error": str(e)
                })

        return triplet_data