"""
Mapping types with provenance tracking (dict and list).

This module provides DictWithProvenance and ListWithProvenance classes that
extend Python's built-in dict and list types to track provenance for all
nested values, with automatic conflict resolution via HierarchyManager.
"""

from __future__ import annotations

import copy
from typing import Any, Optional, Union

from loguru import logger

from herrkunft.core.hierarchy import HierarchyManager
from herrkunft.core.provenance import Provenance, ProvenanceStep


class DictWithProvenance(dict):
    """
    A dictionary subclass with integrated provenance tracking.

    DictWithProvenance automatically tracks the provenance (source, history)
    of every value in the dictionary. It recursively wraps nested dicts and
    lists, and uses HierarchyManager to resolve conflicts when values are
    overridden.

    Key features:
    - Automatic recursive provenance assignment to all nested values
    - Conflict resolution based on category hierarchy
    - __setitem__ integration with HierarchyManager
    - Methods to set and get provenance for the entire structure
    - super_setitem() to bypass hierarchy checking when needed

    Attributes:
        _hierarchy: HierarchyManager instance for conflict resolution
        _custom_setitem: Flag to control whether custom __setitem__ is active

    Examples:
        >>> # Create dict with provenance
        >>> data = {"key": "value"}
        >>> prov = {"key": {"category": "defaults", "line": 10}}
        >>> config = DictWithProvenance(data, prov)
        >>>
        >>> # Access provenance
        >>> config["key"].provenance.current.category  # 'defaults'
        >>>
        >>> # Set new value (higher category wins)
        >>> from herrkunft.types.factory import TypeWrapperFactory
        >>> new_val = TypeWrapperFactory.wrap("new", {"category": "runtime"})
        >>> config["key"] = new_val  # Overwrites because runtime > defaults
        >>>
        >>> # Get provenance tree
        >>> prov_tree = config.get_provenance()
        >>> print(prov_tree["key"]["category"])  # 'runtime'
    """

    def __init__(
        self,
        data: dict[str, Any],
        provenance: Union[dict[str, Any], None] = None,
        hierarchy_manager: Optional[HierarchyManager] = None,
    ):
        """
        Initialize dictionary with provenance tracking.

        Args:
            data: Dictionary data to wrap
            provenance: Provenance information matching the structure of data.
                        Can be a dict with same keys as data, where each value
                        is provenance info for the corresponding data value.
            hierarchy_manager: Custom HierarchyManager. If None, creates default.

        Examples:
            >>> data = {"host": "localhost", "port": 5432}
            >>> prov = {
            ...     "host": {"category": "defaults", "line": 5},
            ...     "port": {"category": "defaults", "line": 6}
            ... }
            >>> config = DictWithProvenance(data, prov)
        """
        super().__init__(data)
        self._hierarchy = hierarchy_manager or HierarchyManager()
        self._custom_setitem = False
        self._put_provenance(provenance or {})
        self._custom_setitem = True

    def _put_provenance(self, provenance: dict[str, Any]) -> None:
        """
        Recursively assign provenance to all values in the dictionary.

        This method wraps each value with its corresponding provenance,
        creating DictWithProvenance for nested dicts and ListWithProvenance
        for nested lists.

        Args:
            provenance: Dictionary with same structure as self, containing
                       provenance information for each key.

        Note:
            This is called during __init__ with _custom_setitem=False to avoid
            triggering hierarchy checks during initial setup.
        """
        # Import here to avoid circular dependency
        from herrkunft.types.factory import TypeWrapperFactory

        for key, val in self.items():
            prov_for_key = provenance.get(key, None)

            if isinstance(val, dict):
                # Nested dict - create DictWithProvenance recursively
                self[key] = DictWithProvenance(val, prov_for_key or {}, self._hierarchy)
            elif isinstance(val, list):
                # Nested list - create ListWithProvenance recursively
                self[key] = ListWithProvenance(val, prov_for_key or [], self._hierarchy)
            elif hasattr(val, "provenance"):
                # Value already has provenance - extend it if we have new info
                if prov_for_key:
                    if isinstance(prov_for_key, list):
                        self[key].provenance.extend(prov_for_key)
                    else:
                        self[key].provenance.append(
                            ProvenanceStep(**prov_for_key)
                            if isinstance(prov_for_key, dict)
                            else prov_for_key
                        )
            else:
                # Wrap primitive value with provenance
                self[key] = TypeWrapperFactory.wrap(val, prov_for_key)

    def set_provenance(
        self,
        provenance: Union[Dict, List, ProvenanceStep],
        update_method: str = "extend",
    ) -> None:
        """
        Set the same provenance for all values in the dictionary.

        Unlike _put_provenance which assigns different provenance to each key,
        this method assigns the SAME provenance to ALL values recursively.

        Args:
            provenance: Provenance to assign to all values
            update_method: How to update existing provenance:
                - "extend": Append new provenance to existing history
                - "update": Update the last provenance step with new fields
                - "replace": Replace all provenance with new provenance

        Examples:
            >>> config = DictWithProvenance({"a": 1, "b": 2}, {})
            >>> config.set_provenance({"category": "runtime", "modified_by": "user"})
            >>> config["a"].provenance.current.category  # 'runtime'
            >>> config["b"].provenance.current.category  # 'runtime'
        """
        # Import here to avoid circular dependency
        from herrkunft.types.factory import TypeWrapperFactory

        # Normalize provenance to list of ProvenanceStep
        if not isinstance(provenance, list):
            provenance = [provenance]

        # Convert to ProvenanceStep objects
        prov_steps = []
        for p in provenance:
            if isinstance(p, ProvenanceStep):
                prov_steps.append(p)
            elif isinstance(p, dict):
                prov_steps.append(ProvenanceStep(**p))
            else:
                prov_steps.append(p)

        for key, val in self.items():
            if isinstance(val, dict):
                # Nested dict - convert and recurse
                if not isinstance(val, DictWithProvenance):
                    self[key] = DictWithProvenance(val, {}, self._hierarchy)
                self[key].set_provenance(prov_steps, update_method=update_method)
            elif isinstance(val, list):
                # Nested list - convert and recurse
                if not isinstance(val, ListWithProvenance):
                    self[key] = ListWithProvenance(val, [], self._hierarchy)
                self[key].set_provenance(prov_steps, update_method=update_method)
            elif hasattr(val, "provenance"):
                # Value with provenance - update it
                if update_method == "extend":
                    for step in prov_steps:
                        self[key].provenance.append(step)
                elif update_method == "update":
                    if self[key].provenance and len(self[key].provenance) > 0:
                        # Update last step
                        last_step = self[key].provenance[-1]
                        for prov_step in prov_steps:
                            if isinstance(prov_step, ProvenanceStep):
                                last_step.update(prov_step.dict())
                    else:
                        # No existing provenance, just set it
                        for step in prov_steps:
                            self[key].provenance.append(step)
                elif update_method == "replace":
                    self[key].provenance = Provenance(prov_steps)
                else:
                    raise ValueError(
                        f"Unknown update_method '{update_method}'. "
                        f"Use 'extend', 'update', or 'replace'."
                    )
            else:
                # No provenance - wrap with it
                self[key] = TypeWrapperFactory.wrap(val, prov_steps)

    def get_provenance(self, index: int = -1) -> dict[str, Any]:
        """
        Extract provenance tree matching the structure of this dictionary.

        Returns a dictionary with the same keys as self, but with provenance
        information as values instead of the actual data values.

        Args:
            index: Which step in provenance history to return (-1 for current)

        Returns:
            Dictionary with same structure as self, but values are provenance info

        Examples:
            >>> config = DictWithProvenance(
            ...     {"db": {"host": "localhost"}},
            ...     {"db": {"host": {"category": "defaults", "line": 5}}}
            ... )
            >>> prov = config.get_provenance()
            >>> prov["db"]["host"]["category"]  # 'defaults'
        """
        provenance_dict = {}

        for key, val in self.items():
            if isinstance(val, (DictWithProvenance, ListWithProvenance)):
                # Nested mapping - recurse
                provenance_dict[key] = val.get_provenance(index=index)
            elif hasattr(val, "provenance"):
                # Value with provenance - extract the step
                if val.provenance and len(val.provenance) > 0:
                    step = val.provenance[index]
                    provenance_dict[key] = step.dict() if step else None
                else:
                    provenance_dict[key] = None
            else:
                # No provenance tracking on this value
                provenance_dict[key] = None

        return provenance_dict

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set item with automatic provenance tracking and hierarchy checking.

        When setting a value:
        1. If key doesn't exist, just set it
        2. If key exists and has provenance, check hierarchy:
           - Higher category overrides lower category
           - Lower category is rejected
           - Same category triggers conflict (unless choose block)
        3. Extend provenance history to track the change

        Args:
            key: Dictionary key
            value: New value (can have provenance or not)

        Raises:
            CategoryConflictError: If trying to override at same category level
                                  without choose block or allow_same_level_override

        Examples:
            >>> from herrkunft.types.factory import TypeWrapperFactory
            >>> config = DictWithProvenance({}, {})
            >>>
            >>> # Set initial value
            >>> val1 = TypeWrapperFactory.wrap("v1", {"category": "defaults"})
            >>> config["key"] = val1
            >>>
            >>> # Override with higher category
            >>> val2 = TypeWrapperFactory.wrap("v2", {"category": "runtime"})
            >>> config["key"] = val2  # Succeeds
            >>>
            >>> # Try to override with same category
            >>> val3 = TypeWrapperFactory.wrap("v3", {"category": "runtime"})
            >>> config["key"] = val3  # Raises CategoryConflictError
        """
        # If custom setitem is disabled (during init), just set normally
        if not self._custom_setitem:
            super().__setitem__(key, value)
            return

        # Get old value if it exists
        old_value = self.get(key, None)

        # If key doesn't exist, just set it
        if key not in self:
            super().__setitem__(key, value)
            return

        # If old value is dict or list, just replace (no hierarchy check for containers)
        if isinstance(old_value, (dict, list)):
            super().__setitem__(key, value)
            return

        # If old value has no provenance, just replace
        if not hasattr(old_value, "provenance"):
            super().__setitem__(key, value)
            return

        # Old value has provenance - need to check hierarchy
        old_provenance = old_value.provenance

        # Get old category
        if old_provenance and len(old_provenance) > 0 and old_provenance.current:
            old_step = old_provenance.current
        else:
            # No provenance info - treat as backend category
            old_step = ProvenanceStep(category=None)  # None = backend

        # Initialize new provenance with copy of old
        new_provenance = old_provenance.copy(deep=True)

        # If new value has provenance, check hierarchy
        if hasattr(value, "provenance") and value.provenance:
            new_step = value.provenance.current or ProvenanceStep(category=None)
        else:
            # New value has no provenance - treat as backend modification
            new_step = ProvenanceStep(category=None)  # Backend category

        # Check if we should override using hierarchy manager
        should_override, error = self._hierarchy.should_override(
            old_step, new_step, key
        )

        if error:
            # Hierarchy manager says we should raise an error
            raise error

        if should_override:
            # Higher category wins - use new value
            final_value = copy.deepcopy(value)
            # Extend provenance with the new value's provenance
            if hasattr(value, "provenance") and value.provenance:
                new_provenance.extend_and_mark(value.provenance, "dict.__setitem__")
            else:
                # No provenance on new value - just mark the modification
                new_provenance.append_modified_by("dict.__setitem__")

            if hasattr(final_value, "provenance"):
                final_value.provenance = new_provenance
            else:
                # Wrap with factory to add provenance
                from herrkunft.types.factory import TypeWrapperFactory

                final_value = TypeWrapperFactory.wrap(value, new_provenance)
        else:
            # Lower category loses - keep old value but mark the attempt
            logger.debug(
                f"Keeping old value for key '{key}' because new category "
                f"'{new_step.category}' <= old category '{old_step.category}'"
            )
            final_value = copy.deepcopy(old_value)
            # Add note to provenance that override was rejected
            new_provenance.append_modified_by("dict.__setitem__->reverted_by_hierarchy")
            if hasattr(final_value, "provenance"):
                final_value.provenance = new_provenance

        super().__setitem__(key, final_value)

    def super_setitem(self, key: str, value: Any) -> None:
        """
        Set item bypassing all provenance tracking and hierarchy checks.

        This method calls dict.__setitem__ directly, skipping all custom logic.
        Use this when you need to force-set a value regardless of hierarchy rules.

        Args:
            key: Dictionary key
            value: Value to set

        Examples:
            >>> config = DictWithProvenance({}, {})
            >>> # Force set a value even if hierarchy would reject it
            >>> config.super_setitem("key", "forced_value")
        """
        super().__setitem__(key, value)

    def update(self, other: dict[str, Any], **kwargs) -> None:
        """
        Update dictionary while preserving provenance.

        This method extends dict.update() to properly handle provenance
        tracking for all updated values, including hierarchy checking.

        Args:
            other: Dictionary to update from
            **kwargs: Additional key-value pairs to update

        Raises:
            CategoryConflictError: If trying to override at same category level

        Examples:
            >>> config = DictWithProvenance({"a": 1}, {"a": {"category": "defaults"}})
            >>> config.update({"b": 2})
            >>> config["b"]  # 2
        """
        # Build a combined dict from other and kwargs
        update_dict = {}
        if other:
            update_dict.update(other)
        update_dict.update(kwargs)

        # Use __setitem__ for each key to trigger hierarchy checks
        for key, val in update_dict.items():
            self[key] = val


class ListWithProvenance(list):
    """
    A list subclass with integrated provenance tracking.

    ListWithProvenance automatically tracks the provenance of every element
    in the list. It recursively wraps nested dicts and lists.

    Key features:
    - Automatic recursive provenance assignment to all elements
    - __setitem__ preserves and extends provenance
    - Methods to set and get provenance for the entire structure

    Attributes:
        _hierarchy: HierarchyManager instance (for consistency with DictWithProvenance)
        _custom_setitem: Flag to control whether custom __setitem__ is active

    Examples:
        >>> # Create list with provenance
        >>> data = ["value1", "value2"]
        >>> prov = [
        ...     {"category": "defaults", "line": 5},
        ...     {"category": "defaults", "line": 6}
        ... ]
        >>> config = ListWithProvenance(data, prov)
        >>>
        >>> # Access provenance
        >>> config[0].provenance.current.line  # 5
        >>>
        >>> # Get provenance tree
        >>> prov_tree = config.get_provenance()
        >>> print(prov_tree[0]["line"])  # 5
    """

    def __init__(
        self,
        data: list[Any],
        provenance: Union[list[Any], None] = None,
        hierarchy_manager: Optional[HierarchyManager] = None,
    ):
        """
        Initialize list with provenance tracking.

        Args:
            data: List data to wrap
            provenance: List of provenance information, one entry per element.
                       Can be a list of dicts/ProvenanceSteps, or empty list.
            hierarchy_manager: Custom HierarchyManager. If None, creates default.

        Examples:
            >>> data = ["host1", "host2"]
            >>> prov = [
            ...     {"category": "defaults", "line": 10},
            ...     {"category": "defaults", "line": 11}
            ... ]
            >>> config = ListWithProvenance(data, prov)
        """
        super().__init__(data)
        self._hierarchy = hierarchy_manager or HierarchyManager()
        self._custom_setitem = False
        self._put_provenance(provenance or [])
        self._custom_setitem = True

    def _put_provenance(self, provenance: list[Any]) -> None:
        """
        Recursively assign provenance to all elements in the list.

        This method wraps each element with its corresponding provenance,
        creating DictWithProvenance for nested dicts and ListWithProvenance
        for nested lists.

        Args:
            provenance: List with same length as self, containing provenance
                       information for each element. If empty or shorter,
                       missing entries are treated as None.

        Note:
            This is called during __init__ with _custom_setitem=False to avoid
            triggering hierarchy checks during initial setup.
        """
        # Import here to avoid circular dependency
        from herrkunft.types.factory import TypeWrapperFactory

        # Ensure provenance list is same length as data list
        if not provenance:
            provenance = [None] * len(self)
        elif len(provenance) < len(self):
            # Pad with None for missing entries
            provenance = list(provenance) + [None] * (len(self) - len(provenance))

        for idx, elem in enumerate(self):
            prov_for_elem = provenance[idx] if idx < len(provenance) else None

            if isinstance(elem, dict):
                # Nested dict - create DictWithProvenance recursively
                self[idx] = DictWithProvenance(
                    elem, prov_for_elem or {}, self._hierarchy
                )
            elif isinstance(elem, list):
                # Nested list - create ListWithProvenance recursively
                self[idx] = ListWithProvenance(
                    elem, prov_for_elem or [], self._hierarchy
                )
            elif hasattr(elem, "provenance"):
                # Value already has provenance - extend it if we have new info
                if prov_for_elem:
                    if isinstance(prov_for_elem, list):
                        self[idx].provenance.extend(prov_for_elem)
                    else:
                        self[idx].provenance.append(
                            ProvenanceStep(**prov_for_elem)
                            if isinstance(prov_for_elem, dict)
                            else prov_for_elem
                        )
            else:
                # Wrap primitive value with provenance
                self[idx] = TypeWrapperFactory.wrap(elem, prov_for_elem)

    def set_provenance(
        self,
        provenance: Union[Dict, List, ProvenanceStep],
        update_method: str = "extend",
    ) -> None:
        """
        Set the same provenance for all elements in the list.

        Unlike _put_provenance which assigns different provenance to each element,
        this method assigns the SAME provenance to ALL elements recursively.

        Args:
            provenance: Provenance to assign to all elements
            update_method: How to update existing provenance:
                - "extend": Append new provenance to existing history
                - "update": Update the last provenance step with new fields
                - "replace": Replace all provenance with new provenance

        Examples:
            >>> config = ListWithProvenance([1, 2, 3], [])
            >>> config.set_provenance({"category": "runtime"})
            >>> config[0].provenance.current.category  # 'runtime'
            >>> config[1].provenance.current.category  # 'runtime'
        """
        # Import here to avoid circular dependency
        from herrkunft.types.factory import TypeWrapperFactory

        # Normalize provenance to list of ProvenanceStep
        if not isinstance(provenance, list):
            provenance = [provenance]

        # Convert to ProvenanceStep objects
        prov_steps = []
        for p in provenance:
            if isinstance(p, ProvenanceStep):
                prov_steps.append(p)
            elif isinstance(p, dict):
                prov_steps.append(ProvenanceStep(**p))
            else:
                prov_steps.append(p)

        for idx, elem in enumerate(self):
            if isinstance(elem, dict):
                # Nested dict - convert and recurse
                if not isinstance(elem, DictWithProvenance):
                    self[idx] = DictWithProvenance(elem, {}, self._hierarchy)
                self[idx].set_provenance(prov_steps, update_method=update_method)
            elif isinstance(elem, list):
                # Nested list - convert and recurse
                if not isinstance(elem, ListWithProvenance):
                    self[idx] = ListWithProvenance(elem, [], self._hierarchy)
                self[idx].set_provenance(prov_steps, update_method=update_method)
            elif hasattr(elem, "provenance"):
                # Value with provenance - update it
                if update_method == "extend":
                    for step in prov_steps:
                        self[idx].provenance.append(step)
                elif update_method == "update":
                    if self[idx].provenance and len(self[idx].provenance) > 0:
                        # Update last step
                        last_step = self[idx].provenance[-1]
                        for prov_step in prov_steps:
                            if isinstance(prov_step, ProvenanceStep):
                                last_step.update(prov_step.dict())
                    else:
                        # No existing provenance, just set it
                        for step in prov_steps:
                            self[idx].provenance.append(step)
                elif update_method == "replace":
                    self[idx].provenance = Provenance(prov_steps)
                else:
                    raise ValueError(
                        f"Unknown update_method '{update_method}'. "
                        f"Use 'extend', 'update', or 'replace'."
                    )
            else:
                # No provenance - wrap with it
                self[idx] = TypeWrapperFactory.wrap(elem, prov_steps)

    def get_provenance(self, index: int = -1) -> list[Any]:
        """
        Extract provenance list matching the structure of this list.

        Returns a list with the same length as self, but with provenance
        information as values instead of the actual data values.

        Args:
            index: Which step in provenance history to return (-1 for current)

        Returns:
            List with same structure as self, but values are provenance info

        Examples:
            >>> config = ListWithProvenance(
            ...     [{"host": "localhost"}],
            ...     [{"host": {"category": "defaults", "line": 5}}]
            ... )
            >>> prov = config.get_provenance()
            >>> prov[0]["host"]["category"]  # 'defaults'
        """
        provenance_list = []

        for elem in self:
            if isinstance(elem, (DictWithProvenance, ListWithProvenance)):
                # Nested mapping - recurse
                provenance_list.append(elem.get_provenance(index=index))
            elif hasattr(elem, "provenance"):
                # Value with provenance - extract the step
                if elem.provenance and len(elem.provenance) > 0:
                    step = elem.provenance[index]
                    provenance_list.append(step.dict() if step else None)
                else:
                    provenance_list.append(None)
            else:
                # No provenance tracking on this element
                provenance_list.append(None)

        return provenance_list

    def __setitem__(self, index: int, value: Any) -> None:
        """
        Set item with automatic provenance extension.

        When setting a value, extend its provenance history to track the change.
        Unlike DictWithProvenance, we don't enforce hierarchy checks here since
        list elements are typically independent.

        Args:
            index: List index
            value: New value (can have provenance or not)

        Examples:
            >>> from herrkunft.types.factory import TypeWrapperFactory
            >>> config = ListWithProvenance([], [])
            >>> config.append("initial")
            >>>
            >>> # Set new value
            >>> val = TypeWrapperFactory.wrap("updated", {"category": "runtime"})
            >>> config[0] = val
        """
        # If custom setitem is disabled (during init), just set normally
        if not self._custom_setitem:
            super().__setitem__(index, value)
            return

        # Check if index is valid and has provenance
        try:
            old_value = self[index]
        except IndexError:
            # Index doesn't exist - just set
            super().__setitem__(index, value)
            return

        # If old value is dict or list, just replace
        if isinstance(old_value, (dict, list)):
            super().__setitem__(index, value)
            return

        # If old value has no provenance, just replace
        if not hasattr(old_value, "provenance"):
            super().__setitem__(index, value)
            return

        # Old value has provenance - extend it
        new_provenance = old_value.provenance.copy(deep=True)

        if hasattr(value, "provenance") and value.provenance:
            # New value has provenance - extend the history
            new_provenance.extend_and_mark(value.provenance, "list.__setitem__")
        else:
            # New value has no provenance - just mark modification
            new_provenance.append_modified_by("list.__setitem__")

        # Create final value with extended provenance
        final_value = copy.deepcopy(value)
        if hasattr(final_value, "provenance"):
            final_value.provenance = new_provenance
        else:
            # Wrap with factory to add provenance
            from herrkunft.types.factory import TypeWrapperFactory

            final_value = TypeWrapperFactory.wrap(value, new_provenance)

        super().__setitem__(index, final_value)

    def super_setitem(self, index: int, value: Any) -> None:
        """
        Set item bypassing all provenance tracking.

        This method calls list.__setitem__ directly, skipping all custom logic.

        Args:
            index: List index
            value: Value to set

        Examples:
            >>> config = ListWithProvenance([1], [])
            >>> # Force set a value without provenance tracking
            >>> config.super_setitem(0, "forced_value")
        """
        super().__setitem__(index, value)
