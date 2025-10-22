"""
Concrete type wrapper implementations for common Python types.

This module provides wrapper classes for types that cannot be easily subclassed
(bool, NoneType) and serves as an example for implementing custom wrappers.
"""

from typing import Any

from herrkunft.types.base import ProvenanceMixin


class BoolWithProvenance(ProvenanceMixin):
    """
    Boolean value with provenance tracking.

    Since bool cannot be subclassed in Python, this class emulates bool behavior
    while adding provenance tracking. It implements the necessary methods to act
    like a boolean in most contexts.

    Note:
        isinstance(obj, bool) will return True due to __class__ property override.
        However, obj is bool will return False (identity check).

    Examples:
        >>> val = BoolWithProvenance(True, {"category": "defaults"})
        >>> bool(val)  # True
        >>> val == True  # True
        >>> if val: print("truthy")  # Works as expected
        >>> isinstance(val, bool)  # True
    """

    def __init__(self, value: bool, provenance: Any = None):
        """
        Initialize boolean with provenance.

        Args:
            value: The boolean value
            provenance: Provenance information

        Examples:
            >>> val = BoolWithProvenance(True, {"category": "defaults", "line": 10})
            >>> print(val.value)  # True
            >>> print(val.provenance.current.line)  # 10
        """
        self.value = value
        self._init_provenance(provenance)

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            String representation of the boolean value

        Examples:
            >>> val = BoolWithProvenance(True)
            >>> repr(val)
            'True'
        """
        return repr(self.value)

    def __str__(self) -> str:
        """
        String conversion.

        Returns:
            String representation of the boolean value

        Examples:
            >>> val = BoolWithProvenance(False)
            >>> str(val)
            'False'
        """
        return str(self.value)

    def __bool__(self) -> bool:
        """
        Boolean conversion.

        Returns:
            The wrapped boolean value

        Examples:
            >>> val = BoolWithProvenance(True)
            >>> bool(val)
            True
            >>> if val: print("yes")
            yes
        """
        return bool(self.value)

    def __eq__(self, other: Any) -> bool:
        """
        Equality comparison.

        Args:
            other: Value to compare with

        Returns:
            True if values are equal

        Examples:
            >>> val = BoolWithProvenance(True)
            >>> val == True  # True
            >>> val == False  # False
            >>> val == BoolWithProvenance(True)  # True
        """
        if isinstance(other, BoolWithProvenance):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other: Any) -> bool:
        """
        Inequality comparison.

        Args:
            other: Value to compare with

        Returns:
            True if values are not equal
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        Hash value.

        Returns:
            Hash of the wrapped boolean value

        Examples:
            >>> val = BoolWithProvenance(True)
            >>> hash(val) == hash(True)
            True
        """
        return hash(self.value)

    @property
    def __class__(self):
        """
        Override __class__ to make isinstance(obj, bool) return True.

        Returns:
            The bool class

        Examples:
            >>> val = BoolWithProvenance(True)
            >>> isinstance(val, bool)
            True
        """
        return bool


class NoneWithProvenance(ProvenanceMixin):
    """
    None value with provenance tracking.

    Since NoneType cannot be subclassed in Python, this class emulates None
    behavior while adding provenance tracking.

    Note:
        isinstance(obj, type(None)) will return True due to __class__ override.
        However, obj is None will return False (identity check).

    Examples:
        >>> val = NoneWithProvenance(None, {"category": "defaults"})
        >>> val == None  # True
        >>> bool(val)  # False
        >>> isinstance(val, type(None))  # True
    """

    def __init__(self, value: None = None, provenance: Any = None):
        """
        Initialize None with provenance.

        Args:
            value: Must be None
            provenance: Provenance information

        Examples:
            >>> val = NoneWithProvenance(None, {"category": "defaults"})
            >>> print(val.value)  # None
        """
        self.value = None
        self._init_provenance(provenance)

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            'None'

        Examples:
            >>> val = NoneWithProvenance()
            >>> repr(val)
            'None'
        """
        return "None"

    def __str__(self) -> str:
        """
        String conversion.

        Returns:
            'None'

        Examples:
            >>> val = NoneWithProvenance()
            >>> str(val)
            'None'
        """
        return "None"

    def __bool__(self) -> bool:
        """
        Boolean conversion.

        Returns:
            Always False (like None)

        Examples:
            >>> val = NoneWithProvenance()
            >>> bool(val)
            False
            >>> if not val: print("none")
            none
        """
        return False

    def __eq__(self, other: Any) -> bool:
        """
        Equality comparison.

        Args:
            other: Value to compare with

        Returns:
            True if other is None or NoneWithProvenance

        Examples:
            >>> val = NoneWithProvenance()
            >>> val == None  # True
            >>> val == 0  # False
            >>> val == NoneWithProvenance()  # True
        """
        if isinstance(other, NoneWithProvenance):
            return True
        return other is None

    def __ne__(self, other: Any) -> bool:
        """
        Inequality comparison.

        Args:
            other: Value to compare with

        Returns:
            True if other is not None or NoneWithProvenance
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        Hash value.

        Returns:
            Hash of None

        Examples:
            >>> val = NoneWithProvenance()
            >>> hash(val) == hash(None)
            True
        """
        return hash(None)

    @property
    def __class__(self):
        """
        Override __class__ to make isinstance(obj, type(None)) return True.

        Returns:
            The NoneType class

        Examples:
            >>> val = NoneWithProvenance()
            >>> isinstance(val, type(None))
            True
        """
        return type(None)


# String, int, float wrappers are created dynamically by the factory
# as they can be subclassed directly. These examples show how custom
# wrappers can be created if needed:


class StrWithProvenance(str, ProvenanceMixin):
    """
    String value with provenance tracking.

    This is a direct subclass of str that adds provenance. It's created
    automatically by the factory, but provided here as an example.

    Examples:
        >>> val = StrWithProvenance("hello", {"category": "defaults"})
        >>> val.upper()  # 'HELLO' (but without provenance)
        >>> val.provenance.current.category  # 'defaults'
    """

    def __new__(cls, value: str, provenance: Any = None):
        """
        Create new string instance.

        Args:
            value: The string value
            provenance: Provenance information

        Returns:
            New StrWithProvenance instance
        """
        return super().__new__(cls, value)

    def __init__(self, value: str, provenance: Any = None):
        """
        Initialize string with provenance.

        Args:
            value: The string value
            provenance: Provenance information
        """
        self.value = value
        self._init_provenance(provenance)


class IntWithProvenance(int, ProvenanceMixin):
    """
    Integer value with provenance tracking.

    This is a direct subclass of int that adds provenance. It's created
    automatically by the factory, but provided here as an example.

    Examples:
        >>> val = IntWithProvenance(42, {"category": "defaults"})
        >>> val + 1  # 43 (but without provenance)
        >>> val.provenance.current.category  # 'defaults'
    """

    def __new__(cls, value: int, provenance: Any = None):
        """
        Create new integer instance.

        Args:
            value: The integer value
            provenance: Provenance information

        Returns:
            New IntWithProvenance instance
        """
        return super().__new__(cls, value)

    def __init__(self, value: int, provenance: Any = None):
        """
        Initialize integer with provenance.

        Args:
            value: The integer value
            provenance: Provenance information
        """
        self.value = value
        self._init_provenance(provenance)


class FloatWithProvenance(float, ProvenanceMixin):
    """
    Float value with provenance tracking.

    This is a direct subclass of float that adds provenance. It's created
    automatically by the factory, but provided here as an example.

    Examples:
        >>> val = FloatWithProvenance(3.14, {"category": "defaults"})
        >>> val * 2  # 6.28 (but without provenance)
        >>> val.provenance.current.category  # 'defaults'
    """

    def __new__(cls, value: float, provenance: Any = None):
        """
        Create new float instance.

        Args:
            value: The float value
            provenance: Provenance information

        Returns:
            New FloatWithProvenance instance
        """
        return super().__new__(cls, value)

    def __init__(self, value: float, provenance: Any = None):
        """
        Initialize float with provenance.

        Args:
            value: The float value
            provenance: Provenance information
        """
        self.value = value
        self._init_provenance(provenance)
