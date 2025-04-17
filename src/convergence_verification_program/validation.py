# src\convergence_verification_program\validation.py

from typing import List, Dict
from .mesh import MeshData
from .standards import StandardParameters
from .exceptions import InvalidRefinementSequenceError
from .numerics import calculate_refinement_ratio
from .config import STRICT_MODE


def validate_mesh_sequence(
    meshes: List[MeshData],
    parameters: StandardParameters,
    strict: bool = True,
    verbose: bool = False
) -> List[Dict]:
    """
    Validate mesh refinement ratios using per-mesh dimension.

    Parameters
    ----------
    meshes : List[MeshData]
        List of mesh objects.
    parameters : StandardParameters
        The refinement bounds specified by the verification standard.
    strict : bool, optional
        Whether to raise an exception if validation fails (default is True).
    verbose : bool, optional
        Whether to print technically descriptive failure messages (default is False).

    Returns
    -------
    List[Dict]
        List of validation results, including ratio and status.

    Raises
    ------
    InvalidRefinementSequenceError
        If strict mode is on and a refinement ratio fails validation.
    """
    # Override local strict flag if STRICT_MODE is globally enabled
    strict = strict or STRICT_MODE

    if len(meshes) < 3:
        msg = "Minimum of 3 meshes required for convergence analysis."
        if verbose:
            print(f"[Validation Error] {msg}")
        raise InvalidRefinementSequenceError(msg)

    report = []

    for i in range(len(meshes) - 1):
        m1 = meshes[i]
        m2 = meshes[i + 1]
        dim = m1.dim

        if dim not in {1, 2, 3}:
            msg = f"Mesh '{m1.identifier}' has invalid dimension: {dim}"
            if verbose:
                print(f"[Validation Error] {msg}")
            if strict:
                raise InvalidRefinementSequenceError(msg)

        if m1.node_count <= 0 or m2.node_count <= 0:
            msg = f"Non-positive node count in mesh pair: {m1.identifier}, {m2.identifier}"
            if verbose:
                print(f"[Validation Error] {msg}")
            if strict:
                raise InvalidRefinementSequenceError(msg)
            report.append({
                "index": i,
                "meshes": (m1.identifier, m2.identifier),
                "status": "invalid_node_count",
                "message": msg
            })
            continue

        ratio = calculate_refinement_ratio(m1.node_count, m2.node_count, dim)
        valid = parameters.min_refinement <= ratio <= parameters.max_refinement

        message = "OK" if valid else (
            f"Refinement ratio {ratio:.2f} outside allowed range "
            f"[{parameters.min_refinement}, {parameters.max_refinement}]"
        )

        if verbose:
            outcome = "✔ PASSED" if valid else "✖ FAILED"
            print(f"[Check {i}] {m1.identifier} ➝ {m2.identifier} | "
                  f"r = {ratio:.3f} | dim = {dim} | {outcome} — {message}")

        result = {
            "index": i,
            "meshes": (m1.identifier, m2.identifier),
            "refinement_ratio": ratio,
            "valid": valid,
            "message": message
        }

        if not valid and strict:
            raise InvalidRefinementSequenceError(result["message"], details=result)

        report.append(result)

    return report