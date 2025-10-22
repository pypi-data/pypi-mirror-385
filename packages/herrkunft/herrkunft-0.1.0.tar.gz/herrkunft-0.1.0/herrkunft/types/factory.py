"""
Factory for creating provenance-wrapped types dynamically.

This module provides the TypeWrapperFactory class that creates wrapper classes
on-the-fly for arbitrary Python types while preserving their original behavior
and adding provenance tracking.
"""

from typing import Any, Type, TypeVar, Union

from herrkunft.core.provenance import Provenance
from herrkunft.types.base import HasProvenance, ProvenanceMixin
from herrkunft.types.wrappers import (
    BoolWithProvenance,
    FloatWithProvenance,
    IntWithProvenance,
    NoneWithProvenance,
    StrWithProvenance,
)

T = TypeVar("T")


class TypeWrapperFactory:
    """
    Factory for creating provenance-wrapped objects.

    This factory creates wrapper classes dynamically for types that can be
    subclassed, and uses pre-defined wrappers for types that cannot be
    subclassed (bool, NoneType).

    The factory maintains a cache of created wrapper classes for performance,
    avoiding the overhead of recreating the same wrapper class multiple times.

    Examples:
        >>> factory = TypeWrapperFactory()
        >>> wrapped = factory.wrap("hello", {"category": "defaults"})
        >>> print(wrapped.provenance.current.category)  # 'defaults'
        >>> isinstance(wrapped, str)  # True
    """

    # Cache of created wrapper classes: {type: wrapper_class}
    _class_cache: dict[Type, Type] = {}

    # Pre-defined wrapper classes for common types
    _predefined_wrappers: dict[Type, Type] = {
        str: StrWithProvenance,
        int: IntWithProvenance,
        float: FloatWithProvenance,
    }

    @classmethod
    def wrap(cls, value: T, provenance: Any = None) -> Union[T, HasProvenance]:
        """
        Wrap a value with provenance tracking.

        This method automatically determines the appropriate wrapper type for
        the given value and creates a wrapped instance that behaves like the
        original type while tracking provenance.

        Args:
            value: Value to wrap (can be any Python type)
            provenance: Provenance information (Provenance, dict, list, or None)

        Returns:
            Wrapped value with provenance attribute. The return type depends on
            the input value's type.

        Examples:
            >>> # Wrap a string
            >>> wrapped_str = TypeWrapperFactory.wrap("hello", {"category": "defaults"})
            >>> isinstance(wrapped_str, str)  # True
            >>> wrapped_str.provenance.current.category  # 'defaults'
            >>>
            >>> # Wrap a boolean
            >>> wrapped_bool = TypeWrapperFactory.wrap(True, {"line": 42})
            >>> bool(wrapped_bool)  # True
            >>> wrapped_bool.provenance.current.line  # 42
            >>>
            >>> # Wrap an integer
            >>> wrapped_int = TypeWrapperFactory.wrap(123)
            >>> wrapped_int + 1  # 124 (result loses provenance)
            >>> wrapped_int.provenance  # Provenance([])
        """
        # Handle None before type checking (type(None) doesn't work well with isinstance)
        if value is None:
            return NoneWithProvenance(value, provenance)

        # Handle bool before other checks (bool is a subtype of int in Python)
        if isinstance(value, bool):
            return BoolWithProvenance(value, provenance)

        # Handle already wrapped values - update provenance if provided
        if isinstance(value, HasProvenance):
            if provenance is not None:
                if isinstance(provenance, Provenance):
                    value.provenance = provenance
                else:
                    value.provenance = Provenance(provenance)
            return value

        # Get the value's type
        value_type = type(value)

        # Check if we have a predefined wrapper for this type
        if value_type in cls._predefined_wrappers:
            wrapper_class = cls._predefined_wrappers[value_type]
            # Don't cache predefined wrappers since they're already in the dict
            return wrapper_class(value, provenance)

        # For other types, create or retrieve a dynamic wrapper class
        # This WILL cache the dynamically created class
        wrapper_class = cls._get_or_create_wrapper_class(value_type)
        return wrapper_class(value, provenance)

    @classmethod
    def _get_or_create_wrapper_class(cls, value_type: Type[T]) -> Type[T]:
        """
        Get cached wrapper class or create a new one.

        This method checks if a wrapper class for the given type already exists
        in the cache. If it does, it returns the cached class. If not, it creates
        a new wrapper class, caches it, and returns it.

        Args:
            value_type: The type to wrap

        Returns:
            Wrapper class that subclasses the given type and adds provenance

        Examples:
            >>> # First call creates the class
            >>> wrapper1 = TypeWrapperFactory._get_or_create_wrapper_class(str)
            >>> # Second call retrieves from cache
            >>> wrapper2 = TypeWrapperFactory._get_or_create_wrapper_class(str)
            >>> wrapper1 is wrapper2  # True
        """
        # Return cached class if available
        if value_type in cls._class_cache:
            return cls._class_cache[value_type]

        # Create new wrapper class
        wrapper_class = cls._create_wrapper_class(value_type)

        # Cache for future use
        cls._class_cache[value_type] = wrapper_class

        return wrapper_class

    @classmethod
    def _create_wrapper_class(cls, value_type: Type[T]) -> Type[T]:
        """
        Create a new wrapper class for the given type.

        This method dynamically creates a new class that:
        1. Subclasses the original type
        2. Mixes in ProvenanceMixin for provenance functionality
        3. Implements __new__ and __init__ methods

        Args:
            value_type: The type to wrap

        Returns:
            New wrapper class

        Examples:
            >>> MyStrWrapper = TypeWrapperFactory._create_wrapper_class(str)
            >>> obj = MyStrWrapper("hello", {"category": "defaults"})
            >>> isinstance(obj, str)  # True
            >>> hasattr(obj, "provenance")  # True
        """
        class_name = f"{value_type.__name__.capitalize()}WithProvenance"

        # Create the new wrapper class
        # Note: ProvenanceMixin must come first in MRO to ensure its methods
        # take precedence over the base type's methods
        wrapper_class = type(
            class_name,
            (value_type, ProvenanceMixin),
            {
                "__new__": cls._make_new_method(value_type),
                "__init__": cls._make_init_method(),
                "__module__": __name__,
            },
        )

        return wrapper_class

    @staticmethod
    def _make_new_method(value_type: Type[T]):
        """
        Create a __new__ method for the wrapper class.

        The __new__ method is responsible for creating the actual instance
        of the wrapped type. This is necessary for immutable types like
        str, int, and float.

        Args:
            value_type: The type being wrapped

        Returns:
            __new__ method for the wrapper class

        Examples:
            >>> new_method = TypeWrapperFactory._make_new_method(str)
            >>> # Used internally during class creation
        """

        def __new__(cls, value, provenance=None):
            """Create new instance of the wrapped type."""
            try:
                # Try to create instance with value
                instance = super(cls, cls).__new__(cls, value)
            except TypeError:
                # If that fails (e.g., for some custom types), try without value
                instance = super(cls, cls).__new__(cls)
            return instance

        return __new__

    @staticmethod
    def _make_init_method():
        """
        Create an __init__ method for the wrapper class.

        The __init__ method initializes the provenance tracking for the
        wrapped value.

        Returns:
            __init__ method for the wrapper class

        Examples:
            >>> init_method = TypeWrapperFactory._make_init_method()
            >>> # Used internally during class creation
        """

        def __init__(self, value, provenance=None):
            """Initialize the wrapped value with provenance."""
            # For objects, we need to copy their __dict__ to preserve attributes
            if hasattr(value, "__dict__"):
                for key, val in value.__dict__.items():
                    setattr(self, key, val)
            self.value = value
            self._init_provenance(provenance)

        return __init__

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the wrapper class cache.

        This method is primarily useful for testing or when you want to ensure
        fresh wrapper classes are created (e.g., after modifying the factory
        behavior).

        Examples:
            >>> TypeWrapperFactory.wrap("test")
            >>> len(TypeWrapperFactory._class_cache)  # >= 1
            >>> TypeWrapperFactory.clear_cache()
            >>> len(TypeWrapperFactory._class_cache)  # 0
        """
        cls._class_cache.clear()

    @classmethod
    def get_wrapper_class(cls, value_type: Type[T]) -> Type[T]:
        """
        Get the wrapper class for a given type without creating an instance.

        This is useful when you want to inspect or use the wrapper class directly
        rather than wrapping a specific value.

        Args:
            value_type: The type to get a wrapper for

        Returns:
            Wrapper class for the given type

        Examples:
            >>> StrWrapper = TypeWrapperFactory.get_wrapper_class(str)
            >>> obj = StrWrapper("hello", {"category": "defaults"})
            >>> isinstance(obj, str)  # True
        """
        # Handle special cases
        if value_type is type(None):
            return NoneWithProvenance
        if value_type is bool:
            return BoolWithProvenance

        # Check predefined wrappers
        if value_type in cls._predefined_wrappers:
            return cls._predefined_wrappers[value_type]

        # Get or create dynamic wrapper
        return cls._get_or_create_wrapper_class(value_type)

    @classmethod
    def is_wrapped(cls, value: Any) -> bool:
        """
        Check if a value is wrapped with provenance tracking.

        Args:
            value: Value to check

        Returns:
            True if the value has provenance tracking

        Examples:
            >>> wrapped = TypeWrapperFactory.wrap("hello")
            >>> TypeWrapperFactory.is_wrapped(wrapped)  # True
            >>> TypeWrapperFactory.is_wrapped("hello")  # False
        """
        return isinstance(value, HasProvenance)


# Convenience function for the factory
def wrap_with_provenance(value: T, provenance: Any = None) -> Union[T, HasProvenance]:
    """
    Convenience function to wrap a value with provenance tracking.

    This is a wrapper around TypeWrapperFactory.wrap for easier usage.

    Args:
        value: Value to wrap
        provenance: Provenance information

    Returns:
        Wrapped value with provenance tracking

    Examples:
        >>> wrapped = wrap_with_provenance("hello", {"category": "defaults"})
        >>> wrapped.provenance.current.category  # 'defaults'
    """
    return TypeWrapperFactory.wrap(value, provenance)
