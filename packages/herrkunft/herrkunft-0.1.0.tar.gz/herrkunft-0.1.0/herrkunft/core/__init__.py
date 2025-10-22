"""
Core provenance tracking functionality.

This module provides the fundamental classes and functions for tracking
configuration value provenance.
"""

from .decorators import (
    keep_provenance_in_recursive_function,
    preserve_provenance,
    track_provenance,
)
from .hierarchy import CategoryLevel, HierarchyConfig, HierarchyManager
from .provenance import Provenance, ProvenanceStep

__all__ = [
    # Provenance classes
    "Provenance",
    "ProvenanceStep",
    # Hierarchy management
    "CategoryLevel",
    "HierarchyConfig",
    "HierarchyManager",
    # Decorators
    "track_provenance",
    "keep_provenance_in_recursive_function",
    "preserve_provenance",
]
