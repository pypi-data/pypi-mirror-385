"""
Type wrapper system for provenance tracking.

This module provides the complete type wrapper system that allows transparently
adding provenance tracking to Python's native types while preserving their
original behavior.

The type wrapper system consists of:
1. Base classes and protocols (base.py)
2. Concrete wrapper implementations (wrappers.py)
3. Factory for dynamic wrapper creation (factory.py)

Usage:
    >>> from herrkunft.types import wrap_with_provenance
    >>> wrapped = wrap_with_provenance("hello", {"category": "defaults"})
    >>> print(wrapped.provenance.current.category)  # 'defaults'
    >>> isinstance(wrapped, str)  # True
"""

from herrkunft.types.base import (
    HasProvenance,
    ProvenanceMixin,
    ProvenanceWrapper,
)
from herrkunft.types.factory import (
    TypeWrapperFactory,
    wrap_with_provenance,
)
from herrkunft.types.mappings import (
    DictWithProvenance,
    ListWithProvenance,
)
from herrkunft.types.wrappers import (
    BoolWithProvenance,
    FloatWithProvenance,
    IntWithProvenance,
    NoneWithProvenance,
    StrWithProvenance,
)

__all__ = [
    # Protocols and base classes
    "HasProvenance",
    "ProvenanceMixin",
    "ProvenanceWrapper",
    # Concrete wrapper classes
    "BoolWithProvenance",
    "NoneWithProvenance",
    "StrWithProvenance",
    "IntWithProvenance",
    "FloatWithProvenance",
    # Mapping types
    "DictWithProvenance",
    "ListWithProvenance",
    # Factory
    "TypeWrapperFactory",
    "wrap_with_provenance",
]
