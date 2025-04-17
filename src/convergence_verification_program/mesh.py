# src\convergence_verification_program\mesh.py

from typing import Dict, Any, Optional
from pydantic import BaseModel, field_validator, Field
from json import dumps


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
    dim : int, optional
        Dimensionality of the mesh (must be 1, 2, or 3). Defaults to 3.
    units : Dict[str, str], optional
        Units associated with each parameter.
    """
    identifier: str = Field(..., description="Unique mesh identifier")
    node_count: int = Field(..., gt=0, description="Positive number of nodes in the mesh")
    parameters: Dict[str, float] = Field(..., description="Parameter results for this mesh")
    dim: Optional[int] = Field(3, description="Spatial dimension of the mesh (1, 2, or 3)")
    units: Optional[Dict[str, str]] = Field(None, description="Optional units for parameter annotations")

    @field_validator('node_count')
    @classmethod
    def validate_node_count(cls, value: int) -> int:
        """
        Ensure node count is strictly positive.

        Parameters
        ----------
        value : int
            The input node count.

        Returns
        -------
        int
            Validated node count.

        Raises
        ------
        ValueError
            If the node count is not greater than 0.
        """
        if value <= 0:
            raise ValueError("Node count must be positive")
        return value

    @field_validator('dim')
    @classmethod
    def validate_dim(cls, value: Optional[int]) -> int:
        """
        Validate the spatial dimension value.

        Parameters
        ----------
        value : int
            The input dimension.

        Returns
        -------
        int
            Validated dimension value.

        Raises
        ------
        ValueError
            If dimension is not in {1, 2, 3}.
        """
        if value not in {1, 2, 3}:
            raise ValueError("Mesh dimension must be 1, 2, or 3.")
        return value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeshData":
        """
        Construct a MeshData object from a raw dictionary.

        Parameters
        ----------
        data : dict
            Input dictionary with keys 'id', 'resolution', and 'parameters'.

        Returns
        -------
        MeshData
            Parsed mesh object.

        Raises
        ------
        KeyError
            If required keys are missing.
        ValueError
            If parameters are not valid.
        """
        if not all(k in data for k in ('id', 'resolution', 'parameters')):
            raise KeyError("Missing one or more required keys: 'id', 'resolution', 'parameters'")

        if not isinstance(data['parameters'], dict):
            raise ValueError("'parameters' must be a dictionary of floats")

        return cls(
            identifier=data['id'],
            node_count=data['resolution'],
            parameters=data['parameters'],
            dim=data.get('dim', 3),
            units=data.get('units')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the mesh data to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the mesh.
        """
        return {
            "identifier": self.identifier,
            "node_count": self.node_count,
            "parameters": self.parameters,
            "dim": self.dim,
            "units": self.units
        }

    def to_json(self, indent: int = 4) -> str:
        """
        Serialize the mesh data to JSON format.

        Parameters
        ----------
        indent : int
            Indentation level for formatting (default is 4).

        Returns
        -------
        str
            JSON string.
        """
        return dumps(self.to_dict(), indent=indent)