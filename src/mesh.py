from typing import Dict, Any
from pydantic import BaseModel, field_validator, Field

class MeshData(BaseModel):
    """
    Represents a single mesh used in a convergence study.

    Attributes
    ----------
    identifier : str
        A unique identifier for the mesh.
    node_count : int
        The number of nodes in the mesh (must be positive).
    parameters : Dict[str, float]
        A dictionary mapping parameter names to their computed values.
    """
    identifier: str = Field(..., description="Unique mesh identifier")
    node_count: int = Field(..., gt=0, description="Positive number of nodes in the mesh")
    parameters: Dict[str, float] = Field(..., description="Parameter results for this mesh")

    @field_validator('node_count')
    @classmethod
    def validate_node_count(cls, value: int) -> int:
        """
        Ensure node count is strictly positive.

        Parameters
        ----------
        value : int
            Node count to validate.

        Returns
        -------
        int
            The validated node count.

        Raises
        ------
        ValueError
            If node count is not greater than zero.
        """
        if value <= 0:
            raise ValueError("Node count must be positive")
        return value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeshData":
        """
        Construct MeshData from an untyped dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Raw input dictionary expected to contain 'id', 'resolution', and 'parameters'.

        Returns
        -------
        MeshData
            Parsed and validated MeshData instance.

        Raises
        ------
        KeyError
            If required keys are missing.
        ValueError
            If values are invalid or incomplete.
        """
        if not all(k in data for k in ('id', 'resolution', 'parameters')):
            raise KeyError("Missing one or more required keys: 'id', 'resolution', 'parameters'")

        if not isinstance(data['parameters'], dict):
            raise ValueError("'parameters' must be a dictionary of floats")

        return cls(
            identifier=data['id'],
            node_count=data['resolution'],
            parameters=data['parameters']
        )