"""
Hierarchy management for category-based conflict resolution.

This module provides the HierarchyManager which enforces category precedence
rules and resolves conflicts when values are set from different sources.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field

from ..exceptions import CategoryConflictError, ChooseConflictError
from .provenance import ProvenanceStep


class CategoryLevel(IntEnum):
    """
    Enumeration of category hierarchy levels.

    Higher numeric values have higher precedence. Categories are ordered
    from lowest (UNKNOWN=0) to highest (BACKEND=9) precedence.
    """

    UNKNOWN = 0
    DEFAULTS = 1
    OTHER_SOFTWARE = 2
    MACHINES = 3
    COMPONENTS = 4
    SETUPS = 5
    COUPLINGS = 6
    RUNSCRIPT = 7
    COMMAND_LINE = 8
    BACKEND = 9


class HierarchyConfig(BaseModel):
    """
    Configuration for hierarchy behavior.

    Attributes:
        categories: List of category names in precedence order (low to high)
        strict_mode: Raise errors on conflicts vs. warn and override
        allow_same_level_override: Allow overrides within same category level
    """

    categories: list[str] = Field(
        default_factory=lambda: [level.name.lower() for level in CategoryLevel],
        description="Category names in precedence order",
    )
    strict_mode: bool = Field(
        default=True, description="Raise errors on conflicts vs. warn and override"
    )
    allow_same_level_override: bool = Field(
        default=False, description="Allow overrides within same category level"
    )

    model_config = {"frozen": False}


class HierarchyManager:
    """
    Manages category hierarchy and conflict resolution.

    The HierarchyManager determines whether a new value should override an
    existing value based on their category levels. It enforces rules like:
    - Higher category levels always override lower ones
    - Same-level conflicts can be configured to error or allow override
    - Choose blocks can override at the same level
    - Nested choose blocks are handled correctly

    Example:
        >>> config = HierarchyConfig(strict_mode=True)
        >>> manager = HierarchyManager(config)
        >>> old_step = ProvenanceStep(category="defaults")
        >>> new_step = ProvenanceStep(category="runtime")
        >>> should_override, error = manager.should_override(old_step, new_step, "mykey")
        >>> print(should_override)  # True - runtime > defaults
    """

    def __init__(self, config: Optional[HierarchyConfig] = None):
        """
        Initialize hierarchy manager.

        Args:
            config: Custom hierarchy configuration. If None, uses default.
        """
        self.config = config or HierarchyConfig()
        self._level_map = self._build_level_map()

    def _build_level_map(self) -> dict[str, int]:
        """
        Build mapping from category name to level.

        Returns:
            Dictionary mapping category names to numeric levels
        """
        return {cat: idx for idx, cat in enumerate(self.config.categories)}

    def get_level(self, category: Optional[str]) -> int:
        """
        Get hierarchy level for a category.

        Args:
            category: Category name (case-insensitive)

        Returns:
            Numeric level (higher = higher precedence). Returns BACKEND
            level for None category.
        """
        if category is None:
            return CategoryLevel.BACKEND

        return self._level_map.get(category.lower(), CategoryLevel.UNKNOWN)

    def should_override(
        self, old_step: ProvenanceStep, new_step: ProvenanceStep, key: str
    ) -> tuple[bool, Optional[Exception]]:
        """
        Determine if new value should override old value.

        This is the core conflict resolution logic. It checks:
        1. Category levels (higher always wins)
        2. Choose block nesting (nested choose can override)
        3. Same-level conflict rules (strict mode vs. allow)

        Args:
            old_step: Provenance of existing value
            new_step: Provenance of new value
            key: Configuration key being set

        Returns:
            Tuple of (should_override, error_if_conflict)
            - should_override: True if new value should replace old
            - error_if_conflict: Exception to raise, or None

        Example:
            >>> old = ProvenanceStep(category="defaults")
            >>> new = ProvenanceStep(category="components")
            >>> should_override, err = manager.should_override(old, new, "key")
            >>> print(should_override, err)  # (True, None)
        """
        old_level = self.get_level(old_step.category)
        new_level = self.get_level(new_step.category)

        # Higher level always wins
        if new_level > old_level:
            logger.trace(
                f"Allowing override of {key}: new category '{new_step.category}' "
                f"({new_level}) > old category '{old_step.category}' ({old_level})"
            )
            return True, None

        # Lower level never wins
        if new_level < old_level:
            logger.debug(
                f"Ignoring {key} from lower level ({new_step.category}) "
                f"than existing ({old_step.category})"
            )
            return False, None

        # Same level - check conflict resolution rules
        return self._resolve_same_level(old_step, new_step, key)

    def _resolve_same_level(
        self, old_step: ProvenanceStep, new_step: ProvenanceStep, key: str
    ) -> tuple[bool, Optional[Exception]]:
        """
        Resolve conflicts at the same hierarchy level.

        Args:
            old_step: Provenance of existing value
            new_step: Provenance of new value
            key: Configuration key

        Returns:
            Tuple of (should_override, error_if_conflict)
        """
        # Check for choose block conflicts
        old_from_choose = old_step.from_choose
        new_from_choose = new_step.from_choose

        if old_from_choose and new_from_choose:
            # Check if new choose is nested in old choose
            if not self._is_nested_choose(old_from_choose, new_from_choose):
                old_choose_key = (
                    old_from_choose[-1].get("choose_key", "unknown")
                    if old_from_choose
                    else "unknown"
                )
                new_choose_key = (
                    new_from_choose[-1].get("choose_key", "unknown")
                    if new_from_choose
                    else "unknown"
                )

                error = ChooseConflictError(
                    key=key,
                    old_choose=old_choose_key,
                    new_choose=new_choose_key,
                    category=old_step.category,
                    old_step=old_step,
                    new_step=new_step,
                )
                return False, error if self.config.strict_mode else None

        # Choose block can override
        if new_from_choose:
            logger.trace(
                f"Allowing override of {key} from choose block: "
                f"{new_from_choose[-1].get('choose_key', 'unknown')}"
            )
            return True, None

        # Same level, no choose blocks
        if self.config.allow_same_level_override:
            logger.warning(
                f"Overriding {key} at same level {old_step.category} "
                f"(allow_same_level_override=True)"
            )
            return True, None

        # Strict mode - raise error
        error = CategoryConflictError(
            key=key,
            category=old_step.category,
            old_step=old_step,
            new_step=new_step,
        )
        return False, error if self.config.strict_mode else None

    @staticmethod
    def _is_nested_choose(old_choose: list[Dict], new_choose: list[Dict]) -> bool:
        """
        Check if new choose is nested within old choose.

        A choose is nested if it starts with all the elements of the parent choose.

        Args:
            old_choose: Existing choose block history
            new_choose: New choose block history

        Returns:
            True if new_choose is nested within old_choose

        Example:
            >>> old = [{"choose_key": "resolution"}]
            >>> new = [{"choose_key": "resolution"}, {"choose_key": "platform"}]
            >>> HierarchyManager._is_nested_choose(old, new)
            True
        """
        if len(new_choose) < len(old_choose):
            return False

        return new_choose[: len(old_choose)] == old_choose
