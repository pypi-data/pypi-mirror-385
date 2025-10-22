"""
Validation utilities for provenance data structures.

This module provides functions to validate the integrity and consistency
of provenance information.
"""

from pathlib import Path
from typing import Any, Optional

from loguru import logger

from ..config.settings import settings
from ..exceptions import ValidationError


def validate_provenance_step(step: Any) -> tuple[bool, Optional[str]]:
    """
    Validate a single provenance step.

    Args:
        step: ProvenanceStep object or dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)
            - is_valid: True if step is valid
            - error_message: None if valid, error description if invalid

    Example:
        >>> step = {"category": "defaults", "yaml_file": "config.yaml", "line": 5}
        >>> is_valid, error = validate_provenance_step(step)
        >>> if not is_valid:
        ...     print(f"Validation error: {error}")
    """
    # Check if step is a dict or has dict() method
    if hasattr(step, "dict"):
        step_dict = step.dict()
    elif isinstance(step, dict):
        step_dict = step
    else:
        return False, f"Step must be dict or Pydantic model, got {type(step)}"

    # Validate line number if present
    if "line" in step_dict and step_dict["line"] is not None:
        line = step_dict["line"]
        if not isinstance(line, int) or line < 1:
            return False, f"Line number must be positive integer, got {line}"

    # Validate column number if present
    if "col" in step_dict and step_dict["col"] is not None:
        col = step_dict["col"]
        if not isinstance(col, int) or col < 1:
            return False, f"Column number must be positive integer, got {col}"

    # Validate file path if present and validation is enabled
    if settings.validate_file_exists and "yaml_file" in step_dict:
        yaml_file = step_dict["yaml_file"]
        if yaml_file and not yaml_file.startswith(
            "<"
        ):  # Exclude <stream>, <string>, etc.
            file_path = Path(yaml_file)
            if not file_path.exists():
                logger.warning(f"Provenance references non-existent file: {yaml_file}")

    # Validate from_choose structure
    if "from_choose" in step_dict and step_dict["from_choose"]:
        from_choose = step_dict["from_choose"]
        if not isinstance(from_choose, list):
            return False, "from_choose must be a list"

        for idx, choose in enumerate(from_choose):
            if not isinstance(choose, dict):
                return False, f"from_choose[{idx}] must be a dict, got {type(choose)}"

    return True, None


def validate_provenance_history(history: Any) -> tuple[bool, list[str]]:
    """
    Validate a complete provenance history.

    Args:
        history: Provenance object (list of steps) to validate

    Returns:
        Tuple of (is_valid, error_messages)
            - is_valid: True if all steps are valid
            - error_messages: List of error descriptions (empty if valid)

    Example:
        >>> is_valid, errors = validate_provenance_history(value.provenance)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(error)
    """
    errors = []

    if not hasattr(history, "__iter__"):
        return False, ["Provenance history must be iterable"]

    if len(history) == 0:
        logger.debug("Empty provenance history")
        return True, []

    for idx, step in enumerate(history):
        is_valid, error = validate_provenance_step(step)
        if not is_valid:
            errors.append(f"Step {idx}: {error}")

    return len(errors) == 0, errors


def validate_provenance_tree(data: Any, path: str = "") -> tuple[bool, list[str]]:
    """
    Recursively validate provenance in a nested data structure.

    This function traverses the entire data structure and validates
    all provenance information found.

    Args:
        data: Data structure to validate (dict, list, or wrapped value)
        path: Current path in the structure (for error reporting)

    Returns:
        Tuple of (is_valid, error_messages)
            - is_valid: True if all provenance is valid
            - error_messages: List of errors with paths

    Example:
        >>> from herrkunft import load_yaml
        >>> config = load_yaml("config.yaml")
        >>> is_valid, errors = validate_provenance_tree(config)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(error)
    """
    errors = []

    # Validate current value's provenance
    if hasattr(data, "provenance"):
        is_valid, step_errors = validate_provenance_history(data.provenance)
        if not is_valid:
            for error in step_errors:
                errors.append(f"{path}: {error}" if path else error)

    # Recursively validate dict values
    if isinstance(data, dict):
        for key, value in data.items():
            key_path = f"{path}.{key}" if path else str(key)
            is_valid, nested_errors = validate_provenance_tree(value, key_path)
            errors.extend(nested_errors)

    # Recursively validate list elements
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            item_path = f"{path}[{idx}]"
            is_valid, nested_errors = validate_provenance_tree(item, item_path)
            errors.extend(nested_errors)

    return len(errors) == 0, errors


def check_provenance_consistency(
    old_step: Any, new_step: Any
) -> tuple[bool, Optional[str]]:
    """
    Check if two provenance steps are consistent for merging.

    This validates that the new step can extend the old step's history
    without creating logical inconsistencies.

    Args:
        old_step: Existing provenance step
        new_step: New provenance step to add

    Returns:
        Tuple of (is_consistent, issue_description)

    Example:
        >>> old = {"category": "defaults", "yaml_file": "base.yaml"}
        >>> new = {"category": "environment", "yaml_file": "prod.yaml"}
        >>> is_consistent, issue = check_provenance_consistency(old, new)
    """
    # Validate both steps first
    is_valid, error = validate_provenance_step(old_step)
    if not is_valid:
        return False, f"Old step invalid: {error}"

    is_valid, error = validate_provenance_step(new_step)
    if not is_valid:
        return False, f"New step invalid: {error}"

    # Get step dictionaries
    old_dict = old_step.dict() if hasattr(old_step, "dict") else old_step
    new_dict = new_step.dict() if hasattr(new_step, "dict") else new_step

    # Check for suspicious patterns
    old_file = old_dict.get("yaml_file")
    new_file = new_dict.get("yaml_file")

    # Same file with same line is suspicious unless it's a modification
    if (
        old_file
        and new_file
        and old_file == new_file
        and old_dict.get("line") == new_dict.get("line")
        and not new_dict.get("modified_by")
    ):
        return (
            False,
            f"Same file and line without modification marker: {old_file}:{old_dict.get('line')}",
        )

    return True, None


def validate_category_name(category: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a category name is valid.

    Args:
        category: Category name to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_category_name("defaults")
        >>> is_valid, error = validate_category_name("invalid category!")
    """
    if not category:
        return False, "Category name cannot be empty"

    if not isinstance(category, str):
        return False, f"Category must be string, got {type(category)}"

    # Check for valid identifier characters
    if not category.replace("_", "").replace("-", "").isalnum():
        return False, f"Category name contains invalid characters: {category}"

    # Check length
    if len(category) > 50:
        return False, f"Category name too long (max 50 chars): {category}"

    return True, None


def validate_yaml_reference(
    yaml_file: str, line: Optional[int] = None, col: Optional[int] = None
) -> tuple[bool, Optional[str]]:
    """
    Validate a YAML file reference in provenance.

    Args:
        yaml_file: Path to YAML file
        line: Optional line number
        col: Optional column number

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_yaml_reference("config.yaml", 5, 10)
    """
    if not yaml_file:
        return False, "YAML file path cannot be empty"

    # Allow special markers like <stream>, <string>
    if yaml_file.startswith("<") and yaml_file.endswith(">"):
        return True, None

    # Validate line number
    if line is not None:
        if not isinstance(line, int) or line < 1:
            return False, f"Invalid line number: {line}"

    # Validate column number
    if col is not None:
        if not isinstance(col, int) or col < 1:
            return False, f"Invalid column number: {col}"

    # Check file existence if enabled
    if settings.validate_file_exists:
        file_path = Path(yaml_file)
        if not file_path.exists():
            return False, f"File does not exist: {yaml_file}"

        # If line number provided, validate it's not beyond file length
        if line is not None:
            try:
                with file_path.open("r") as f:
                    num_lines = sum(1 for _ in f)
                if line > num_lines:
                    return False, f"Line {line} exceeds file length ({num_lines} lines)"
            except Exception as e:
                logger.warning(f"Could not read file for validation: {e}")

    return True, None


def ensure_provenance_valid(data: Any, raise_on_invalid: bool = True) -> bool:
    """
    Ensure provenance data is valid, optionally raising an exception.

    This is a convenience function that validates and optionally raises
    a ValidationError with all issues found.

    Args:
        data: Data structure to validate
        raise_on_invalid: If True, raise ValidationError on invalid data

    Returns:
        True if valid

    Raises:
        ValidationError: If raise_on_invalid is True and data is invalid

    Example:
        >>> from herrkunft import load_yaml
        >>> from herrkunft.utils.validation import ensure_provenance_valid
        >>> config = load_yaml("config.yaml")
        >>> ensure_provenance_valid(config)  # Raises if invalid
        True
    """
    is_valid, errors = validate_provenance_tree(data)

    if not is_valid:
        error_msg = "Provenance validation failed:\n" + "\n".join(
            f"  - {e}" for e in errors
        )

        if raise_on_invalid:
            raise ValidationError(error_msg)
        else:
            logger.error(error_msg)
            return False

    return True
