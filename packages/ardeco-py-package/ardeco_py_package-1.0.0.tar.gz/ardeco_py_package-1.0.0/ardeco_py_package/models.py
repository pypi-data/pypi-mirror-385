import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Dataset:
    variable_code: str
    dimensions: Dict[str, Any]
    nuts_versions: List[int] = field(default_factory=list)
    dataset_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        base = {"variable_code": self.variable_code}
        base.update(self.dimensions)
        base["nuts_versions"] = self.nuts_versions
        if self.dataset_id:
            base["dataset_id"] = self.dataset_id
        return base
    

@dataclass
class Variable:
    """Represents a single ARDECO variable, including its metadata and allowed dimensions.

    Attributes:
        code (str): Unique variable identifier (e.g., 'SNPTN').
        description (str): Human-readable description of the variable.
        allowed_dimensions (List[str]): List of dimension keys available for filtering.
        nuts_level (Optional[str]): NUTS territorial level of the dataset.
        dimensions (Dict[str, List[str]]): Formatted dimensions grouped by category
            (e.g., {"age": ["Y_LT15", "Y15-64"], "sex": ["F", "M"]}).

    Notes:
        The raw GraphQL dimensions are stored internally in `_dimensions_raw`.
        Accessing `.dimensions` always returns a cleaned, human-readable version.
    """
    code: str
    description: str
    allowed_dimensions: List[str]
    nuts_level: Optional[str] = None
    _dimensions_raw: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    
    @property
    def dimensions(self) -> Dict[str, List[str]]:
        """Return formatted dimensions directly."""
        formatted = {}
        for dim in self._dimensions_raw or []:
            group = dim.get("dimensionGroupName")
            values = [v.get("dimensionValueName") for v in dim.get("dimensionValueList", [])]
            if group:
                formatted[group] = values
        return formatted
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "description": self.description,
            "allowed_dimensions": self.allowed_dimensions,
            "nuts_level": self.nuts_level,
            "dimensions": self.dimensions,
        }

    def __repr__(self) -> str:
        if not self.dimensions:
            dims_str = "None"
        else:
            dims_str = "\n    ".join(f"{k}: {v}" for k, v in self.dimensions.items())
        return (
            f"Variable(\n"
            f"  code='{self.code}',\n"
            f"  description='{self.description}',\n"
            f"  allowed_dimensions={self.allowed_dimensions},\n"
            f"  nuts_level={self.nuts_level},\n"
            f"  dimensions=\n    {dims_str}\n"
            f")"
        )


@dataclass
class Tercet:
    code: str
    name: str
    tercet_class_code: str
    tercet_class_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tercet_code": self.code,
            "tercet_name": self.name,
            "tercet_class_code": self.tercet_class_code,
            "tercet_class_name": self.tercet_class_name,
        }
        

@dataclass
class DataTable:
    data: List[Dict[str, Any]]
    columns: Optional[List[str]] = None

    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame(self.data, columns=self.columns)
