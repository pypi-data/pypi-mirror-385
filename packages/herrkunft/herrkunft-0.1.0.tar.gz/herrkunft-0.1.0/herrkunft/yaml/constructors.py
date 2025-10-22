"""
Custom YAML constructors for provenance injection.

This module provides custom YAML constructors that can be used with ruamel.yaml
to add special handling for environment variables and other custom tags.
"""

from __future__ import annotations

import os
import re
from typing import Any

from loguru import logger
from ruamel.yaml import RoundTripConstructor
from ruamel.yaml.nodes import ScalarNode


class EnvironmentConstructor(RoundTripConstructor):
    """
    YAML constructor that handles !ENV tags for environment variable substitution.

    This constructor allows you to reference environment variables in YAML files
    using the !ENV tag. For example:
        database_url: !ENV ${DATABASE_URL}

    The constructor will replace ${DATABASE_URL} with the value of the
    DATABASE_URL environment variable.

    Attributes:
        env_variables: List of (var_name, resolved_value) tuples for all
            environment variables that were resolved during loading.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the constructor with empty env_variables list."""
        super().__init__(*args, **kwargs)
        self.env_variables: list[tuple[str, str]] = []

    def construct_scalar(self, node: Any) -> Any:
        """
        Construct scalar values with !ENV tag support.

        This method is called by ruamel.yaml when constructing scalar nodes.
        If the node has an !ENV tag, it will substitute environment variables.

        Args:
            node: YAML node being constructed

        Returns:
            Constructed value (with env vars substituted if !ENV tag present)

        Raises:
            ValueError: If !ENV tag is used but no ${VAR} pattern found
            EnvironmentError: If referenced environment variable doesn't exist
        """
        # Pattern for ${VAR} syntax
        pattern_envvar = re.compile(r"\$\{(\w+)\}")

        if isinstance(node, ScalarNode) and node.tag == "!ENV":
            env_variable = node.value
            envvar_matches = pattern_envvar.findall(env_variable)

            if envvar_matches:
                full_value = env_variable
                for env_var in envvar_matches:
                    # Check if variable exists in environment
                    if env_var not in os.environ:
                        raise OSError(
                            f"Environment variable '{env_var}' not found. "
                            f"Required in: {env_variable}"
                        )

                    # Replace ${VAR} with actual value
                    env_value = os.getenv(env_var)
                    full_value = full_value.replace(f"${{{env_var}}}", env_value)

                # Track which env vars were used
                self.env_variables.append((env_var, full_value))
                return full_value
            else:
                raise ValueError(
                    f"!ENV tag used but no ${{VAR}} pattern found in: {env_variable}"
                )

        # For non-!ENV nodes, use default construction
        return super().construct_scalar(node)


class ProvenanceConstructor(EnvironmentConstructor):
    """
    YAML constructor that extracts provenance information for every value.

    This constructor extends EnvironmentConstructor to also capture line and
    column information for every constructed value. It returns tuples of
    (value, provenance) instead of just values.

    The provenance tuple contains:
        - line: Line number (0-indexed from ruamel, will be adjusted)
        - col: Column number (0-indexed from ruamel, will be adjusted)

    This is used internally by the loader to build the provenance dictionary.
    """

    def construct_object(
        self, node: Any, *args, **kwargs
    ) -> tuple[Any, tuple[int, int]]:
        """
        Construct object and extract provenance information.

        This method overrides the base construct_object to wrap every value
        with its provenance information (line and column).

        Args:
            node: YAML node containing data and position information
            *args: Additional positional arguments for parent constructor
            **kwargs: Additional keyword arguments for parent constructor

        Returns:
            Tuple of (data, provenance) where:
                - data: The actual value from the YAML file
                - provenance: Tuple of (line, col) for the value
        """
        # Construct the actual data using parent class
        data = super().construct_object(node, *args, **kwargs)

        # Extract position information
        # ruamel uses 0-indexed line/col, we'll store them as-is
        # and adjust to 1-indexed later in the loader
        provenance = (
            node.start_mark.line,
            node.start_mark.column,
        )

        return (data, provenance)


def create_env_loader(loader_class=None):
    """
    Create a YAML loader class with environment variable support.

    This function creates a custom YAML loader that can handle !ENV tags
    for environment variable substitution. This is useful for loading
    configuration files that reference environment variables.

    Args:
        loader_class: Base loader class to extend (default: yaml.SafeLoader)

    Returns:
        A YAML loader class with !ENV tag support

    Examples:
        >>> import yaml
        >>> from herrkunft.yaml.constructors import create_env_loader
        >>> EnvLoader = create_env_loader()
        >>> with open('config.yaml') as f:
        ...     config = yaml.load(f, Loader=EnvLoader)

    Note:
        This is provided for compatibility with PyYAML. For provenance
        tracking, use ProvenanceLoader instead.
    """
    import yaml

    if loader_class is None:
        loader_class = yaml.SafeLoader

    # Pattern for ${VAR} syntax
    pattern_envvar = re.compile(r"\$\{(\w+)\}")

    # Pattern for valid !ENV lines (uncommented)
    pattern_envtag = re.compile(r"""^[^\#]*\!ENV[ \t]+['|"]?\$\{\w+\}['|"]?""")

    # Add implicit resolver for ${VAR} pattern
    loader_class.add_implicit_resolver("!ENV", pattern_envvar, None)

    # Track resolved environment variables
    loader_class.env_variables = []

    def constructor_env_variables(loader, node):
        """
        Construct environment variable values.

        This function is registered as the constructor for !ENV tags.
        It extracts environment variables from the YAML value and replaces
        them with their actual values.

        Args:
            loader: YAML loader instance
            node: YAML node to construct

        Returns:
            String with environment variables substituted
        """
        # Get file information for error messages
        fname = node.start_mark.name
        line_num = node.start_mark.line + 1
        column_start = node.start_mark.column
        column_end = node.end_mark.column

        # Read the line containing the !ENV tag
        try:
            with open(fname) as yaml_file:
                file_lines = yaml_file.readlines()
                cur_line = file_lines[line_num - 1].rstrip()
        except (OSError, IndexError):
            cur_line = ""

        # Log debug info if requested
        if os.getenv("ESM_PARSER_DEBUG"):
            logger.debug("=" * 60)
            logger.debug(f"Reading file: {fname}")
            logger.debug(f"Reading line: {cur_line}")
            logger.debug(f"Match: {cur_line[column_start:column_end]}")
            logger.debug("=" * 60)

        # Construct the scalar value
        value = loader.construct_scalar(node)

        # Check if line has valid !ENV tag
        envtag_match = re.search(pattern_envtag, cur_line)

        # Find all ${VAR} patterns
        envvar_matches = pattern_envvar.findall(value)

        # Only substitute if valid !ENV tag present
        if envtag_match and envvar_matches:
            full_value = value
            for env_var in envvar_matches:
                # Check if variable exists
                if not os.getenv(env_var):
                    raise OSError(
                        f"Environment variable '{env_var}' is not defined. "
                        f"Required in {fname}:{line_num}"
                    )

                # Substitute the value
                full_value = full_value.replace(f"${{{env_var}}}", os.getenv(env_var))
                loader.env_variables.append((env_var, full_value))

            return full_value

        return value

    # Register the constructor
    loader_class.add_constructor("!ENV", constructor_env_variables)

    return loader_class


def check_duplicates(yaml_file):
    """
    Check for duplicate keys in a YAML file.

    This function reads a YAML file and checks for duplicate keys at any level
    of the document. If duplicates are found, it raises an error with information
    about where the duplicates are located.

    Args:
        yaml_file: File object or path to YAML file

    Raises:
        KeyError: If duplicate keys are found, with details about locations

    Examples:
        >>> with open('config.yaml') as f:
        ...     check_duplicates(f)  # Raises error if duplicates found
    """
    import yaml

    class PreserveDuplicatesLoader(yaml.loader.Loader):
        """Custom loader that detects duplicate keys."""

        pass

    def map_constructor(loader, node, deep=False):
        """
        Construct mapping and check for duplicates.

        Args:
            loader: YAML loader instance
            node: Mapping node being constructed
            deep: Whether to do deep construction

        Returns:
            Constructed mapping

        Raises:
            KeyError: If duplicate keys found
        """
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            value = loader.construct_object(value_node, deep=deep)

            # Get position information
            file = str(key_node.start_mark.name)
            line = key_node.start_mark.line + 1
            col = key_node.start_mark.column + 1

            if key in mapping:
                old_info = mapping[key]
                raise KeyError(
                    f"Duplicate key '{key}' found in {file}:\n"
                    f"  First occurrence: line {old_info['line']}, col {old_info['col']}\n"
                    f"  Second occurrence: line {line}, col {col}"
                )

            mapping[key] = {"key": key, "file": file, "line": line, "col": col}

        return loader.construct_mapping(node, deep)

    # Add the constructor
    PreserveDuplicatesLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, map_constructor
    )

    # Create env loader with duplicate checking
    new_loader = create_env_loader(loader_class=PreserveDuplicatesLoader)

    # Load and check
    return yaml.load(yaml_file, Loader=new_loader)
