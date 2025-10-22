"""Custom exception classes for the provenance library."""

from typing import Any, Optional


class ProvenanceError(Exception):
    """Base exception class for all provenance-related errors."""

    pass


class CategoryConflictError(ProvenanceError):
    """
    Raised when conflicting values are set at the same category level.

    This error indicates that two different values are being set for the same key
    at the same hierarchy level, which requires explicit resolution.

    Attributes:
        key: The configuration key with the conflict
        category: The category level where the conflict occurred
        old_step: The provenance step of the existing value
        new_step: The provenance step of the new conflicting value
    """

    def __init__(
        self,
        key: str,
        category: Optional[str],
        old_step: Any,
        new_step: Any,
        message: Optional[str] = None,
    ) -> None:
        """
        Initialize category conflict error.

        Args:
            key: Configuration key with conflict
            category: Category level of conflict
            old_step: Provenance step of existing value
            new_step: Provenance step of new value
            message: Optional custom error message
        """
        self.key = key
        self.category = category
        self.old_step = old_step
        self.new_step = new_step

        if message is None:
            old_file = getattr(old_step, "yaml_file", "unknown")
            old_line = getattr(old_step, "line", "?")
            new_file = getattr(new_step, "yaml_file", "unknown")
            new_line = getattr(new_step, "line", "?")

            message = (
                f"Category conflict for key '{key}' at level '{category}': "
                f"existing value from {old_file}:{old_line} conflicts with "
                f"new value from {new_file}:{new_line}. "
                f"Use different categories or choose blocks to resolve."
            )

        super().__init__(message)


class ChooseConflictError(ProvenanceError):
    """
    Raised when conflicting choose blocks are encountered at the same level.

    This error indicates that two non-nested choose blocks are attempting to
    set the same configuration key, which is not allowed.

    Attributes:
        key: The configuration key with the conflict
        old_choose: Identifier of the existing choose block
        new_choose: Identifier of the conflicting choose block
        category: The category level where the conflict occurred
        old_step: The provenance step of the existing value
        new_step: The provenance step of the new conflicting value
    """

    def __init__(
        self,
        key: str,
        old_choose: str,
        new_choose: str,
        category: Optional[str],
        old_step: Any,
        new_step: Any,
        message: Optional[str] = None,
    ) -> None:
        """
        Initialize choose conflict error.

        Args:
            key: Configuration key with conflict
            old_choose: Identifier of existing choose block
            new_choose: Identifier of conflicting choose block
            category: Category level of conflict
            old_step: Provenance step of existing value
            new_step: Provenance step of new value
            message: Optional custom error message
        """
        self.key = key
        self.old_choose = old_choose
        self.new_choose = new_choose
        self.category = category
        self.old_step = old_step
        self.new_step = new_step

        if message is None:
            message = (
                f"Choose block conflict for key '{key}': "
                f"choose block '{old_choose}' conflicts with '{new_choose}' "
                f"at category level '{category}'. Choose blocks must be nested "
                f"to override values."
            )

        super().__init__(message)


class ValidationError(ProvenanceError):
    """
    Raised when provenance validation fails.

    This error indicates that provenance data is malformed or inconsistent.
    """

    pass


class SerializationError(ProvenanceError):
    """
    Raised when serialization or deserialization of provenance fails.

    This error indicates that provenance data could not be converted to/from
    the requested format.
    """

    pass


class ConfigurationError(ProvenanceError):
    """
    Raised when there is an error in provenance configuration.

    This error indicates that settings or configuration is invalid.
    """

    pass


class LoaderError(ProvenanceError):
    """
    Raised when YAML loading with provenance fails.

    This error indicates that a YAML file could not be loaded or parsed
    correctly with provenance tracking.
    """

    pass


class DumperError(ProvenanceError):
    """
    Raised when YAML dumping with provenance fails.

    This error indicates that data could not be written to YAML format
    with provenance annotations.
    """

    pass
