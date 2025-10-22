"""Global configuration settings for the provenance library."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProvenanceSettings(BaseSettings):
    """
    Global provenance library settings.

    Settings can be configured via:
    - Environment variables (prefixed with PROVENANCE_)
    - Direct attribute assignment
    - Constructor arguments

    Example:
        >>> from herrkunft.config.settings import settings
        >>> settings.log_level = "DEBUG"
        >>> settings.strict_conflicts = True

    Environment Variables:
        PROVENANCE_LOG_LEVEL: Logging level (default: INFO)
        PROVENANCE_LOG_PROVENANCE_OPERATIONS: Log provenance operations (default: False)
        PROVENANCE_DEFAULT_CATEGORY: Default category for loading (default: None)
        PROVENANCE_STRICT_CONFLICTS: Raise errors on conflicts (default: True)
        PROVENANCE_ALLOW_SAME_LEVEL_OVERRIDE: Allow same-level overrides (default: False)
        PROVENANCE_CACHE_WRAPPER_CLASSES: Cache dynamically created classes (default: True)
        PROVENANCE_MAX_PROVENANCE_HISTORY: Limit history length (default: None)
        PROVENANCE_YAML_WIDTH: YAML output line width (default: 120)
        PROVENANCE_INCLUDE_TIMESTAMPS: Include timestamps in provenance (default: False)
        PROVENANCE_DEFAULT_CATEGORIES: Default category hierarchy (comma-separated)
    """

    model_config = SettingsConfigDict(
        env_prefix="PROVENANCE_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level for the library (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    log_provenance_operations: bool = Field(
        default=False,
        description="Enable detailed logging of provenance operations",
    )

    # Hierarchy settings
    default_category: Optional[str] = Field(
        default=None,
        description="Default category to use when loading YAML files",
    )

    strict_conflicts: bool = Field(
        default=True,
        description="Raise errors on category conflicts instead of warnings",
    )

    allow_same_level_override: bool = Field(
        default=False,
        description="Allow values to override at the same category level",
    )

    default_categories: list[str] = Field(
        default_factory=lambda: [
            "unknown",
            "defaults",
            "other_software",
            "machines",
            "components",
            "setups",
            "couplings",
            "runscript",
            "command_line",
            "backend",
        ],
        description="Default category hierarchy in precedence order (low to high)",
    )

    # Performance settings
    cache_wrapper_classes: bool = Field(
        default=True,
        description="Cache dynamically created wrapper classes for performance",
    )

    max_provenance_history: Optional[int] = Field(
        default=None,
        description="Maximum length of provenance history (None = unlimited)",
    )

    # YAML settings
    yaml_width: int = Field(
        default=120,
        description="Line width for YAML output",
        gt=20,
        le=4096,
    )

    include_timestamps: bool = Field(
        default=False,
        description="Include ISO timestamps in provenance steps",
    )

    preserve_quotes: bool = Field(
        default=True,
        description="Preserve quotes in YAML round-trips",
    )

    # Validation settings
    validate_on_load: bool = Field(
        default=True,
        description="Validate provenance structure when loading",
    )

    validate_file_exists: bool = Field(
        default=True,
        description="Check that provenance yaml_file paths exist",
    )

    def configure_logging(self) -> None:
        """
        Configure loguru logging based on settings.

        This method sets up the logging level for the provenance library.
        Call this after modifying log_level to apply changes.
        """
        import sys

        from loguru import logger

        # Remove default handler
        logger.remove()

        # Add handler with configured level
        logger.add(
            sys.stderr,
            level=self.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

        if self.log_provenance_operations:
            logger.info("Provenance operation logging enabled")

    def reset_to_defaults(self) -> None:
        """
        Reset all settings to their default values.

        This is useful for testing or when you want to start fresh.
        """
        defaults = ProvenanceSettings()
        for field_name in self.model_fields:
            setattr(self, field_name, getattr(defaults, field_name))


# Global settings instance
# This can be imported and used throughout the library
settings = ProvenanceSettings()

# Configure logging on import
settings.configure_logging()


def get_settings() -> ProvenanceSettings:
    """
    Get the global settings instance.

    Returns:
        The global ProvenanceSettings instance

    Example:
        >>> from herrkunft.config import get_settings
        >>> settings = get_settings()
        >>> settings.log_level = "DEBUG"
    """
    return settings


def reset_settings() -> None:
    """
    Reset settings to default values.

    This is primarily useful for testing.

    Example:
        >>> from herrkunft.config import reset_settings
        >>> reset_settings()
    """
    global settings
    settings.reset_to_defaults()
    settings.configure_logging()
