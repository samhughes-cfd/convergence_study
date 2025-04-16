from typing import List, Dict
from .mesh import MeshData
from .standards import StandardParameters
from .exceptions import InvalidRefinementSequenceError

def validate_mesh_sequence(
    meshes: List[MeshData],
    parameters: StandardParameters,
    dim: int = 3,
    strict: bool = True
) -> List[Dict]:
    """
    Validate mesh refinement ratios and optionally raise on failure.

    Parameters
    ----------
    meshes : List[MeshData]
        Sequence of mesh objects to validate.
    parameters : StandardParameters
        Refinement bounds from selected standard.
    dim : int, optional
        Spatial dimension for ratio scaling (default is 3).
    strict : bool, optional
        Whether to raise an exception on invalid refinement (default is True).

    Returns
    -------
    List[Dict]
        Detailed results for each mesh pair with validation status and ratio.

    Raises
    ------
    InvalidRefinementSequenceError
        If strict mode is on and a refinement check fails.
    """
    if len(meshes) < 3:
        raise InvalidRefinementSequenceError("Minimum 3 meshes required for convergence analysis.")

    report = []

    for i in range(len(meshes) - 1):
        m1 = meshes[i]
        m2 = meshes[i + 1]
        coarse = m1.node_count
        fine = m2.node_count

        if coarse <= 0 or fine <= 0:
            msg = f"Non-positive node count in mesh pair: {m1.identifier}, {m2.identifier}"
            if strict:
                raise InvalidRefinementSequenceError(msg)
            report.append({
                "index": i,
                "meshes": (m1.identifier, m2.identifier),
                "status": "invalid_node_count",
                "message": msg
            })
            continue

        ratio = (fine / coarse) ** (1 / dim)
        valid = parameters.min_refinement <= ratio <= parameters.max_refinement

        result = {
            "index": i,
            "meshes": (m1.identifier, m2.identifier),
            "refinement_ratio": ratio,
            "valid": valid,
            "message": "OK" if valid else (
                f"Refinement ratio {ratio:.2f} outside allowed range "
                f"[{parameters.min_refinement}, {parameters.max_refinement}]"
            )
        }

        if not valid and strict:
            raise InvalidRefinementSequenceError(result["message"], details=result)

        report.append(result)

    return report