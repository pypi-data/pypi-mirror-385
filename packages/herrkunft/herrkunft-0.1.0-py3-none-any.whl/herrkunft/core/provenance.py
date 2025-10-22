"""
Core provenance classes for tracking value history.

This module provides the Provenance and ProvenanceStep classes that form
the foundation of the provenance tracking system.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ProvenanceStep(BaseModel):
    """
    Single step in provenance history.

    Each ProvenanceStep represents one point in the history of a value,
    tracking its origin, modifications, and metadata.

    Attributes:
        category: Configuration category (e.g., 'defaults', 'components', 'setups')
        subcategory: Subcategory identifier (e.g., specific component name)
        yaml_file: Source YAML file path
        line: Line number in file (1-indexed)
        col: Column number in file (1-indexed)
        modified_by: Function that modified this value
        extended_by: Function that extended the provenance history
        from_choose: Choose block history for conditional configuration
        timestamp: ISO timestamp of modification
    """

    category: Optional[str] = Field(None, description="Configuration category")
    subcategory: Optional[str] = Field(None, description="Subcategory identifier")
    yaml_file: Optional[str] = Field(None, description="Source YAML file path")
    line: Optional[int] = Field(None, ge=1, description="Line number in file")
    col: Optional[int] = Field(None, ge=1, description="Column number in file")
    modified_by: Optional[str] = Field(None, description="Function that modified value")
    extended_by: Optional[str] = Field(
        None, description="Function that extended history"
    )
    from_choose: List[Dict[str, Any]] = Field(
        default_factory=list, description="Choose block history"
    )
    timestamp: Optional[str] = Field(None, description="ISO timestamp of modification")

    model_config = {
        "frozen": False,  # Allow updates
        "extra": "allow",  # Allow additional fields
    }

    def dict(self, exclude_none: bool = True, **kwargs) -> dict[str, Any]:
        """
        Convert to dictionary representation.

        Args:
            exclude_none: Exclude None values from output
            **kwargs: Additional arguments

        Returns:
            Dictionary representation
        """
        return self.model_dump(exclude_none=exclude_none, **kwargs)

    def update(self, data: dict[str, Any]) -> None:
        """
        Update step with new data (for compatibility).

        Args:
            data: Dictionary of fields to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Provenance(list):
    """
    A list subclass storing the complete modification history of a value.

    Each element represents one step in the value's history, with the last
    element representing the current value's provenance.

    The Provenance class extends list to provide specialized methods for
    tracking and managing value history in a configuration system.

    Examples:
        >>> prov = Provenance({"category": "defaults", "yaml_file": "config.yaml"})
        >>> prov.append_modified_by("my_function")
        >>> print(len(prov))  # 2
        >>> print(prov.current.modified_by)  # "my_function"
    """

    def __init__(
        self,
        data: Optional[
            Union[
                ProvenanceStep,
                list[ProvenanceStep],
                dict[str, Any],
                list[dict[str, Any]],
            ]
        ] = None,
    ):
        """
        Initialize provenance from step(s).

        Args:
            data: Provenance data as a single step, list of steps, dict, or list of dicts.
                  Can also be None to create an empty provenance.

        Examples:
            >>> # From a single dict
            >>> prov = Provenance({"category": "defaults"})
            >>> # From a list of dicts
            >>> prov = Provenance([{"category": "defaults"}, {"category": "runtime"}])
            >>> # From ProvenanceStep objects
            >>> step = ProvenanceStep(category="defaults")
            >>> prov = Provenance(step)
        """
        if data is None:
            super().__init__()
        elif isinstance(data, (ProvenanceStep, dict)):
            super().__init__([self._ensure_step(data)])
        elif isinstance(data, list):
            super().__init__([self._ensure_step(item) for item in data])
        else:
            super().__init__()

    @staticmethod
    def _ensure_step(data: Union[ProvenanceStep, dict[str, Any]]) -> ProvenanceStep:
        """
        Convert dict to ProvenanceStep if needed.

        Args:
            data: Either a ProvenanceStep or dict representation

        Returns:
            ProvenanceStep instance
        """
        if isinstance(data, ProvenanceStep):
            return data
        return ProvenanceStep(**data)

    def append_modified_by(self, func: str) -> None:
        """
        Duplicate the last provenance step and mark it as modified by func.

        This method is used to track when a value is modified by a function,
        preserving the complete history while marking the modification point.

        Args:
            func: Name/identifier of the modifying function

        Examples:
            >>> prov = Provenance({"category": "defaults"})
            >>> prov.append_modified_by("my_function")
            >>> print(prov[-1].modified_by)  # "my_function"
        """
        if not self:
            # Create a minimal step if provenance is empty
            step = ProvenanceStep(modified_by=str(func))
            self.append(step)
            return

        new_step = self[-1].model_copy(deep=True)
        new_step.modified_by = str(func)
        self.append(new_step)

    def extend_and_mark(self, other: "Provenance", func: str) -> None:
        """
        Extend this provenance with another, marking the extension source.

        This method is used when a value's provenance history needs to include
        another value's history (e.g., when overriding a configuration value).

        Args:
            other: Provenance history to append
            func: Function responsible for the extension

        Examples:
            >>> old_prov = Provenance({"category": "defaults"})
            >>> new_prov = Provenance({"category": "runtime"})
            >>> old_prov.extend_and_mark(new_prov, "dict.__setitem__")
            >>> print(old_prov[-1].extended_by)  # "dict.__setitem__"
        """
        if other is self:
            self.append_modified_by(func)
            return

        for step in other:
            new_step = step.model_copy(deep=True)
            new_step.extended_by = str(func)
            self.append(new_step)

    @property
    def current(self) -> Optional[ProvenanceStep]:
        """
        Get the current (last) provenance step.

        Returns:
            The most recent provenance step, or None if empty

        Examples:
            >>> prov = Provenance({"category": "defaults", "line": 42})
            >>> print(prov.current.line)  # 42
        """
        return self[-1] if self else None

    def to_dict(self) -> list[dict[str, Any]]:
        """
        Convert to list of dictionaries.

        Returns:
            List of provenance steps as dictionaries, excluding None values

        Examples:
            >>> prov = Provenance({"category": "defaults", "line": 42})
            >>> dicts = prov.to_dict()
            >>> print(dicts[0]["category"])  # "defaults"
        """
        return [step.dict(exclude_none=True) for step in self]

    def to_json(self) -> str:
        """
        Convert to JSON string.

        Returns:
            JSON representation of the provenance history
        """
        import json

        return json.dumps(self.to_dict(), indent=2)

    def copy(self, deep: bool = True) -> "Provenance":
        """
        Create a copy of this provenance.

        Args:
            deep: Whether to deep copy the steps

        Returns:
            New Provenance instance
        """
        if deep:
            return Provenance([step.model_copy(deep=True) for step in self])
        else:
            return Provenance(list(self))

    def __repr__(self) -> str:
        """String representation showing number of steps and current step."""
        if not self:
            return "Provenance([])"

        current = self.current
        summary = []
        if current:
            if current.category:
                summary.append(f"category={current.category}")
            if current.yaml_file:
                summary.append(f"file={current.yaml_file}")
            if current.line:
                summary.append(f"line={current.line}")

        summary_str = ", ".join(summary) if summary else "empty"
        return f"Provenance({len(self)} steps: {summary_str})"
