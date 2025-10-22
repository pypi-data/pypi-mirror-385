"""
Decorators for preserving provenance in recursive and transformation functions.

This module provides decorators that ensure provenance information is correctly
maintained when values are transformed or passed through recursive operations.
"""

import copy
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def track_provenance(
    modify_provenance: bool = True, functions_to_skip: list = None
) -> Callable:
    """
    Decorator to preserve and track provenance through function calls.

    This decorator is designed for functions that transform values while
    preserving their provenance. It handles:
    - Copying provenance from input to output
    - Marking modifications in the provenance history
    - Handling values with and without provenance

    Args:
        modify_provenance: If True, mark the function in provenance history
        functions_to_skip: List of function names that should not modify provenance

    Returns:
        Decorator function

    Example:
        >>> @track_provenance()
        ... def my_transform(config, value):
        ...     return str(value).upper()
        >>>
        >>> # Provenance from 'value' is preserved and marked as modified by my_transform
    """
    if functions_to_skip is None:
        functions_to_skip = []

    def decorator(func: Callable) -> Callable:
        # Determine if this function should modify provenance
        should_modify = modify_provenance and func.__name__ not in functions_to_skip

        @wraps(func)
        def wrapper(tree: Any, rhs: Any, *args, **kwargs) -> Any:
            """
            Wrapper that preserves provenance through the function call.

            Args:
                tree: First argument (often a context or configuration tree)
                rhs: Right-hand side value (the value being transformed)
                *args: Additional positional arguments
                **kwargs: Additional keyword arguments

            Returns:
                Transformed value with preserved/updated provenance
            """
            # Temporarily disable custom __setitem__ if present
            custom_setitem_was_active = False
            if hasattr(rhs, "custom_setitem") and rhs.custom_setitem:
                rhs.custom_setitem = False
                custom_setitem_was_active = True

            # Call the original function
            output = func(tree, rhs, *args, **kwargs)

            # Handle provenance preservation
            if hasattr(rhs, "provenance"):
                provenance = copy.deepcopy(rhs.provenance)

                # Value was modified (type changed or value changed)
                if type(rhs) != type(output) or rhs != output:
                    output = copy.deepcopy(output)

                    # If output already has provenance, extend it
                    if hasattr(output, "provenance"):
                        if should_modify:
                            provenance.extend_and_mark(output.provenance, func.__name__)
                        output.provenance = provenance

                    # If output has no provenance but rhs did, transfer it
                    elif provenance is not None:
                        if should_modify:
                            provenance.append_modified_by(func.__name__)

                        # Wrap output with provenance
                        from ..types.base import ProvenanceWrapperFactory

                        output = ProvenanceWrapperFactory.wrap(output, provenance)

            # Restore custom_setitem if it was active
            if custom_setitem_was_active:
                rhs.custom_setitem = True

            return output

        return wrapper

    return decorator


def keep_provenance_in_recursive_function(func: Callable) -> Callable:
    """
    Decorator for recursive functions to preserve provenance.

    This is a convenience wrapper around track_provenance specifically
    designed for recursive functions that might not want to mark every
    recursion in the provenance history.

    Args:
        func: The recursive function to decorate

    Returns:
        Decorated function that preserves provenance

    Example:
        >>> @keep_provenance_in_recursive_function
        ... def recursive_transform(tree, value):
        ...     if isinstance(value, dict):
        ...         return {k: recursive_transform(tree, v) for k, v in value.items()}
        ...     return value * 2
    """
    # List of functions that shouldn't modify provenance on every call
    functions_to_skip = ["find_variable", "recursive_run_function"]

    return track_provenance(
        modify_provenance=True, functions_to_skip=functions_to_skip
    )(func)


def preserve_provenance(func: Callable) -> Callable:
    """
    Simple decorator that preserves provenance without marking modifications.

    Use this for functions that pass through values without changing them,
    or for read-only operations.

    Args:
        func: Function to decorate

    Returns:
        Decorated function

    Example:
        >>> @preserve_provenance
        ... def get_value(config, key):
        ...     return config.get(key)
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        result = func(*args, **kwargs)

        # If the first argument has provenance and result doesn't, copy it
        if (
            args
            and hasattr(args[0], "provenance")
            and not hasattr(result, "provenance")
        ):
            from ..types.base import ProvenanceWrapperFactory

            return ProvenanceWrapperFactory.wrap(result, args[0].provenance)

        return result

    return wrapper
