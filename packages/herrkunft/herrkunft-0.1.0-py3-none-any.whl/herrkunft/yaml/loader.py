"""
YAML loader with automatic provenance tracking.

This module provides a YAML loader that automatically tracks the origin of every
value loaded from YAML files, including file path, line number, and column number.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Optional, TextIO, Union

from loguru import logger
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class ProvenanceLoader:
    """
    Load YAML files with automatic provenance tracking.

    This loader uses ruamel.yaml to preserve line and column information for every
    value in the YAML file. The provenance information is structured to match the
    data structure, making it easy to track where each value originated.

    Examples:
        Basic usage:

        >>> loader = ProvenanceLoader(category="components", subcategory="fesom")
        >>> result = loader.load("config.yaml")
        >>> # result is a tuple: (data_dict, provenance_dict)

        Loading multiple files:

        >>> loader = ProvenanceLoader()
        >>> configs = loader.load_multiple([
        ...     ("defaults.yaml", "defaults", None),
        ...     ("prod.yaml", "environment", "production")
        ... ])

    Attributes:
        category: Default category for loaded values (e.g., "components", "setups")
        subcategory: Default subcategory for loaded values (e.g., "fesom", "awicm")
    """

    def __init__(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
    ):
        """
        Initialize the provenance loader.

        Args:
            category: Default category for all loaded values. Common categories
                include: 'defaults', 'machines', 'components', 'setups',
                'runscript', 'command_line'
            subcategory: Default subcategory identifier (e.g., specific machine
                name or component name)
        """
        self.category = category
        self.subcategory = subcategory
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        # Allow wide output to avoid line wrapping
        self.yaml.width = 4096
        # Register custom constructors
        self._register_env_constructor()

    def _register_env_constructor(self):
        """
        Register custom constructor for !ENV tags to support environment variables.

        This allows YAML files to use syntax like:
            database_url: !ENV ${DATABASE_URL}

        The constructor will substitute environment variables at load time.
        """
        pattern_envvar = re.compile(r"\$\{(\w+)\}")

        def env_constructor(loader, node):
            """Construct environment variable values."""
            value = loader.construct_scalar(node)

            # Find all ${VAR} patterns
            envvar_matches = pattern_envvar.findall(value)

            if envvar_matches:
                full_value = value
                for env_var in envvar_matches:
                    # Check if variable exists
                    if env_var not in os.environ:
                        raise EnvironmentError(
                            f"Environment variable '{env_var}' not found. "
                            f"Required in: {value}"
                        )

                    # Substitute the value
                    env_value = os.getenv(env_var)
                    full_value = full_value.replace(f"${{{env_var}}}", env_value)

                return full_value

            return value

        # Register the constructor with the YAML instance
        self.yaml.constructor.add_constructor('!ENV', env_constructor)

    def load(
        self,
        source: Union[str, Path, TextIO],
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        return_tuple: bool = False,
    ):
        """
        Load YAML file with provenance tracking.

        This method loads a YAML file and creates a DictWithProvenance that
        integrates data and provenance tracking seamlessly.

        Args:
            source: File path (as string or Path object) or file-like object
            category: Category for this file (overrides default)
            subcategory: Subcategory for this file (overrides default)
            return_tuple: If True, return (data, provenance) tuple for backward
                compatibility. If False (default), return DictWithProvenance.

        Returns:
            DictWithProvenance with integrated provenance tracking, or
            tuple of (data_dict, provenance_dict) if return_tuple=True

        Raises:
            FileNotFoundError: If source is a path and file doesn't exist
            yaml.YAMLError: If YAML file is malformed

        Examples:
            >>> loader = ProvenanceLoader()
            >>> config = loader.load("config.yaml", category="defaults")
            >>> print(config["database"]["host"])
            localhost
            >>> print(config["database"]["host"].provenance.current.line)
            3
        """
        # Import here to avoid circular dependency
        from herrkunft.types.mappings import DictWithProvenance

        category = category or self.category
        subcategory = subcategory or self.subcategory

        # Load YAML with ruamel to preserve structure info
        if isinstance(source, (str, Path)):
            yaml_path = Path(source)
            if not yaml_path.exists():
                raise FileNotFoundError(f"YAML file not found: {yaml_path}")

            with yaml_path.open("r") as f:
                data = self.yaml.load(f)
            file_path = str(yaml_path.absolute())
        else:
            data = self.yaml.load(source)
            file_path = getattr(source, "name", "<stream>")

        # Handle empty files
        if data is None:
            logger.warning(f"YAML file is empty: {file_path}")
            if return_tuple:
                return {}, {}
            else:
                return DictWithProvenance({}, {})

        # Extract provenance from YAML structure
        provenance = self._extract_provenance(data, file_path, category, subcategory)

        # Convert CommentedMap to regular dict for data
        clean_data = self._clean_commented_data(data)

        # Return based on preference
        if return_tuple:
            return clean_data, provenance
        else:
            return DictWithProvenance(clean_data, provenance)

    def _clean_commented_data(self, node: Any) -> Any:
        """
        Convert CommentedMap/CommentedSeq to regular dict/list.

        Args:
            node: Node from ruamel.yaml (may be CommentedMap, CommentedSeq, or scalar)

        Returns:
            Regular Python dict, list, or scalar value
        """
        if isinstance(node, CommentedMap):
            return {
                key: self._clean_commented_data(value) for key, value in node.items()
            }
        elif isinstance(node, CommentedSeq):
            return [self._clean_commented_data(item) for item in node]
        else:
            return node

    def _extract_provenance(
        self,
        node: Any,
        file_path: str,
        category: Optional[str],
        subcategory: Optional[str],
    ) -> Union[dict[str, Any], list[Any], dict[str, Any]]:
        """
        Recursively extract provenance from YAML structure.

        This method traverses the YAML structure and creates a matching provenance
        structure. For each value, it captures:
        - file: Source file path
        - line: Line number (1-indexed)
        - col: Column number (1-indexed)
        - category: Configuration category
        - subcategory: Configuration subcategory

        Args:
            node: YAML node from ruamel.yaml (CommentedMap, CommentedSeq, or scalar)
            file_path: Absolute path to source YAML file
            category: Configuration category
            subcategory: Configuration subcategory

        Returns:
            Provenance structure matching the node structure:
            - For dicts: dict with same keys, provenance values
            - For lists: list of provenance values
            - For scalars: dict with provenance fields
        """
        if isinstance(node, CommentedMap):
            result = {}
            for key, value in node.items():
                # Get line/column info for the VALUE (not the key)
                # ruamel stores this in lc.data
                lc_data = node.lc.data.get(key)
                if lc_data:
                    # lc_data is ((key_line, key_col), (val_line, val_col), ...)
                    # We want the value position
                    line, col = lc_data[2] + 1, lc_data[3] + 1
                else:
                    line, col = None, None

                # Recursively process nested structures
                if isinstance(value, (CommentedMap, CommentedSeq)):
                    result[key] = self._extract_provenance(
                        value, file_path, category, subcategory
                    )
                else:
                    # Create provenance for leaf value
                    result[key] = {
                        "yaml_file": file_path,
                        "line": line,
                        "col": col,
                        "category": category,
                        "subcategory": subcategory,
                    }
            return result

        elif isinstance(node, CommentedSeq):
            result = []
            for idx, value in enumerate(node):
                # Get line/column for list element
                lc_data = node.lc.data.get(idx)
                if lc_data:
                    line, col = lc_data[0] + 1, lc_data[1] + 1
                else:
                    line, col = None, None

                if isinstance(value, (CommentedMap, CommentedSeq)):
                    result.append(
                        self._extract_provenance(
                            value, file_path, category, subcategory
                        )
                    )
                else:
                    result.append(
                        {
                            "yaml_file": file_path,
                            "line": line,
                            "col": col,
                            "category": category,
                            "subcategory": subcategory,
                        }
                    )
            return result

        else:
            # Scalar value without position info
            return {
                "yaml_file": file_path,
                "line": None,
                "col": None,
                "category": category,
                "subcategory": subcategory,
            }

    def load_multiple(
        self,
        files: list[tuple],
        return_tuple: bool = False,
    ) -> List:
        """
        Load multiple YAML files.

        This method loads multiple YAML files, each with their own category and
        subcategory. The files are NOT merged - each is returned separately.
        Use DictWithProvenance.update() to merge them with hierarchy resolution.

        Args:
            files: List of tuples, where each tuple is:
                - (path, category) or
                - (path, category, subcategory)
            return_tuple: If True, return list of (data, provenance) tuples for
                backward compatibility. If False (default), return list of
                DictWithProvenance objects.

        Returns:
            List of DictWithProvenance objects, or list of (data, prov) tuples
            if return_tuple=True

        Examples:
            >>> loader = ProvenanceLoader()
            >>> configs = loader.load_multiple([
            ...     ("defaults.yaml", "defaults"),
            ...     ("machine.yaml", "machines", "levante"),
            ...     ("component.yaml", "components", "fesom"),
            ... ])
            >>> # configs is a list of DictWithProvenance objects
            >>> for config in configs:
            ...     print(config.keys())

        Raises:
            ValueError: If tuple format is invalid
        """
        results = []

        for file_info in files:
            if len(file_info) == 2:
                path, cat = file_info
                subcat = None
            elif len(file_info) == 3:
                path, cat, subcat = file_info
            else:
                raise ValueError(
                    f"Invalid file info tuple: {file_info}. "
                    "Expected (path, category) or (path, category, subcategory)"
                )

            result = self.load(
                path, category=cat, subcategory=subcat, return_tuple=return_tuple
            )
            results.append(result)

        return results
