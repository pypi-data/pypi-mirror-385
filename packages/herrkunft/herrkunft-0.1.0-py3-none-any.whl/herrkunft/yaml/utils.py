"""
Utility functions for YAML processing with provenance.

This module provides helper functions for working with YAML files and
provenance data, including validation, merging, and conversion utilities.
"""

import re
from typing import Any, Optional


def validate_provenance_structure(
    data: dict[str, Any], provenance: dict[str, Any]
) -> bool:
    """
    Validate that data and provenance dictionaries have matching structure.

    This function recursively checks that the provenance dictionary has the same
    structure as the data dictionary - same keys, same nesting levels.

    Args:
        data: Dictionary containing loaded YAML data
        provenance: Dictionary containing provenance information

    Returns:
        True if structures match, False otherwise

    Examples:
        >>> data = {"a": 1, "b": {"c": 2}}
        >>> prov = {"a": {...}, "b": {"c": {...}}}
        >>> validate_provenance_structure(data, prov)
        True
    """
    # Check that all data keys have provenance
    for key in data.keys():
        if key not in provenance:
            return False

        # Recursively check nested structures
        if isinstance(data[key], dict):
            if not isinstance(provenance[key], dict):
                return False
            if not validate_provenance_structure(data[key], provenance[key]):
                return False
        elif isinstance(data[key], list):
            if not isinstance(provenance[key], list):
                return False
            if len(data[key]) != len(provenance[key]):
                return False
            # Check each list element
            for i, item in enumerate(data[key]):
                if isinstance(item, dict):
                    if not isinstance(provenance[key][i], dict):
                        return False
                    if not validate_provenance_structure(item, provenance[key][i]):
                        return False

    return True


def get_provenance_for_key(
    data: dict[str, Any],
    provenance: dict[str, Any],
    key_path: str,
    separator: str = ".",
) -> Optional[dict[str, Any]]:
    """
    Get provenance information for a specific key path.

    This function retrieves provenance for a deeply nested key using dot notation.
    For example, "database.connection.host" will navigate through nested dicts.

    Args:
        data: Dictionary containing data
        provenance: Dictionary containing provenance
        key_path: Dot-separated path to key (e.g., "a.b.c")
        separator: Separator character for path (default: ".")

    Returns:
        Provenance dict for the key, or None if key doesn't exist

    Examples:
        >>> data = {"db": {"host": "localhost"}}
        >>> prov = {"db": {"host": {"line": 5, "col": 8}}}
        >>> get_provenance_for_key(data, prov, "db.host")
        {'line': 5, 'col': 8, ...}
    """
    keys = key_path.split(separator)

    current_data = data
    current_prov = provenance

    for key in keys:
        if not isinstance(current_data, dict) or key not in current_data:
            return None
        if not isinstance(current_prov, dict) or key not in current_prov:
            return None

        current_data = current_data[key]
        current_prov = current_prov[key]

    # If current_prov is still a dict with nested structure, it means we're at
    # a container level. Return the provenance as-is.
    return current_prov


def merge_provenance_dicts(
    prov1: dict[str, Any], prov2: dict[str, Any], prefer_second: bool = True
) -> dict[str, Any]:
    """
    Merge two provenance dictionaries.

    This function merges two provenance dictionaries with the same structure.
    When both have provenance for the same key, the second is preferred by default.

    Args:
        prov1: First provenance dictionary
        prov2: Second provenance dictionary
        prefer_second: If True, prefer prov2 values; if False, prefer prov1

    Returns:
        Merged provenance dictionary

    Examples:
        >>> p1 = {"a": {"line": 1}, "b": {"line": 2}}
        >>> p2 = {"a": {"line": 10}, "c": {"line": 3}}
        >>> merged = merge_provenance_dicts(p1, p2)
        >>> merged["a"]["line"]
        10
    """
    result = {}

    # Get all keys from both dicts
    all_keys = set(prov1.keys()) | set(prov2.keys())

    for key in all_keys:
        if key in prov1 and key in prov2:
            # Both have this key
            if isinstance(prov1[key], dict) and isinstance(prov2[key], dict):
                # Check if it's a provenance leaf or nested structure
                if "yaml_file" in prov1[key] or "yaml_file" in prov2[key]:
                    # It's a provenance leaf - choose one
                    result[key] = prov2[key] if prefer_second else prov1[key]
                else:
                    # It's nested structure - recurse
                    result[key] = merge_provenance_dicts(
                        prov1[key], prov2[key], prefer_second
                    )
            elif isinstance(prov1[key], list) and isinstance(prov2[key], list):
                # For lists, prefer the second one entirely
                result[key] = prov2[key] if prefer_second else prov1[key]
            else:
                result[key] = prov2[key] if prefer_second else prov1[key]
        elif key in prov1:
            result[key] = prov1[key]
        else:
            result[key] = prov2[key]

    return result


def filter_provenance_by_category(
    provenance: dict[str, Any], category: str
) -> dict[str, Any]:
    """
    Filter provenance dictionary to only include entries from a specific category.

    This function recursively filters a provenance dictionary to only include
    entries that match the specified category.

    Args:
        provenance: Provenance dictionary to filter
        category: Category to filter for (e.g., "components", "defaults")

    Returns:
        Filtered provenance dictionary with same structure

    Examples:
        >>> prov = {
        ...     "a": {"category": "defaults", "line": 1},
        ...     "b": {"category": "components", "line": 2}
        ... }
        >>> filtered = filter_provenance_by_category(prov, "defaults")
        >>> "a" in filtered
        True
        >>> "b" in filtered
        False
    """
    result = {}

    for key, value in provenance.items():
        if isinstance(value, dict):
            # Check if it's a provenance leaf
            if "category" in value:
                if value["category"] == category:
                    result[key] = value
            else:
                # It's a nested structure - recurse
                filtered = filter_provenance_by_category(value, category)
                if filtered:  # Only include if non-empty
                    result[key] = filtered
        elif isinstance(value, list):
            # Filter list elements
            filtered_list = []
            for item in value:
                if isinstance(item, dict):
                    if "category" in item and item["category"] == category:
                        filtered_list.append(item)
                    else:
                        # Nested dict in list
                        filtered_item = filter_provenance_by_category(item, category)
                        if filtered_item:
                            filtered_list.append(filtered_item)
            if filtered_list:
                result[key] = filtered_list

    return result


def format_provenance_for_display(provenance: dict[str, Any], indent: int = 0) -> str:
    """
    Format provenance dictionary as human-readable string.

    This function converts a provenance dictionary into a nicely formatted
    string suitable for displaying to users or logging.

    Args:
        provenance: Provenance dictionary to format
        indent: Indentation level (used for recursion)

    Returns:
        Formatted string representation of provenance

    Examples:
        >>> prov = {"database": {"host": {"line": 5, "yaml_file": "config.yaml"}}}
        >>> print(format_provenance_for_display(prov))
        database:
          host: config.yaml:5
    """
    lines = []
    indent_str = "  " * indent

    for key, value in provenance.items():
        if isinstance(value, dict):
            # Check if it's a provenance leaf
            if "yaml_file" in value:
                file = value.get("yaml_file", "unknown")
                line = value.get("line", "?")
                col = value.get("col", "?")
                cat = value.get("category", "")

                location = f"{file}:{line}:{col}"
                if cat:
                    location += f" ({cat})"

                lines.append(f"{indent_str}{key}: {location}")
            else:
                # Nested structure
                lines.append(f"{indent_str}{key}:")
                lines.append(format_provenance_for_display(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{indent_str}{key}:")
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    if "yaml_file" in item:
                        file = item.get("yaml_file", "unknown")
                        line = item.get("line", "?")
                        lines.append(f"{indent_str}  [{i}]: {file}:{line}")
                    else:
                        lines.append(f"{indent_str}  [{i}]:")
                        lines.append(format_provenance_for_display(item, indent + 2))

    return "\n".join(lines)


def extract_file_list_from_provenance(provenance: dict[str, Any]) -> list[str]:
    """
    Extract list of unique YAML files referenced in provenance.

    This function recursively scans a provenance dictionary and returns a list
    of all unique YAML files that contributed values.

    Args:
        provenance: Provenance dictionary

    Returns:
        List of unique file paths (sorted)

    Examples:
        >>> prov = {
        ...     "a": {"yaml_file": "/path/to/file1.yaml"},
        ...     "b": {"yaml_file": "/path/to/file2.yaml"}
        ... }
        >>> files = extract_file_list_from_provenance(prov)
        >>> len(files)
        2
    """
    files = set()

    def extract_recursive(prov_dict):
        if isinstance(prov_dict, dict):
            if "yaml_file" in prov_dict:
                files.add(prov_dict["yaml_file"])
            else:
                for value in prov_dict.values():
                    extract_recursive(value)
        elif isinstance(prov_dict, list):
            for item in prov_dict:
                extract_recursive(item)

    extract_recursive(provenance)
    return sorted(list(files))


def sanitize_yaml_value(value: str) -> str:
    """
    Sanitize a string value for safe YAML output.

    This function escapes special characters and handles multiline strings
    to ensure they are safely represented in YAML.

    Args:
        value: String value to sanitize

    Returns:
        Sanitized string safe for YAML output

    Examples:
        >>> sanitize_yaml_value("simple")
        'simple'
        >>> sanitize_yaml_value("with: colon")
        '"with: colon"'
    """
    if not isinstance(value, str):
        return value

    # Characters that need quoting in YAML
    special_chars = r"[:{}\[\],&*#?|\-<>=!%@`]"

    # Check if string needs quoting
    if re.search(special_chars, value):
        # Escape internal quotes
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'

    # Check for leading/trailing whitespace
    if value != value.strip():
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'

    return value


def create_minimal_provenance(
    file_path: str, category: Optional[str] = None, subcategory: Optional[str] = None
) -> dict[str, Any]:
    """
    Create a minimal provenance dictionary for programmatically created values.

    This function creates a basic provenance dictionary for values that weren't
    loaded from a YAML file but need provenance tracking.

    Args:
        file_path: Path to associate with this value (may be synthetic)
        category: Optional category
        subcategory: Optional subcategory

    Returns:
        Minimal provenance dictionary

    Examples:
        >>> prov = create_minimal_provenance("<runtime>", category="backend")
        >>> prov["yaml_file"]
        '<runtime>'
        >>> prov["category"]
        'backend'
    """
    return {
        "yaml_file": file_path,
        "line": None,
        "col": None,
        "category": category,
        "subcategory": subcategory,
    }
