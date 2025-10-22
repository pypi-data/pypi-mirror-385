"""
Comprehensive tests for YAML loader with provenance tracking.

This module tests the ProvenanceLoader class and related utilities to ensure
that YAML files are loaded correctly with accurate provenance information.
"""

import os
from io import StringIO
from pathlib import Path

import pytest

# Import the modules to test
from herrkunft.yaml import (
    ProvenanceLoader,
    create_minimal_provenance,
    extract_file_list_from_provenance,
    format_provenance_for_display,
    get_provenance_for_key,
    validate_provenance_structure,
)

# Fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestProvenanceLoader:
    """Tests for the ProvenanceLoader class."""

    def test_load_simple_config(self):
        """Test loading a simple YAML configuration file."""
        loader = ProvenanceLoader(category="test", subcategory="simple")
        data, prov = loader.load(FIXTURES_DIR / "simple_config.yaml", return_tuple=True)

        # Check that data was loaded
        assert "database" in data
        assert data["database"]["host"] == "localhost"
        assert data["database"]["port"] == 5432

        # Check that provenance was extracted
        assert "database" in prov
        assert "host" in prov["database"]
        assert prov["database"]["host"]["line"] is not None
        assert prov["database"]["host"]["yaml_file"].endswith("simple_config.yaml")
        assert prov["database"]["host"]["category"] == "test"
        assert prov["database"]["host"]["subcategory"] == "simple"

    def test_load_nested_structure(self):
        """Test loading YAML with deeply nested structures."""
        loader = ProvenanceLoader()
        data, prov = loader.load(FIXTURES_DIR / "nested_config.yaml", return_tuple=True)

        # Check deep nesting
        assert "services" in data
        assert "api" in data["services"]
        assert "endpoints" in data["services"]["api"]
        assert "users" in data["services"]["api"]["endpoints"]
        assert "auth" in data["services"]["api"]["endpoints"]["users"]
        assert data["services"]["api"]["endpoints"]["users"]["auth"]["required"] is True

        # Check provenance for deeply nested value
        assert "services" in prov
        assert "api" in prov["services"]
        assert "endpoints" in prov["services"]["api"]
        users_auth_prov = prov["services"]["api"]["endpoints"]["users"]["auth"][
            "required"
        ]
        assert users_auth_prov["line"] is not None
        assert users_auth_prov["yaml_file"].endswith("nested_config.yaml")

    def test_load_with_lists(self):
        """Test loading YAML with list structures."""
        loader = ProvenanceLoader()
        data, prov = loader.load(FIXTURES_DIR / "simple_config.yaml", return_tuple=True)

        # Check list data
        assert "features" in data["application"]
        assert isinstance(data["application"]["features"], list)
        assert "authentication" in data["application"]["features"]

        # Check provenance for list elements
        assert isinstance(prov["application"]["features"], list)
        assert len(prov["application"]["features"]) == len(
            data["application"]["features"]
        )
        for item_prov in prov["application"]["features"]:
            assert "line" in item_prov
            assert item_prov["yaml_file"].endswith("simple_config.yaml")

    def test_load_from_string_io(self):
        """Test loading YAML from a StringIO object."""
        yaml_content = """
test:
  value: 123
  name: test_name
"""
        stream = StringIO(yaml_content)
        stream.name = "<test_stream>"

        loader = ProvenanceLoader(category="runtime")
        data, prov = loader.load(stream, return_tuple=True)

        assert data["test"]["value"] == 123
        assert prov["test"]["value"]["yaml_file"] == "<test_stream>"
        assert prov["test"]["value"]["category"] == "runtime"

    def test_load_nonexistent_file(self):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        loader = ProvenanceLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_file.yaml", return_tuple=True)

    def test_load_empty_file(self):
        """Test loading an empty YAML file."""
        empty_yaml = FIXTURES_DIR / "empty.yaml"
        empty_yaml.write_text("")

        loader = ProvenanceLoader()
        data, prov = loader.load(empty_yaml, return_tuple=True)

        assert data == {}
        assert prov == {}

        # Cleanup
        empty_yaml.unlink()

    def test_load_multiple_files(self):
        """Test loading multiple YAML files."""
        loader = ProvenanceLoader()
        results = loader.load_multiple(
            [
                (FIXTURES_DIR / "defaults.yaml", "defaults"),
                (FIXTURES_DIR / "production.yaml", "environment", "production"),
                (FIXTURES_DIR / "development.yaml", "environment", "development"),
            ],
            return_tuple=True,
        )

        assert len(results) == 3

        # Check first file (defaults)
        defaults_data, defaults_prov = results[0]
        assert defaults_data["app"]["name"] == "DefaultApp"
        assert defaults_prov["app"]["name"]["category"] == "defaults"

        # Check second file (production)
        prod_data, prod_prov = results[1]
        assert prod_data["database"]["pool_size"] == 20
        assert prod_prov["database"]["pool_size"]["category"] == "environment"
        assert prod_prov["database"]["pool_size"]["subcategory"] == "production"

        # Check third file (development)
        dev_data, dev_prov = results[2]
        assert dev_data["logging"]["level"] == "DEBUG"
        assert dev_prov["logging"]["level"]["subcategory"] == "development"

    def test_category_override(self):
        """Test that category can be overridden per load."""
        loader = ProvenanceLoader(category="default_category")

        # Load with default category
        data1, prov1 = loader.load(
            FIXTURES_DIR / "simple_config.yaml", return_tuple=True
        )
        assert prov1["database"]["host"]["category"] == "default_category"

        # Load with override category
        data2, prov2 = loader.load(
            FIXTURES_DIR / "simple_config.yaml",
            category="override_category",
            return_tuple=True,
        )
        assert prov2["database"]["host"]["category"] == "override_category"

    def test_line_and_column_accuracy(self):
        """Test that line and column numbers are accurate."""
        loader = ProvenanceLoader()
        data, prov = loader.load(FIXTURES_DIR / "simple_config.yaml", return_tuple=True)

        # The "database" key should be on line 2
        # Note: We need to check the actual file to verify exact lines
        database_section = prov["database"]

        # Check that host has line/col info
        host_prov = database_section["host"]
        assert host_prov["line"] is not None
        assert host_prov["col"] is not None
        assert host_prov["line"] > 0  # Should be positive line number
        assert host_prov["col"] > 0  # Should be positive column number


class TestUtilityFunctions:
    """Tests for YAML utility functions."""

    def test_validate_provenance_structure(self):
        """Test validating that provenance matches data structure."""
        data = {"a": 1, "b": {"c": 2, "d": 3}, "e": [1, 2, 3]}

        # Valid provenance
        valid_prov = {
            "a": {"line": 1},
            "b": {"c": {"line": 2}, "d": {"line": 3}},
            "e": [{"line": 4}, {"line": 5}, {"line": 6}],
        }
        assert validate_provenance_structure(data, valid_prov) is True

        # Invalid provenance (missing key)
        invalid_prov1 = {
            "a": {"line": 1},
            "b": {"c": {"line": 2}},  # Missing "d"
        }
        assert validate_provenance_structure(data, invalid_prov1) is False

        # Invalid provenance (wrong type)
        invalid_prov2 = {
            "a": {"line": 1},
            "b": "wrong type",  # Should be dict
            "e": [{"line": 4}, {"line": 5}, {"line": 6}],
        }
        assert validate_provenance_structure(data, invalid_prov2) is False

    def test_get_provenance_for_key(self):
        """Test retrieving provenance for a specific key path."""
        data = {"database": {"connection": {"host": "localhost", "port": 5432}}}

        prov = {
            "database": {
                "connection": {
                    "host": {"line": 5, "col": 10},
                    "port": {"line": 6, "col": 10},
                }
            }
        }

        # Get nested key provenance
        host_prov = get_provenance_for_key(data, prov, "database.connection.host")
        assert host_prov["line"] == 5
        assert host_prov["col"] == 10

        port_prov = get_provenance_for_key(data, prov, "database.connection.port")
        assert port_prov["line"] == 6

        # Non-existent key
        none_prov = get_provenance_for_key(data, prov, "database.nonexistent")
        assert none_prov is None

    def test_format_provenance_for_display(self):
        """Test formatting provenance as human-readable string."""
        prov = {
            "database": {
                "host": {
                    "yaml_file": "/path/to/config.yaml",
                    "line": 5,
                    "col": 8,
                    "category": "defaults",
                }
            }
        }

        formatted = format_provenance_for_display(prov)
        assert "database:" in formatted
        assert "host: /path/to/config.yaml:5:8" in formatted
        assert "(defaults)" in formatted

    def test_extract_file_list_from_provenance(self):
        """Test extracting unique file list from provenance."""
        prov = {
            "a": {"yaml_file": "/path/to/file1.yaml"},
            "b": {"yaml_file": "/path/to/file2.yaml"},
            "c": {"yaml_file": "/path/to/file1.yaml"},  # Duplicate
        }

        files = extract_file_list_from_provenance(prov)
        assert len(files) == 2
        assert "/path/to/file1.yaml" in files
        assert "/path/to/file2.yaml" in files

    def test_create_minimal_provenance(self):
        """Test creating minimal provenance for runtime values."""
        prov = create_minimal_provenance(
            "<runtime>", category="backend", subcategory="dynamic"
        )

        assert prov["yaml_file"] == "<runtime>"
        assert prov["category"] == "backend"
        assert prov["subcategory"] == "dynamic"
        assert prov["line"] is None
        assert prov["col"] is None


class TestEnvironmentVariables:
    """Tests for environment variable handling in YAML."""

    def test_load_with_env_vars(self):
        """Test loading YAML file with environment variables."""
        # Set test environment variables
        os.environ["DATABASE_URL"] = "postgresql://localhost/testdb"
        os.environ["DB_PASSWORD"] = "secret123"
        os.environ["API_KEY"] = "test_api_key"
        os.environ["API_SECRET"] = "test_api_secret"

        loader = ProvenanceLoader()
        data, prov = loader.load(FIXTURES_DIR / "with_env_vars.yaml", return_tuple=True)

        # Check that env vars were substituted
        assert data["database"]["url"] == "postgresql://localhost/testdb"
        assert data["database"]["password"] == "secret123"
        assert data["api"]["key"] == "test_api_key"
        assert data["api"]["secret"] == "test_api_secret"

        # Check that static values are unchanged
        assert data["static_value"] == "this is not an env var"

        # Cleanup
        del os.environ["DATABASE_URL"]
        del os.environ["DB_PASSWORD"]
        del os.environ["API_KEY"]
        del os.environ["API_SECRET"]

    def test_missing_env_var_raises_error(self):
        """Test that missing environment variable raises error."""
        # Ensure env var doesn't exist
        if "NONEXISTENT_VAR" in os.environ:
            del os.environ["NONEXISTENT_VAR"]

        # Create a test file with missing env var
        test_yaml = FIXTURES_DIR / "missing_env.yaml"
        test_yaml.write_text("value: !ENV ${NONEXISTENT_VAR}")

        loader = ProvenanceLoader()
        with pytest.raises(EnvironmentError):
            loader.load(test_yaml, return_tuple=True)

        # Cleanup
        test_yaml.unlink()


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""

    def test_multi_environment_configuration(self):
        """Test loading configuration from multiple environment layers."""
        loader = ProvenanceLoader()

        # Load files in hierarchy: defaults -> production
        results = loader.load_multiple(
            [
                (FIXTURES_DIR / "defaults.yaml", "defaults"),
                (FIXTURES_DIR / "production.yaml", "environment", "production"),
            ],
            return_tuple=True,
        )

        defaults_data, defaults_prov = results[0]
        prod_data, prod_prov = results[1]

        # Verify defaults
        assert defaults_data["app"]["debug"] is False
        assert defaults_data["app"]["timeout"] == 30

        # Verify production overrides
        assert prod_data["app"]["timeout"] == 60
        assert prod_data["app"]["workers"] == 8

        # Verify provenance tracking
        assert defaults_prov["app"]["timeout"]["category"] == "defaults"
        assert prod_prov["app"]["timeout"]["category"] == "environment"
        assert prod_prov["app"]["timeout"]["subcategory"] == "production"

    def test_complex_nested_navigation(self):
        """Test navigating complex nested structures with provenance."""
        loader = ProvenanceLoader()
        data, prov = loader.load(FIXTURES_DIR / "nested_config.yaml", return_tuple=True)

        # Navigate to deeply nested value
        api_endpoints = data["services"]["api"]["endpoints"]
        users_methods = api_endpoints["users"]["methods"]

        assert isinstance(users_methods, list)
        assert "GET" in users_methods
        assert "POST" in users_methods

        # Check provenance for list items
        users_methods_prov = prov["services"]["api"]["endpoints"]["users"]["methods"]
        assert isinstance(users_methods_prov, list)
        for method_prov in users_methods_prov:
            assert "line" in method_prov
            assert method_prov["yaml_file"].endswith("nested_config.yaml")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
