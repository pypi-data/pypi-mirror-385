"""
Utilities for removing provenance information from wrapped objects.

This module provides functions to extract original values from provenance-wrapped
objects and to extract provenance information as separate structures.
"""

from typing import Any, TypeVar

T = TypeVar("T")


def clean_provenance(data: Any) -> Any:
    """
    Remove all provenance wrappers and return original values.

    This function recursively processes data structures and removes any
    provenance tracking, returning clean Python objects (dict, list, etc.)
    that can be used with any standard library or external API.

    Args:
        data: Data with potential provenance wrappers. Can be:
            - Provenance-wrapped values (with .value attribute)
            - Dictionaries (including DictWithProvenance)
            - Lists (including ListWithProvenance)
            - Any other Python objects (returned as-is)

    Returns:
        Clean data without provenance wrappers:
            - Provenance-wrapped values -> their .value attribute
            - Dicts -> clean dict with cleaned keys and values
            - Lists -> clean list with cleaned elements
            - Other types -> returned unchanged

    Example:
        >>> from herrkunft import load_yaml, clean_provenance
        >>> config = load_yaml("config.yaml")
        >>> clean_config = clean_provenance(config)
        >>> # clean_config is now a regular dict without provenance

        >>> # With nested structures
        >>> nested = {"key": wrapped_value, "nested": {"inner": wrapped_inner}}
        >>> clean = clean_provenance(nested)
        >>> # All nested values are now unwrapped
    """
    # Handle provenance wrappers with .value attribute
    if hasattr(data, "value") and not isinstance(data, type):
        return clean_provenance(data.value)

    # Recursively clean lists
    if isinstance(data, list):
        return [clean_provenance(item) for item in data]

    # Recursively clean dicts
    if isinstance(data, dict):
        return {
            clean_provenance(key): clean_provenance(value)
            for key, value in data.items()
        }

    # Return as-is for other types
    return data


def strip_provenance(data: T) -> T:
    """
    Alias for clean_provenance() for backward compatibility.

    This is the function name used in esm_tools. It does the same thing
    as clean_provenance().

    Args:
        data: Data with potential provenance wrappers

    Returns:
        Clean data without provenance

    Example:
        >>> from herrkunft.utils import strip_provenance
        >>> clean = strip_provenance(wrapped_data)
    """
    return clean_provenance(data)


def extract_provenance_tree(data: Any, index: int = -1) -> Any:
    """
    Extract the provenance structure from a data tree.

    This function creates a parallel structure containing only provenance
    information, matching the shape of the input data.

    Args:
        data: Data with provenance. Can be:
            - DictWithProvenance
            - ListWithProvenance
            - Any provenance-wrapped value
            - Regular Python objects (returns None)
        index: Which provenance step to extract:
            - -1 (default): Current/last provenance step
            - 0: First provenance step
            - n: Specific step in history

    Returns:
        Provenance structure matching input shape:
            - For dicts: Dict with same keys, values are provenance info
            - For lists: List with same length, elements are provenance info
            - For wrapped values: List of provenance step dictionaries
            - For regular values: None

    Example:
        >>> from herrkunft import load_yaml, extract_provenance_tree
        >>> config = load_yaml("config.yaml")
        >>> prov_tree = extract_provenance_tree(config)
        >>> print(prov_tree["database"]["url"])
        {'category': 'defaults', 'yaml_file': 'config.yaml', 'line': 5}

        >>> # Extract original provenance (first step)
        >>> original = extract_provenance_tree(config, index=0)

        >>> # Get full history
        >>> full_history = extract_provenance_tree(config, index=None)
    """
    # Import here to avoid circular imports
    from ..types.base import HasProvenance

    # Handle DictWithProvenance
    if hasattr(data, "get_provenance") and isinstance(data, dict):
        return data.get_provenance(index)

    # Handle ListWithProvenance
    if hasattr(data, "get_provenance") and isinstance(data, list):
        return data.get_provenance(index)

    # Handle any object with provenance attribute
    if isinstance(data, HasProvenance) or hasattr(data, "provenance"):
        prov = data.provenance
        if prov:
            if index is None:
                # Return full history
                return prov.to_dict() if hasattr(prov, "to_dict") else list(prov)
            elif index < len(prov):
                step = prov[index]
                return step.dict() if hasattr(step, "dict") else step
        return None

    # No provenance found
    return None


def get_original_type(data: Any) -> type:
    """
    Get the original type of a provenance-wrapped object.

    This function returns the type of the wrapped value, not the wrapper itself.

    Args:
        data: Potentially wrapped value

    Returns:
        The type of the original unwrapped value

    Example:
        >>> from herrkunft.types.base import ProvenanceWrapperFactory
        >>> wrapped = ProvenanceWrapperFactory.wrap(42, {})
        >>> get_original_type(wrapped)
        <class 'int'>
    """
    if hasattr(data, "value"):
        return type(data.value)
    return type(data)


def is_wrapped(data: Any) -> bool:
    """
    Check if a value is provenance-wrapped.

    Args:
        data: Value to check

    Returns:
        True if the value has provenance tracking, False otherwise

    Example:
        >>> from herrkunft import load_yaml
        >>> config = load_yaml("config.yaml")
        >>> is_wrapped(config["key"])
        True
        >>> is_wrapped(42)
        False
    """
    from ..types.base import HasProvenance

    return isinstance(data, HasProvenance) or (
        hasattr(data, "provenance") and hasattr(data, "_provenance")
    )


def has_provenance(data: Any) -> bool:
    """
    Check if a value or any nested value has provenance information.

    This is a deep check that recursively examines nested structures.

    Args:
        data: Value or structure to check

    Returns:
        True if any value in the structure has provenance

    Example:
        >>> has_provenance({"key": wrapped_value})
        True
        >>> has_provenance({"key": "regular_value"})
        False
    """
    if is_wrapped(data):
        return True

    if isinstance(data, dict):
        return any(has_provenance(v) for v in data.values())

    if isinstance(data, list):
        return any(has_provenance(item) for item in data)

    return False


def extract_value(data: Any) -> Any:
    """
    Extract the actual value from a potentially wrapped object.

    This is similar to clean_provenance but only works on single values,
    not nested structures.

    Args:
        data: Potentially wrapped value

    Returns:
        The unwrapped value

    Example:
        >>> wrapped = ProvenanceWrapperFactory.wrap("hello", {})
        >>> extract_value(wrapped)
        'hello'
    """
    if hasattr(data, "value"):
        return data.value
    return data
