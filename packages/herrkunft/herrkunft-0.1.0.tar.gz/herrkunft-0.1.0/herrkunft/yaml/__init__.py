"""
YAML loading and processing with automatic provenance tracking.

This module provides utilities for loading YAML files while automatically
tracking the origin of every value (file, line, column). It integrates with
the provenance library's core types to enable transparent value origin tracking.

Main Classes:
    ProvenanceLoader: Load YAML files with automatic provenance extraction

Utilities:
    validate_provenance_structure: Validate provenance matches data structure
    get_provenance_for_key: Get provenance for a specific nested key
    format_provenance_for_display: Format provenance as human-readable string

Constructors:
    EnvironmentConstructor: YAML constructor for !ENV tag support
    ProvenanceConstructor: YAML constructor that extracts provenance
    create_env_loader: Create PyYAML loader with environment variable support
    check_duplicates: Check YAML files for duplicate keys

Examples:
    Basic YAML loading with provenance:

    >>> from herrkunft.yaml import ProvenanceLoader
    >>> loader = ProvenanceLoader(category="components", subcategory="fesom")
    >>> data, prov = loader.load("config.yaml")
    >>> print(data["database"]["host"])
    localhost
    >>> print(prov["database"]["host"]["line"])
    3

    Loading multiple files:

    >>> loader = ProvenanceLoader()
    >>> results = loader.load_multiple([
    ...     ("defaults.yaml", "defaults"),
    ...     ("prod.yaml", "environment", "production")
    ... ])

    Using environment variables in YAML:

    >>> # In config.yaml:
    >>> # database_url: !ENV ${DATABASE_URL}
    >>> data, prov = loader.load("config.yaml")
    >>> # ${DATABASE_URL} will be replaced with env var value
"""

from .constructors import (
    EnvironmentConstructor,
    ProvenanceConstructor,
    check_duplicates,
    create_env_loader,
)
from .dumper import ProvenanceDumper
from .loader import ProvenanceLoader
from .utils import (
    create_minimal_provenance,
    extract_file_list_from_provenance,
    filter_provenance_by_category,
    format_provenance_for_display,
    get_provenance_for_key,
    merge_provenance_dicts,
    sanitize_yaml_value,
    validate_provenance_structure,
)

__all__ = [
    # Main loader/dumper
    "ProvenanceLoader",
    "ProvenanceDumper",
    # Constructors
    "EnvironmentConstructor",
    "ProvenanceConstructor",
    "create_env_loader",
    "check_duplicates",
    # Utilities
    "validate_provenance_structure",
    "get_provenance_for_key",
    "merge_provenance_dicts",
    "filter_provenance_by_category",
    "format_provenance_for_display",
    "extract_file_list_from_provenance",
    "sanitize_yaml_value",
    "create_minimal_provenance",
]
