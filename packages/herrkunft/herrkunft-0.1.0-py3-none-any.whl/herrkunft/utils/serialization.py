"""
Serialization utilities for provenance data structures.

This module provides functions to convert provenance-annotated data
to various serialization formats (JSON, dict, etc.) and back.
"""

import json
from pathlib import Path
from typing import Any, Optional, Union

from loguru import logger

from ..exceptions import SerializationError
from .cleaning import clean_provenance, extract_provenance_tree


def to_dict(
    data: Any, include_provenance: bool = False, clean: bool = False
) -> dict[str, Any]:
    """
    Convert data to a dictionary representation.

    Args:
        data: Data to convert (dict, list, or any wrapped value)
        include_provenance: If True, include provenance in the output structure
        clean: If True, remove all provenance wrappers (overrides include_provenance)

    Returns:
        Dictionary representation of the data

    Example:
        >>> from herrkunft import load_yaml
        >>> from herrkunft.utils.serialization import to_dict
        >>> config = load_yaml("config.yaml")

        >>> # Clean dict without provenance
        >>> clean_dict = to_dict(config, clean=True)

        >>> # Dict with separate provenance structure
        >>> result = to_dict(config, include_provenance=True)
        >>> print(result["data"])  # The actual data
        >>> print(result["provenance"])  # The provenance tree
    """
    if clean:
        return clean_provenance(data)

    if not include_provenance:
        return clean_provenance(data)

    # Include provenance in separate structure
    return {
        "data": clean_provenance(data),
        "provenance": extract_provenance_tree(data),
    }


def to_json(
    data: Any,
    include_provenance: bool = False,
    clean: bool = False,
    indent: Optional[int] = 2,
    **json_kwargs: Any,
) -> str:
    """
    Convert data to JSON string.

    Args:
        data: Data to convert
        include_provenance: If True, include provenance in output
        clean: If True, remove all provenance wrappers
        indent: JSON indentation (None for compact)
        **json_kwargs: Additional arguments passed to json.dumps()

    Returns:
        JSON string representation

    Raises:
        SerializationError: If data cannot be serialized to JSON

    Example:
        >>> from herrkunft import load_yaml
        >>> from herrkunft.utils.serialization import to_json
        >>> config = load_yaml("config.yaml")

        >>> # Clean JSON
        >>> json_str = to_json(config, clean=True)

        >>> # With provenance
        >>> json_str = to_json(config, include_provenance=True, indent=4)
    """
    try:
        dict_data = to_dict(data, include_provenance=include_provenance, clean=clean)
        return json.dumps(dict_data, indent=indent, **json_kwargs)
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Failed to serialize to JSON: {e}") from e


def to_json_file(
    data: Any,
    file_path: Union[str, Path],
    include_provenance: bool = False,
    clean: bool = False,
    indent: Optional[int] = 2,
    **json_kwargs: Any,
) -> None:
    """
    Write data to JSON file.

    Args:
        data: Data to write
        file_path: Path to output JSON file
        include_provenance: If True, include provenance in output
        clean: If True, remove all provenance wrappers
        indent: JSON indentation (None for compact)
        **json_kwargs: Additional arguments passed to json.dump()

    Raises:
        SerializationError: If data cannot be written

    Example:
        >>> from herrkunft import load_yaml
        >>> from herrkunft.utils.serialization import to_json_file
        >>> config = load_yaml("config.yaml")
        >>> to_json_file(config, "output.json", clean=True)
    """
    try:
        file_path = Path(file_path)
        dict_data = to_dict(data, include_provenance=include_provenance, clean=clean)

        with file_path.open("w") as f:
            json.dump(dict_data, f, indent=indent, **json_kwargs)

        logger.debug(f"Wrote data to {file_path}")

    except (OSError, TypeError, ValueError) as e:
        raise SerializationError(f"Failed to write JSON to {file_path}: {e}") from e


def from_dict(
    data: dict[str, Any],
    provenance: Optional[dict[str, Any]] = None,
) -> Any:
    """
    Create data structure from dictionary with optional provenance.

    This is useful for deserializing data that was serialized with
    to_dict(include_provenance=True).

    Args:
        data: Dictionary containing the data
        provenance: Optional provenance structure (if separated)

    Returns:
        Data structure with provenance if provided

    Example:
        >>> from herrkunft.utils.serialization import from_dict
        >>> data = {"key": "value"}
        >>> prov = {"key": {"category": "defaults", "line": 1}}
        >>> result = from_dict(data, prov)
    """
    # Import here to avoid circular imports
    from ..types.mappings import DictWithProvenance

    if provenance is not None:
        return DictWithProvenance(data, provenance)
    return data


def from_json(json_str: str, with_provenance: bool = False) -> Any:
    """
    Parse JSON string to data structure.

    Args:
        json_str: JSON string to parse
        with_provenance: If True, expect provenance in the JSON structure

    Returns:
        Parsed data structure

    Raises:
        SerializationError: If JSON cannot be parsed

    Example:
        >>> from herrkunft.utils.serialization import from_json
        >>> json_str = '{"key": "value"}'
        >>> data = from_json(json_str)

        >>> # With provenance
        >>> json_with_prov = '{"data": {...}, "provenance": {...}}'
        >>> data = from_json(json_with_prov, with_provenance=True)
    """
    try:
        parsed = json.loads(json_str)

        if with_provenance:
            if not isinstance(parsed, dict) or "data" not in parsed:
                raise SerializationError(
                    "JSON with provenance must have 'data' and 'provenance' keys"
                )
            return from_dict(parsed["data"], parsed.get("provenance"))

        return parsed

    except json.JSONDecodeError as e:
        raise SerializationError(f"Failed to parse JSON: {e}") from e


def from_json_file(file_path: Union[str, Path], with_provenance: bool = False) -> Any:
    """
    Read data from JSON file.

    Args:
        file_path: Path to JSON file
        with_provenance: If True, expect provenance in the file

    Returns:
        Parsed data structure

    Raises:
        SerializationError: If file cannot be read or parsed

    Example:
        >>> from herrkunft.utils.serialization import from_json_file
        >>> data = from_json_file("config.json")
    """
    try:
        file_path = Path(file_path)

        with file_path.open("r") as f:
            parsed = json.load(f)

        if with_provenance:
            if not isinstance(parsed, dict) or "data" not in parsed:
                raise SerializationError(
                    "JSON with provenance must have 'data' and 'provenance' keys"
                )
            return from_dict(parsed["data"], parsed.get("provenance"))

        return parsed

    except (OSError, json.JSONDecodeError) as e:
        raise SerializationError(f"Failed to read JSON from {file_path}: {e}") from e


def provenance_to_dict(provenance: Any) -> list[dict[str, Any]]:
    """
    Convert a Provenance object to a list of dictionaries.

    Args:
        provenance: Provenance object to convert

    Returns:
        List of provenance step dictionaries

    Example:
        >>> from herrkunft import load_yaml
        >>> config = load_yaml("config.yaml")
        >>> prov_list = provenance_to_dict(config["key"].provenance)
    """
    if hasattr(provenance, "to_dict"):
        return provenance.to_dict()

    if hasattr(provenance, "__iter__"):
        result = []
        for step in provenance:
            if hasattr(step, "dict"):
                result.append(step.dict(exclude_none=True))
            elif isinstance(step, dict):
                result.append(step)
            else:
                result.append(str(step))
        return result

    return []


def dict_to_provenance(data: list[dict[str, Any]]) -> Any:
    """
    Convert a list of dictionaries back to a Provenance object.

    Args:
        data: List of provenance step dictionaries

    Returns:
        Provenance object

    Example:
        >>> from herrkunft.utils.serialization import dict_to_provenance
        >>> prov_data = [{"category": "defaults", "line": 1}]
        >>> prov = dict_to_provenance(prov_data)
    """
    # Import here to avoid circular imports
    from ..core.provenance import Provenance

    return Provenance(data)


def serialize_for_display(
    data: Any,
    max_depth: int = 3,
    current_depth: int = 0,
    show_provenance: bool = True,
) -> str:
    """
    Serialize data for human-readable display.

    This creates a formatted string representation suitable for logging
    or debugging output.

    Args:
        data: Data to serialize
        max_depth: Maximum nesting depth to display
        current_depth: Current depth (for recursion)
        show_provenance: Show provenance information inline

    Returns:
        Formatted string representation

    Example:
        >>> from herrkunft import load_yaml
        >>> from herrkunft.utils.serialization import serialize_for_display
        >>> config = load_yaml("config.yaml")
        >>> print(serialize_for_display(config))
    """
    indent = "  " * current_depth

    if current_depth >= max_depth:
        return f"{indent}..."

    # Handle dicts
    if isinstance(data, dict):
        lines = [f"{indent}{{"]
        for key, value in data.items():
            prov_info = ""
            if show_provenance and hasattr(value, "provenance") and value.provenance:
                prov_step = value.provenance.current
                if prov_step:
                    cat = getattr(prov_step, "category", None)
                    line = getattr(prov_step, "line", None)
                    if cat or line:
                        prov_info = (
                            f" # [{cat}:{line}]"
                            if cat and line
                            else f" # [{cat or line}]"
                        )

            value_str = serialize_for_display(
                value, max_depth, current_depth + 1, show_provenance
            ).lstrip()
            lines.append(f"{indent}  {key}: {value_str}{prov_info}")
        lines.append(f"{indent}}}")
        return "\n".join(lines)

    # Handle lists
    elif isinstance(data, list):
        if len(data) == 0:
            return f"{indent}[]"
        lines = [f"{indent}["]
        for item in data:
            item_str = serialize_for_display(
                item, max_depth, current_depth + 1, show_provenance
            )
            lines.append(f"{indent}  {item_str.lstrip()},")
        lines.append(f"{indent}]")
        return "\n".join(lines)

    # Handle wrapped values
    elif hasattr(data, "value"):
        return f"{indent}{data.value}"

    # Handle other types
    else:
        return f"{indent}{data}"
