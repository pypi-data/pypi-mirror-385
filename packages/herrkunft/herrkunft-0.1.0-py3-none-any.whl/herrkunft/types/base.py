"""
Base classes and protocols for type wrappers with provenance tracking.

This module provides the foundation for creating type wrappers that transparently
add provenance tracking to Python's native types while preserving their original
behavior.
"""

from __future__ import annotations

from abc import ABC
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from herrkunft.core.provenance import Provenance

T = TypeVar("T")


@runtime_checkable
class HasProvenance(Protocol):
    """
    Protocol for objects that have provenance tracking.

    Any object implementing this protocol must provide a provenance property
    that returns a Provenance instance. This allows type checking and
    isinstance checks without requiring inheritance.

    Examples:
        >>> def process_config(value: HasProvenance):
        ...     print(value.provenance.current)
        >>>
        >>> isinstance(my_value, HasProvenance)  # True if has provenance
    """

    @property
    def provenance(self) -> Provenance:
        """Get the provenance history."""
        ...

    @provenance.setter
    def provenance(self, value: Provenance) -> None:
        """Set the provenance history."""
        ...


class ProvenanceMixin:
    """
    Mixin class providing provenance attribute management.

    This mixin provides common provenance-related functionality that can be
    added to any class. It manages the _provenance attribute and provides
    getter/setter properties.

    This is designed to be mixed into wrapper classes created dynamically
    or through inheritance.

    Attributes:
        _provenance: Internal storage for provenance history
        value: The original wrapped value (set by subclasses)
    """

    _provenance: Provenance
    value: Any

    def _init_provenance(self, provenance: Any = None) -> None:
        """
        Initialize provenance attribute.

        This method should be called by subclass __init__ methods to set up
        the provenance tracking.

        Args:
            provenance: Initial provenance data (Provenance, dict, list, or None)

        Examples:
            >>> class MyWrapper(str, ProvenanceMixin):
            ...     def __init__(self, value, provenance=None):
            ...         self._init_provenance(provenance)
            ...         self.value = value
        """
        if isinstance(provenance, Provenance):
            self._provenance = provenance
        elif provenance is None:
            self._provenance = Provenance(None)
        else:
            self._provenance = Provenance(provenance)

    @property
    def provenance(self) -> Provenance:
        """
        Get provenance history.

        Returns:
            The provenance history for this value

        Examples:
            >>> wrapped_value.provenance.current.yaml_file
            '/path/to/config.yaml'
        """
        return self._provenance

    @provenance.setter
    def provenance(self, value: Provenance) -> None:
        """
        Set provenance history.

        Args:
            value: New provenance history (must be a Provenance instance)

        Raises:
            TypeError: If value is not a Provenance instance

        Examples:
            >>> new_prov = Provenance({"category": "runtime"})
            >>> wrapped_value.provenance = new_prov
        """
        if not isinstance(value, Provenance):
            raise TypeError(
                f"Provenance must be a Provenance instance, got {type(value)}"
            )
        self._provenance = value


class ProvenanceWrapper(Generic[T], ABC):
    """
    Abstract base class for provenance wrappers.

    This class defines the interface for all provenance wrappers. Subclasses
    should override __new__ to properly instantiate the wrapped type.

    Type Parameter:
        T: The type being wrapped

    Note:
        This class is primarily for documentation and type hinting. In practice,
        the factory pattern is used to create wrapper classes dynamically.
    """

    _provenance: Provenance
    value: T

    def __init__(self, value: T, provenance: Provenance | dict | list | None = None):
        """
        Initialize wrapper with value and provenance.

        Args:
            value: The actual value to wrap
            provenance: Provenance information

        Examples:
            >>> wrapper = ProvenanceWrapper("my_value", {"category": "defaults"})
        """
        self.value = value
        self._provenance = self._init_provenance_static(provenance)

    @staticmethod
    def _init_provenance_static(prov: Any) -> Provenance:
        """
        Initialize provenance from various input types.

        Args:
            prov: Provenance data (Provenance, dict, list, or None)

        Returns:
            Provenance instance

        Examples:
            >>> prov = ProvenanceWrapper._init_provenance_static({"category": "defaults"})
            >>> isinstance(prov, Provenance)
            True
        """
        if isinstance(prov, Provenance):
            return prov
        if prov is None:
            return Provenance(None)
        return Provenance(prov)

    @property
    def provenance(self) -> Provenance:
        """
        Get provenance history.

        Returns:
            The provenance history for this value
        """
        return self._provenance

    @provenance.setter
    def provenance(self, value: Provenance) -> None:
        """
        Set provenance history.

        Args:
            value: New provenance history

        Raises:
            TypeError: If value is not a Provenance instance
        """
        if not isinstance(value, Provenance):
            raise TypeError("Provenance must be a Provenance instance")
        self._provenance = value
