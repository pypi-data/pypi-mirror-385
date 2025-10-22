"""Version information for the provenance library."""

__version__ = "0.1.0"
__version_info__ = tuple(int(x) for x in __version__.split("."))

# Compatibility version
__api_version__ = "1.0"


# Full version string with metadata
def get_version() -> str:
    """
    Get the full version string.

    Returns:
        Full version string including metadata
    """
    return __version__
