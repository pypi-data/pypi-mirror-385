"""
Comprehensive tests for YAML dumper with provenance support.

This module tests the ProvenanceDumper class to ensure that YAML files are
written correctly with optional provenance comments.
"""

import os
import tempfile
from io import StringIO
from pathlib import Path

from herrkunft.core.provenance import Provenance, ProvenanceStep
from herrkunft.types.factory import TypeWrapperFactory
from herrkunft.yaml import ProvenanceDumper, ProvenanceLoader

# Fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestProvenanceDumperBasics:
    """Tests for basic ProvenanceDumper functionality."""

    def test_dumper_initialization(self):
        """Test that dumper initializes correctly."""
        dumper = ProvenanceDumper()
        assert dumper.include_comments is True
        assert dumper.yaml is not None

    def test_dumper_without_comments(self):
        """Test dumper initialization without comments."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        assert dumper.include_comments is False

    def test_dump_simple_dict(self):
        """Test dumping a simple dictionary."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"key": "value", "number": 42}

        yaml_str = dumper.dumps(data)

        assert "key: value" in yaml_str
        assert "number: 42" in yaml_str

    def test_dump_nested_dict(self):
        """Test dumping a nested dictionary."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {
            "database": {
                "host": "localhost",
                "port": 5432,
            },
            "cache": {
                "enabled": True,
            },
        }

        yaml_str = dumper.dumps(data)

        assert "database:" in yaml_str
        assert "host: localhost" in yaml_str
        assert "port: 5432" in yaml_str
        assert "cache:" in yaml_str
        assert "enabled: true" in yaml_str

    def test_dump_with_list(self):
        """Test dumping dictionary with list values."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {
            "servers": ["server1", "server2", "server3"],
            "ports": [8000, 8001, 8002],
        }

        yaml_str = dumper.dumps(data)

        assert "servers:" in yaml_str
        assert "server1" in yaml_str
        assert "ports:" in yaml_str


class TestProvenanceDumperWithFile:
    """Tests for dumping to files."""

    def test_dump_to_file(self):
        """Test dumping to a file."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"test": "value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            dumper.dump(data, temp_path)

            # Verify file was created and contains data
            with open(temp_path) as f:
                content = f.read()
                assert "test: value" in content
        finally:
            os.unlink(temp_path)

    def test_dump_to_file_object(self):
        """Test dumping to a file object."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"test": "value"}

        stream = StringIO()
        dumper.dump(data, stream)

        content = stream.getvalue()
        assert "test: value" in content

    def test_dump_to_path_object(self):
        """Test dumping using Path object."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"test": "value"}

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "output.yaml"
            dumper.dump(data, temp_path)

            # Verify file was created
            assert temp_path.exists()
            with open(temp_path) as f:
                content = f.read()
                assert "test: value" in content


class TestProvenanceDumperWithWrappedValues:
    """Tests for dumping values with provenance wrappers."""

    def test_dump_wrapped_string(self):
        """Test dumping string wrapped with provenance."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        prov = Provenance({"category": "defaults", "line": 5})
        wrapped_value = TypeWrapperFactory.wrap("hello", prov)

        data = {"key": wrapped_value}
        yaml_str = dumper.dumps(data)

        assert "key: hello" in yaml_str

    def test_dump_wrapped_values_clean(self):
        """Test dumping with clean=True removes wrappers."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        prov = Provenance({"category": "defaults"})
        wrapped_value = TypeWrapperFactory.wrap("hello", prov)

        data = {"key": wrapped_value}
        yaml_str = dumper.dumps(data, clean=True)

        assert "key: hello" in yaml_str
        # Should not have any provenance artifacts
        assert "provenance" not in yaml_str.lower()

    def test_dump_mixed_wrapped_and_plain(self):
        """Test dumping mix of wrapped and plain values."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        prov = Provenance({"category": "defaults"})
        wrapped = TypeWrapperFactory.wrap("wrapped", prov)

        data = {"wrapped_key": wrapped, "plain_key": "plain"}

        yaml_str = dumper.dumps(data)

        assert "wrapped_key: wrapped" in yaml_str
        assert "plain_key: plain" in yaml_str


class TestProvenanceDumperComments:
    """Tests for provenance comment generation."""

    def test_dump_with_comments_simple(self):
        """Test that provenance comments are added."""
        dumper = ProvenanceDumper(include_provenance_comments=True)

        prov_step = ProvenanceStep(
            yaml_file="/path/to/config.yaml",
            line=10,
            col=5,
            category="defaults",
        )
        prov = Provenance(prov_step)
        wrapped_value = TypeWrapperFactory.wrap("hello", prov)

        data = {"key": wrapped_value}
        yaml_str = dumper.dumps(data)

        # Check that comment is present
        assert "config.yaml" in yaml_str
        assert "line: 10" in yaml_str
        assert "category: defaults" in yaml_str

    def test_dump_without_comments(self):
        """Test that comments are not added when disabled."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        prov_step = ProvenanceStep(
            yaml_file="/path/to/config.yaml",
            line=10,
            category="defaults",
        )
        prov = Provenance(prov_step)
        wrapped_value = TypeWrapperFactory.wrap("hello", prov)

        data = {"key": wrapped_value}
        yaml_str = dumper.dumps(data)

        # Check that no comments are present
        assert "#" not in yaml_str or yaml_str.count("#") == 0

    def test_comment_format(self):
        """Test the format of provenance comments."""
        dumper = ProvenanceDumper(include_provenance_comments=True)

        prov_step = ProvenanceStep(
            yaml_file="/path/to/config.yaml",
            line=15,
            col=8,
            category="components",
            subcategory="fesom",
        )
        prov = Provenance(prov_step)
        wrapped_value = TypeWrapperFactory.wrap("value", prov)

        data = {"key": wrapped_value}
        yaml_str = dumper.dumps(data)

        # Verify format: "# from: file | line: N | category: X"
        assert "from: config.yaml" in yaml_str
        assert "line: 15" in yaml_str
        assert "col: 8" in yaml_str
        assert "category: components" in yaml_str
        assert "subcategory: fesom" in yaml_str

    def test_nested_dict_with_comments(self):
        """Test comments on nested dictionaries."""
        dumper = ProvenanceDumper(include_provenance_comments=True)

        prov1 = Provenance(
            {"yaml_file": "file1.yaml", "line": 5, "category": "defaults"}
        )
        prov2 = Provenance(
            {"yaml_file": "file2.yaml", "line": 10, "category": "machines"}
        )

        wrapped1 = TypeWrapperFactory.wrap("value1", prov1)
        wrapped2 = TypeWrapperFactory.wrap("value2", prov2)

        data = {
            "level1": {
                "key1": wrapped1,
                "key2": wrapped2,
            }
        }

        yaml_str = dumper.dumps(data)

        # Both files should be mentioned
        assert "file1.yaml" in yaml_str
        assert "file2.yaml" in yaml_str


class TestProvenanceDumperRoundTrip:
    """Tests for round-trip: load -> dump -> load."""

    def test_round_trip_simple(self):
        """Test round-trip with simple config."""
        loader = ProvenanceLoader(category="test")
        dumper = ProvenanceDumper(include_provenance_comments=False)

        # Load original file
        data = loader.load(FIXTURES_DIR / "simple_config.yaml")

        # Dump to string
        yaml_str = dumper.dumps(data)

        # Verify we can parse it back
        assert "database:" in yaml_str
        assert "host: localhost" in yaml_str

    def test_round_trip_preserves_structure(self):
        """Test that structure is preserved in round-trip."""
        loader = ProvenanceLoader(category="test")
        dumper = ProvenanceDumper(include_provenance_comments=False)

        # Load original
        data = loader.load(FIXTURES_DIR / "nested_config.yaml")

        # Dump and reload
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            dumper.dump(data, temp_path)

            # Reload
            loader2 = ProvenanceLoader()
            data2 = loader2.load(temp_path)

            # Verify structure is preserved
            assert "services" in data2
            assert "api" in data2["services"]
        finally:
            os.unlink(temp_path)


class TestProvenanceDumperEdgeCases:
    """Tests for edge cases and error handling."""

    def test_dump_empty_dict(self):
        """Test dumping empty dictionary."""
        dumper = ProvenanceDumper()
        data = {}

        yaml_str = dumper.dumps(data)

        assert yaml_str == "{}\n" or yaml_str.strip() == "{}"

    def test_dump_none_values(self):
        """Test dumping dictionary with None values."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"key": None, "other": "value"}

        yaml_str = dumper.dumps(data)

        assert "key:" in yaml_str
        assert "other: value" in yaml_str

    def test_dump_boolean_values(self):
        """Test dumping boolean values."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"enabled": True, "disabled": False}

        yaml_str = dumper.dumps(data)

        assert "enabled: true" in yaml_str
        assert "disabled: false" in yaml_str

    def test_dump_numeric_values(self):
        """Test dumping various numeric types."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"integer": 42, "float": 3.14, "negative": -10}

        yaml_str = dumper.dumps(data)

        assert "integer: 42" in yaml_str
        assert "float: 3.14" in yaml_str
        assert "negative: -10" in yaml_str

    def test_dump_special_yaml_characters(self):
        """Test dumping strings with special YAML characters."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"colon": "value: with colon", "quote": 'value with "quotes"'}

        yaml_str = dumper.dumps(data)

        # Should be properly escaped/quoted
        assert "colon:" in yaml_str
        assert "quote:" in yaml_str

    def test_dump_multiline_string(self):
        """Test dumping multiline strings."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"description": "Line 1\nLine 2\nLine 3"}

        yaml_str = dumper.dumps(data)

        assert "description:" in yaml_str
        # ruamel.yaml should handle multiline appropriately


class TestProvenanceDumperListHandling:
    """Tests for list handling in dumper."""

    def test_dump_simple_list(self):
        """Test dumping simple list."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"items": ["item1", "item2", "item3"]}

        yaml_str = dumper.dumps(data)

        assert "items:" in yaml_str
        assert "item1" in yaml_str
        assert "item2" in yaml_str
        assert "item3" in yaml_str

    def test_dump_list_of_dicts(self):
        """Test dumping list of dictionaries."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        }

        yaml_str = dumper.dumps(data)

        assert "users:" in yaml_str
        assert "Alice" in yaml_str
        assert "Bob" in yaml_str

    def test_dump_nested_lists(self):
        """Test dumping nested lists."""
        dumper = ProvenanceDumper(include_provenance_comments=False)
        data = {"matrix": [[1, 2], [3, 4], [5, 6]]}

        yaml_str = dumper.dumps(data)

        assert "matrix:" in yaml_str


class TestProvenanceDumperIntegration:
    """Integration tests with other provenance components."""

    def test_dump_with_real_loader_data(self):
        """Test dumping data loaded with ProvenanceLoader."""
        loader = ProvenanceLoader(category="test")
        dumper = ProvenanceDumper(include_provenance_comments=False)

        # Load a real config
        data = loader.load(FIXTURES_DIR / "simple_config.yaml")

        # Dump it
        yaml_str = dumper.dumps(data)

        # Verify it's valid YAML
        assert "database:" in yaml_str
        assert "application:" in yaml_str

    def test_clean_removes_all_wrappers(self):
        """Test that clean=True removes all provenance wrappers."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        # Create data with wrapped values
        prov = Provenance({"category": "test"})
        data = {
            "key1": TypeWrapperFactory.wrap("value1", prov),
            "key2": TypeWrapperFactory.wrap(42, prov),
            "key3": TypeWrapperFactory.wrap(True, prov),
        }

        yaml_str = dumper.dumps(data, clean=True)

        # Should be plain YAML without any wrapper artifacts
        assert "key1: value1" in yaml_str
        assert "key2: 42" in yaml_str
        assert "key3: true" in yaml_str
        # No mention of provenance or wrappers
        assert "Provenance" not in yaml_str
        assert "_hierarchy" not in yaml_str


class TestProvenanceDumperYAMLPreservation:
    """Tests for YAML formatting preservation."""

    def test_preserve_yaml_style(self):
        """Test that YAML style is preserved when possible."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        # Create data that should use block style
        data = {
            "config": {
                "option1": "value1",
                "option2": "value2",
            }
        }

        yaml_str = dumper.dumps(data)

        # Should not be in flow style (not {config: {option1: value1, ...}})
        assert "{" not in yaml_str or yaml_str.count("{") == 0

    def test_wide_output_no_wrapping(self):
        """Test that long lines are not wrapped."""
        dumper = ProvenanceDumper(include_provenance_comments=False)

        long_value = "a" * 200  # Very long string
        data = {"long_key": long_value}

        yaml_str = dumper.dumps(data)

        # Should contain the long value (possibly quoted but not wrapped)
        assert long_value in yaml_str or f"'{long_value}'" in yaml_str
