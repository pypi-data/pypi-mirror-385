"""
YAML dumper with provenance comment support.

This module provides a YAML dumper that can write configuration data to YAML files,
optionally including provenance information as comments. This allows users to see
where each value originated from directly in the YAML file.
"""

from io import StringIO
from pathlib import Path
from typing import Any, TextIO, Union

from loguru import logger
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class ProvenanceDumper:
    """
    Dump dictionaries to YAML with provenance as comments.

    This dumper can write configuration data to YAML files while optionally
    preserving provenance information as inline comments. This makes it easy
    to track the origin of each value when reading the file.

    Examples:
        Basic usage with provenance comments:

        >>> dumper = ProvenanceDumper(include_provenance_comments=True)
        >>> config = load_yaml("input.yaml", category="defaults")
        >>> dumper.dump(config, "output.yaml")

        Dump without provenance (clean):

        >>> dumper = ProvenanceDumper(include_provenance_comments=False)
        >>> dumper.dump(config, "output.yaml", clean=True)

        Dump to string:

        >>> yaml_string = dumper.dumps(config)

    Attributes:
        include_comments: Whether to add provenance as comments
        yaml: ruamel.yaml YAML instance for dumping
    """

    def __init__(self, include_provenance_comments: bool = True):
        """
        Initialize dumper.

        Args:
            include_provenance_comments: Add provenance as YAML comments.
                When True, provenance information (file, line, category) will
                be added as comments in the output YAML.
        """
        self.include_comments = include_provenance_comments
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.width = 4096  # Avoid line wrapping

    def dump(
        self,
        data: Any,
        target: Union[Path, str, TextIO],
        clean: bool = False,
    ) -> None:
        """
        Dump dictionary to YAML file.

        This method writes the data to a YAML file, optionally including provenance
        information as comments. If clean=True, all provenance wrappers are removed
        before dumping.

        Args:
            data: Dictionary to dump (with or without provenance). Can be
                DictWithProvenance, regular dict, or any other structure.
            target: Output file path (as string or Path object) or file-like object.
            clean: Remove provenance wrappers before dumping. If True, the output
                will be plain Python types (dict, list, str, etc.) without any
                provenance tracking.

        Raises:
            IOError: If the file cannot be written

        Examples:
            >>> dumper = ProvenanceDumper()
            >>> dumper.dump({"key": "value"}, "output.yaml")
            >>>
            >>> # Dump without provenance wrappers
            >>> dumper.dump(config, "clean_output.yaml", clean=True)
            >>>
            >>> # Dump to file object
            >>> with open("output.yaml", "w") as f:
            ...     dumper.dump(config, f)
        """
        # Import here to avoid circular dependency
        from herrkunft.utils.cleaning import clean_provenance

        if clean:
            data = clean_provenance(data)

        # Add provenance comments if requested
        # We check if data has the necessary attributes for provenance tracking
        if self.include_comments and (
            self._has_provenance(data)
            or (isinstance(data, dict) and self._dict_has_wrapped_values(data))
        ):
            commented_data = self._add_provenance_comments(data)
        else:
            # If not adding comments, ensure data is in a format ruamel.yaml can handle
            commented_data = self._prepare_data_for_dump(data, clean)

        # Dump to file
        if isinstance(target, (str, Path)):
            target_path = Path(target)
            logger.debug(f"Dumping YAML to file: {target_path}")
            with target_path.open("w") as f:
                self.yaml.dump(commented_data, f)
        else:
            logger.debug("Dumping YAML to stream")
            self.yaml.dump(commented_data, target)

    def dumps(
        self,
        data: Any,
        clean: bool = False,
    ) -> str:
        """
        Dump dictionary to YAML string.

        This method returns the YAML representation as a string rather than
        writing to a file.

        Args:
            data: Dictionary to dump (with or without provenance)
            clean: Remove provenance wrappers before dumping

        Returns:
            YAML string representation of the data

        Examples:
            >>> dumper = ProvenanceDumper()
            >>> yaml_str = dumper.dumps({"database": {"host": "localhost"}})
            >>> print(yaml_str)
            database:
              host: localhost
        """
        stream = StringIO()
        self.dump(data, stream, clean=clean)
        return stream.getvalue()

    def _has_provenance(self, data: Any) -> bool:
        """
        Check if data structure has provenance tracking.

        Args:
            data: Data to check

        Returns:
            True if data appears to have provenance tracking
        """
        # Check if it's a DictWithProvenance or ListWithProvenance
        # We can't import these directly due to potential circular dependencies,
        # so we check for the characteristic methods
        if isinstance(data, dict):
            # Check if it's a DictWithProvenance by looking for characteristic methods
            return (
                hasattr(data, "get_provenance")
                or hasattr(data, "set_provenance")
                or hasattr(data, "_hierarchy")
            )
        elif isinstance(data, list):
            # Check if it's a ListWithProvenance
            return (
                hasattr(data, "get_provenance")
                or hasattr(data, "set_provenance")
                or hasattr(data, "_hierarchy")
            )
        return False

    def _dict_has_wrapped_values(self, data: dict) -> bool:
        """
        Check if a plain dict has any values with provenance.

        Args:
            data: Dictionary to check

        Returns:
            True if any values have provenance
        """
        for value in data.values():
            if hasattr(value, "provenance") and value.provenance:
                return True
            if isinstance(value, dict):
                if self._dict_has_wrapped_values(value):
                    return True
        return False

    def _prepare_data_for_dump(self, data: Any, clean: bool) -> Any:
        """
        Prepare data for dumping without provenance comments.

        This method ensures the data is in a format that ruamel.yaml can handle,
        cleaning provenance wrappers if necessary.

        Args:
            data: Data to prepare
            clean: Whether to clean provenance wrappers

        Returns:
            Data ready for dumping
        """
        from herrkunft.utils.cleaning import clean_provenance

        if clean:
            return clean_provenance(data)

        # If data is a dict or list, recursively clean any wrapped values
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Clean wrapped values
                if hasattr(value, "value"):
                    result[key] = value.value
                elif isinstance(value, (dict, list)):
                    result[key] = self._prepare_data_for_dump(value, False)
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            result = []
            for item in data:
                if hasattr(item, "value"):
                    result.append(item.value)
                elif isinstance(item, (dict, list)):
                    result.append(self._prepare_data_for_dump(item, False))
                else:
                    result.append(item)
            return result

        return data

    def _add_provenance_comments(self, data: Any) -> CommentedMap:
        """
        Add provenance information as YAML comments.

        This method creates a CommentedMap structure that includes provenance
        information as comments before each key. The format is:
        # from: /path/to/file.yaml | line: 5 | category: defaults

        Args:
            data: Dictionary with provenance tracking (DictWithProvenance)

        Returns:
            CommentedMap with provenance comments attached

        Examples:
            >>> # Input: DictWithProvenance({"key": "value"})
            >>> # Output: CommentedMap with comment:
            >>> # # from: config.yaml | line: 3 | category: defaults
            >>> # key: value
        """
        from herrkunft.utils.cleaning import clean_provenance

        commented = CommentedMap()

        for key, value in data.items():
            # Get provenance for this value
            if hasattr(value, "provenance") and value.provenance:
                prov = value.provenance.current
                if prov:
                    # Format provenance comment
                    comment_parts = []

                    if prov.yaml_file:
                        # Show just the filename if it's a path
                        file_name = Path(prov.yaml_file).name
                        comment_parts.append(f"from: {file_name}")

                    if prov.line is not None:
                        comment_parts.append(f"line: {prov.line}")

                    if prov.col is not None:
                        comment_parts.append(f"col: {prov.col}")

                    if prov.category:
                        comment_parts.append(f"category: {prov.category}")

                    if prov.subcategory:
                        comment_parts.append(f"subcategory: {prov.subcategory}")

                    if comment_parts:
                        comment = " | ".join(comment_parts)
                        # Add comment before the key
                        commented.yaml_set_comment_before_after_key(
                            key, before=f" {comment}"
                        )

            # Recursively process nested structures
            if isinstance(value, dict) and (
                self._has_provenance(value) or self._dict_has_wrapped_values(value)
            ):
                commented[key] = self._add_provenance_comments(value)
            elif isinstance(value, list) and self._has_provenance(value):
                commented[key] = self._add_list_comments(value)
            else:
                # Clean the value of provenance wrapper
                commented[key] = clean_provenance(value)

        return commented

    def _add_list_comments(self, data: Any) -> CommentedSeq:
        """
        Add provenance comments to list elements.

        For lists, we create a CommentedSeq and add comments for elements
        where provenance information is available.

        Args:
            data: List with provenance tracking (ListWithProvenance)

        Returns:
            CommentedSeq with provenance comments

        Examples:
            >>> # For list elements with provenance, comments are added:
            >>> # - item1  # from: config.yaml | line: 5
            >>> # - item2  # from: config.yaml | line: 6
        """
        from herrkunft.utils.cleaning import clean_provenance

        commented = CommentedSeq()

        for idx, elem in enumerate(data):
            # Handle nested dictionaries
            if self._has_provenance(elem) and isinstance(elem, dict):
                commented.append(self._add_provenance_comments(elem))
            # Handle nested lists
            elif self._has_provenance(elem) and isinstance(elem, list):
                commented.append(self._add_list_comments(elem))
            else:
                # Add the cleaned element
                cleaned_elem = clean_provenance(elem)
                commented.append(cleaned_elem)

                # Try to add provenance comment for this element
                if hasattr(elem, "provenance") and elem.provenance:
                    prov = elem.provenance.current
                    if prov:
                        comment_parts = []
                        if prov.yaml_file:
                            file_name = Path(prov.yaml_file).name
                            comment_parts.append(f"from: {file_name}")
                        if prov.line is not None:
                            comment_parts.append(f"line: {prov.line}")
                        if prov.category:
                            comment_parts.append(f"category: {prov.category}")

                        if comment_parts:
                            comment = " | ".join(comment_parts)
                            # Add end-of-line comment for this element
                            commented.yaml_add_eol_comment(comment, idx)

        return commented
