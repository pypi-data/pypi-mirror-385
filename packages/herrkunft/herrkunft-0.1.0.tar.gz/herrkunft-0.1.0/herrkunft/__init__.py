"""
herrkunft - Track configuration value origins and modification history.

From German "Herkunft" (origin, provenance) - this library provides transparent
tracking of configuration value origins and modification history through YAML
parsing with modern Python best practices.

Basic usage:
    >>> from herrkunft import load_yaml
    >>> config = load_yaml("config.yaml", category="defaults")
    >>> print(config["database"]["url"])
    >>> print(config["database"]["url"].provenance.current)

See the documentation for more advanced usage and features.

Authors:
    Paul Gierz <paul.gierz@awi.de>
    Miguel Andrés-Martínez <miguel.andres-martinez@awi.de>
"""

# Configuration
from .config import ProvenanceSettings, get_settings, reset_settings, settings
from .core.hierarchy import CategoryLevel, HierarchyConfig, HierarchyManager

# Core imports - all implemented by Expert 1
from .core.provenance import Provenance, ProvenanceStep
from .exceptions import (
    CategoryConflictError,
    ChooseConflictError,
    ConfigurationError,
    DumperError,
    LoaderError,
    ProvenanceError,
    SerializationError,
    ValidationError,
)

# Type system imports - implemented by Expert 2
from .types.base import HasProvenance
from .types.factory import TypeWrapperFactory as ProvenanceWrapperFactory
from .types.mappings import DictWithProvenance, ListWithProvenance

# Utilities
from .utils import (
    # Cleaning
    clean_provenance,
    ensure_provenance_valid,
    extract_provenance_tree,
    from_dict,
    from_json,
    from_json_file,
    strip_provenance,
    # Serialization
    to_dict,
    to_json,
    to_json_file,
    validate_provenance_history,
    # Validation
    validate_provenance_step,
    validate_provenance_tree,
)
from .version import __api_version__, __version__, __version_info__
from .yaml.dumper import ProvenanceDumper

# YAML handling imports - implemented by Expert 3
from .yaml.loader import ProvenanceLoader


# Convenience functions for common operations
def load_yaml(
    path: str,
    category: str = None,
    subcategory: str = None,
) -> DictWithProvenance:
    """
    Load YAML file with provenance tracking.

    This is a convenience function that creates a ProvenanceLoader
    and loads a single file.

    Args:
        path: Path to YAML file
        category: Configuration category for hierarchy resolution
        subcategory: Optional subcategory identifier

    Returns:
        Dictionary with provenance tracking enabled

    Example:
        >>> config = load_yaml("config.yaml", category="defaults")
        >>> print(config["key"].provenance.current.yaml_file)
    """
    loader = ProvenanceLoader(category=category, subcategory=subcategory)
    return loader.load(path)


def dump_yaml(
    data: dict,
    path: str,
    include_provenance: bool = True,
    clean: bool = False,
) -> None:
    """
    Dump dictionary to YAML file.

    This is a convenience function that creates a ProvenanceDumper
    and dumps a single file.

    Args:
        data: Dictionary to dump
        path: Output file path
        include_provenance: Add provenance as comments
        clean: Remove provenance wrappers before dumping

    Example:
        >>> dump_yaml(config, "output.yaml", include_provenance=True)
    """
    dumper = ProvenanceDumper(include_provenance_comments=include_provenance)
    dumper.dump(data, path, clean=clean)


# Public API - what users should import
__all__ = [
    # Version info
    "__version__",
    "__version_info__",
    "__api_version__",
    # Core classes (from Expert 1)
    "Provenance",
    "ProvenanceStep",
    "HierarchyManager",
    "HierarchyConfig",
    "CategoryLevel",
    # Type wrappers (from Expert 2)
    "DictWithProvenance",
    "ListWithProvenance",
    "ProvenanceWrapperFactory",
    "HasProvenance",
    # YAML handling (from Expert 3)
    "ProvenanceLoader",
    "ProvenanceDumper",
    # Convenience functions
    "load_yaml",
    "dump_yaml",
    # Configuration (from Expert 4)
    "ProvenanceSettings",
    "settings",
    "get_settings",
    "reset_settings",
    # Utilities (from Expert 4)
    "clean_provenance",
    "strip_provenance",
    "extract_provenance_tree",
    "validate_provenance_step",
    "validate_provenance_history",
    "validate_provenance_tree",
    "ensure_provenance_valid",
    "to_dict",
    "to_json",
    "to_json_file",
    "from_dict",
    "from_json",
    "from_json_file",
    # Exceptions
    "ProvenanceError",
    "CategoryConflictError",
    "ChooseConflictError",
    "ValidationError",
    "SerializationError",
    "ConfigurationError",
    "LoaderError",
    "DumperError",
]
