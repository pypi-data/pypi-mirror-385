"""
Integration tests for herrkunft library.

This module provides end-to-end integration tests that verify all components
work together correctly. These tests cover:
- Complete YAML load/modify/save workflows
- Multi-file hierarchical configuration loading
- Conflict resolution and hierarchy management
- Nested structure provenance tracking
- Round-trip data integrity

These tests require all core components to be implemented:
- DictWithProvenance, ListWithProvenance (Expert 2)
- ProvenanceDumper (Expert 3)
- ProvenanceLoader (Expert 3)
"""

from pathlib import Path

import pytest

# Import all components needed for integration testing
try:
    from herrkunft import (
        CategoryLevel,
        DictWithProvenance,
        HierarchyConfig,
        HierarchyManager,
        ListWithProvenance,
        Provenance,
        ProvenanceDumper,
        ProvenanceLoader,
        ProvenanceStep,
        clean_provenance,
        dump_yaml,
        extract_provenance_tree,
        load_yaml,
    )

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


# Fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# Skip all tests if components not yet implemented
pytestmark = pytest.mark.skipif(
    not COMPONENTS_AVAILABLE,
    reason=f"Core components not yet implemented: {IMPORT_ERROR if not COMPONENTS_AVAILABLE else ''}",
)


class TestCompleteWorkflow:
    """Test complete end-to-end workflows."""

    def test_basic_load_modify_save_reload(self, tmp_path):
        """
        Test: load YAML -> modify -> save -> reload

        This is the most fundamental integration test - it verifies that
        a configuration can be loaded with provenance, modified, saved,
        and reloaded without data loss.
        """
        # Create a simple test YAML file
        test_yaml = tmp_path / "test_config.yaml"
        test_yaml.write_text("""
database:
  host: localhost
  port: 5432
  name: testdb

server:
  host: 0.0.0.0
  port: 8080
""")

        # Step 1: Load with provenance
        config = load_yaml(str(test_yaml), category="defaults")

        # Verify it's a DictWithProvenance
        assert isinstance(config, DictWithProvenance), (
            f"Expected DictWithProvenance, got {type(config)}"
        )

        # Verify provenance is attached
        assert hasattr(config["database"]["host"], "provenance"), (
            "Expected provenance attribute on values"
        )

        prov = config["database"]["host"].provenance
        assert prov is not None, "Provenance should not be None"
        assert len(prov) > 0, "Provenance history should have at least one step"
        assert prov.current.yaml_file.endswith("test_config.yaml")
        assert prov.current.category == "defaults"

        # Step 2: Modify values
        config["database"]["host"] = "production.example.com"
        config["database"]["port"] = 5433
        config["new_key"] = "new_value"

        # Verify modification added provenance step
        assert hasattr(config["database"]["host"], "provenance")
        host_prov = config["database"]["host"].provenance
        assert len(host_prov) > 1, "Modification should add provenance step"

        # Step 3: Save with provenance comments
        output_yaml = tmp_path / "output_config.yaml"
        dump_yaml(config, str(output_yaml), include_provenance=True)

        # Verify file was created
        assert output_yaml.exists(), "Output file should be created"

        # Verify content is valid YAML
        content = output_yaml.read_text()
        assert "database:" in content
        assert "host: production.example.com" in content
        assert "port: 5433" in content
        assert "new_key: new_value" in content

        # Step 4: Reload and verify
        reloaded = load_yaml(str(output_yaml), category="reloaded")
        assert isinstance(reloaded, DictWithProvenance)
        assert reloaded["database"]["host"] == "production.example.com"
        assert reloaded["database"]["port"] == 5433
        assert reloaded["new_key"] == "new_value"

        # Verify provenance on reloaded data
        assert hasattr(reloaded["database"]["host"], "provenance")
        reloaded_prov = reloaded["database"]["host"].provenance
        assert reloaded_prov.current.yaml_file.endswith("output_config.yaml")

    def test_clean_save_without_provenance(self, tmp_path):
        """Test saving without provenance metadata (clean mode)."""
        # Create test file
        test_yaml = tmp_path / "test.yaml"
        test_yaml.write_text("key: value\nnested:\n  item: data")

        # Load with provenance
        config = load_yaml(str(test_yaml), category="test")

        # Modify
        config["key"] = "modified"

        # Save without provenance (clean mode)
        output_yaml = tmp_path / "clean_output.yaml"
        dump_yaml(config, str(output_yaml), include_provenance=False, clean=True)

        # Verify output is clean (no provenance comments)
        content = output_yaml.read_text()
        assert "# from:" not in content.lower()
        assert "# provenance" not in content.lower()
        assert "key: modified" in content


class TestHierarchicalConfiguration:
    """Test multi-file loading with hierarchy and conflict resolution."""

    def test_two_level_hierarchy_override(self, tmp_path):
        """
        Test: Load defaults, then override with higher-priority config.

        Verifies that HierarchyManager correctly allows higher categories
        to override lower categories.
        """
        # Create defaults file
        defaults_yaml = tmp_path / "defaults.yaml"
        defaults_yaml.write_text("""
database:
  host: localhost
  port: 5432

server:
  debug: true
  workers: 1
""")

        # Create production overrides
        prod_yaml = tmp_path / "production.yaml"
        prod_yaml.write_text("""
database:
  host: prod.db.example.com
  port: 5433

server:
  debug: false
  workers: 4
""")

        # Load defaults first
        config = load_yaml(str(defaults_yaml), category="defaults")
        assert config["database"]["host"] == "localhost"
        assert config["server"]["debug"] == True

        # Load production config
        prod_config = load_yaml(
            str(prod_yaml), category="environment", subcategory="production"
        )

        # Update with production (should override because environment > defaults)
        config.update(prod_config)

        # Verify higher category won
        assert config["database"]["host"] == "prod.db.example.com"
        assert config["database"]["port"] == 5433
        assert config["server"]["debug"] == False
        assert config["server"]["workers"] == 4

        # Verify provenance shows override
        host_prov = config["database"]["host"].provenance
        assert host_prov.current.category == "environment"
        assert host_prov.current.subcategory == "production"

    def test_multi_file_loading_with_loader(self, tmp_path):
        """Test using ProvenanceLoader.load_multiple() for batch loading."""
        # Create multiple config files
        files = []
        for i, (name, category, content) in enumerate(
            [
                ("base.yaml", "defaults", "key: base_value\nbase_only: true"),
                ("dev.yaml", "environment", "key: dev_value\nenv: development"),
                (
                    "feature.yaml",
                    "components",
                    "key: feature_value\nfeature_flag: true",
                ),
            ]
        ):
            f = tmp_path / name
            f.write_text(content)
            files.append((str(f), category))

        # Load multiple files
        loader = ProvenanceLoader()
        configs = loader.load_multiple(files)

        assert len(configs) == 3
        assert all(isinstance(c, DictWithProvenance) for c in configs)

        # Verify each has correct provenance
        assert configs[0]["key"].provenance.current.category == "defaults"
        assert configs[1]["key"].provenance.current.category == "environment"
        assert configs[2]["key"].provenance.current.category == "components"

    def test_conflict_detection_same_category(self, tmp_path):
        """
        Test: Attempting to override at same category level should raise error.

        This verifies that HierarchyManager correctly detects and prevents
        conflicts at the same hierarchy level.
        """
        # Create two files in same category
        file1 = tmp_path / "comp1.yaml"
        file1.write_text("shared_key: value_from_comp1")

        file2 = tmp_path / "comp2.yaml"
        file2.write_text("shared_key: value_from_comp2")

        # Load first file
        config = load_yaml(str(file1), category="components", subcategory="comp1")

        # Load second file
        config2 = load_yaml(str(file2), category="components", subcategory="comp2")

        # Try to merge at same level - should raise CategoryConflictError
        from herrkunft import CategoryConflictError

        with pytest.raises(CategoryConflictError):
            config.update(config2)


class TestNestedStructures:
    """Test deeply nested dicts and lists preserve provenance."""

    def test_nested_dict_provenance(self, tmp_path):
        """Test that deeply nested dictionaries preserve provenance at all levels."""
        # Create YAML with deep nesting
        test_yaml = tmp_path / "nested.yaml"
        test_yaml.write_text("""
level1:
  level2:
    level3:
      level4:
        deep_value: found_it
        another: value
""")

        # Load and verify nesting
        config = load_yaml(str(test_yaml), category="test")

        # Verify each level is DictWithProvenance
        assert isinstance(config, DictWithProvenance)
        assert isinstance(config["level1"], DictWithProvenance)
        assert isinstance(config["level1"]["level2"], DictWithProvenance)
        assert isinstance(config["level1"]["level2"]["level3"], DictWithProvenance)
        assert isinstance(
            config["level1"]["level2"]["level3"]["level4"], DictWithProvenance
        )

        # Verify deep value has provenance
        deep_val = config["level1"]["level2"]["level3"]["level4"]["deep_value"]
        assert hasattr(deep_val, "provenance")
        assert deep_val.provenance.current.yaml_file.endswith("nested.yaml")

    def test_nested_list_provenance(self, tmp_path):
        """Test that lists within dicts preserve provenance for elements."""
        # Create YAML with lists
        test_yaml = tmp_path / "with_lists.yaml"
        test_yaml.write_text("""
servers:
  - hostname: server1.example.com
    port: 8080
  - hostname: server2.example.com
    port: 8081

simple_list:
  - item1
  - item2
  - item3
""")

        # Load and verify
        config = load_yaml(str(test_yaml), category="test")

        # Verify lists are ListWithProvenance
        assert isinstance(config["servers"], ListWithProvenance)
        assert isinstance(config["simple_list"], ListWithProvenance)

        # Verify list elements are wrapped appropriately
        assert isinstance(config["servers"][0], DictWithProvenance)
        assert hasattr(config["servers"][0]["hostname"], "provenance")

        # Verify simple list items have provenance
        assert hasattr(config["simple_list"][0], "provenance")

    def test_modify_nested_preserves_provenance(self, tmp_path):
        """Test that modifying nested structures preserves provenance chain."""
        # Create nested structure
        test_yaml = tmp_path / "test.yaml"
        test_yaml.write_text("""
config:
  database:
    host: localhost
""")

        config = load_yaml(str(test_yaml), category="defaults")

        # Modify nested value
        config["config"]["database"]["host"] = "newhost.example.com"

        # Verify provenance chain
        prov = config["config"]["database"]["host"].provenance
        assert len(prov) >= 2  # Original + modification

        # First step should be from YAML load
        assert prov[0].yaml_file.endswith("test.yaml")

        # Latest step should be modification
        assert prov.current.modified_by is not None


class TestProvenanceTreeExtraction:
    """Test provenance tree extraction and inspection."""

    def test_extract_full_provenance_tree(self, tmp_path):
        """Test extracting complete provenance tree from configuration."""
        test_yaml = tmp_path / "config.yaml"
        test_yaml.write_text("""
database:
  host: localhost
  port: 5432

server:
  host: 0.0.0.0
  workers: 4
""")

        config = load_yaml(str(test_yaml), category="defaults")

        # Extract provenance tree
        prov_tree = extract_provenance_tree(config)

        # Verify structure matches data
        assert "database" in prov_tree
        assert "server" in prov_tree
        assert "host" in prov_tree["database"]
        assert "port" in prov_tree["database"]

        # Verify provenance data is present
        db_host_prov = prov_tree["database"]["host"]
        assert "yaml_file" in db_host_prov
        assert db_host_prov["yaml_file"].endswith("config.yaml")
        assert "line" in db_host_prov
        assert db_host_prov["line"] > 0
        assert db_host_prov["category"] == "defaults"

    def test_provenance_history_access(self, tmp_path):
        """Test accessing provenance history with index parameter."""
        test_yaml = tmp_path / "test.yaml"
        test_yaml.write_text("key: original_value")

        config = load_yaml(str(test_yaml), category="defaults")

        # Modify multiple times
        config["key"] = "second_value"
        config["key"] = "third_value"

        # Get provenance at different points in history
        prov = config["key"].provenance

        # Current (index=-1 or no index)
        current_tree = extract_provenance_tree(config, index=-1)
        assert current_tree["key"]["modified_by"] is not None

        # First step (index=0)
        first_tree = extract_provenance_tree(config, index=0)
        assert first_tree["key"]["yaml_file"].endswith("test.yaml")


class TestRoundTripIntegrity:
    """Test data integrity through load/save/load cycles."""

    def test_round_trip_preserves_data_types(self, tmp_path):
        """Verify that all YAML data types survive round-trip."""
        test_yaml = tmp_path / "types.yaml"
        test_yaml.write_text("""
string_val: hello world
int_val: 42
float_val: 3.14159
bool_true: true
bool_false: false
null_val: null
list_val:
  - one
  - 2
  - 3.0
dict_val:
  nested: value
""")

        # Load
        config = load_yaml(str(test_yaml), category="test")

        # Save
        output = tmp_path / "output.yaml"
        dump_yaml(config, str(output), include_provenance=False, clean=True)

        # Reload
        reloaded = load_yaml(str(output), category="test")

        # Verify types preserved
        assert isinstance(reloaded["string_val"], str)
        assert reloaded["string_val"] == "hello world"
        assert isinstance(reloaded["int_val"], int)
        assert reloaded["int_val"] == 42
        assert isinstance(reloaded["float_val"], float)
        assert abs(reloaded["float_val"] - 3.14159) < 0.00001
        assert isinstance(reloaded["bool_true"], bool)
        assert reloaded["bool_true"] == True
        assert isinstance(reloaded["bool_false"], bool)
        assert reloaded["bool_false"] == False
        assert reloaded["null_val"] == None  # Use == instead of is for wrapped types
        assert isinstance(reloaded["list_val"], list)
        assert len(reloaded["list_val"]) == 3
        assert isinstance(reloaded["dict_val"], dict)

    def test_round_trip_preserves_structure(self, tmp_path):
        """Verify that nested structure is preserved through round-trip."""
        test_yaml = tmp_path / "structure.yaml"
        test_yaml.write_text("""
root:
  level1:
    level2:
      - item1
      - item2
    another:
      key: value
  sibling:
    data: here
""")

        # Load
        config = load_yaml(str(test_yaml), category="test")

        # Save with provenance
        output = tmp_path / "output.yaml"
        dump_yaml(config, str(output), include_provenance=True)

        # Reload
        reloaded = load_yaml(str(output), category="test")

        # Verify structure preserved
        assert "root" in reloaded
        assert "level1" in reloaded["root"]
        assert "level2" in reloaded["root"]["level1"]
        assert isinstance(reloaded["root"]["level1"]["level2"], list)
        assert len(reloaded["root"]["level1"]["level2"]) == 2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dict(self, tmp_path):
        """Test loading and saving empty dictionary."""
        test_yaml = tmp_path / "empty.yaml"
        test_yaml.write_text("{}")

        config = load_yaml(str(test_yaml), category="test")
        assert isinstance(config, DictWithProvenance)
        assert len(config) == 0

        output = tmp_path / "output.yaml"
        dump_yaml(config, str(output))

        reloaded = load_yaml(str(output), category="test")
        assert len(reloaded) == 0

    def test_empty_list(self, tmp_path):
        """Test handling of empty lists."""
        test_yaml = tmp_path / "empty_list.yaml"
        test_yaml.write_text("items: []")

        config = load_yaml(str(test_yaml), category="test")
        assert isinstance(config["items"], ListWithProvenance)
        assert len(config["items"]) == 0

    def test_single_value(self, tmp_path):
        """Test single top-level value."""
        test_yaml = tmp_path / "single.yaml"
        test_yaml.write_text("single_key: single_value")

        config = load_yaml(str(test_yaml), category="test")
        assert "single_key" in config
        assert config["single_key"] == "single_value"

    def test_unicode_values(self, tmp_path):
        """Test handling of Unicode characters."""
        test_yaml = tmp_path / "unicode.yaml"
        test_yaml.write_text("""
greeting: Hello 世界
emoji: 🎉🎊
german: Schöne Grüße
""")

        config = load_yaml(str(test_yaml), category="test")
        assert config["greeting"] == "Hello 世界"
        assert config["emoji"] == "🎉🎊"
        assert config["german"] == "Schöne Grüße"

        # Round-trip
        output = tmp_path / "output.yaml"
        dump_yaml(config, str(output))
        reloaded = load_yaml(str(output), category="test")
        assert reloaded["greeting"] == "Hello 世界"


class TestCleanProvenance:
    """Test provenance cleaning utilities."""

    def test_clean_provenance_removes_wrappers(self, tmp_path):
        """Test that clean_provenance removes all wrapper types."""
        test_yaml = tmp_path / "test.yaml"
        test_yaml.write_text("""
key: value
nested:
  item: data
list:
  - one
  - two
""")

        config = load_yaml(str(test_yaml), category="test")

        # Clean provenance
        cleaned = clean_provenance(config)

        # Verify it's a plain dict
        assert type(cleaned) is dict
        assert type(cleaned["nested"]) is dict
        assert type(cleaned["list"]) is list

        # Verify data is preserved
        assert cleaned["key"] == "value"
        assert cleaned["nested"]["item"] == "data"
        assert cleaned["list"] == ["one", "two"]


# Performance tests (optional, for later optimization)
class TestPerformance:
    """Basic performance regression tests."""

    @pytest.mark.slow
    def test_large_config_load_performance(self, tmp_path):
        """Test loading large configuration (1000+ keys)."""
        # Create large YAML
        large_yaml = tmp_path / "large.yaml"
        with open(large_yaml, "w") as f:
            for i in range(1000):
                f.write(f"key_{i}: value_{i}\n")

        import time

        start = time.time()
        config = load_yaml(str(large_yaml), category="test")
        elapsed = time.time() - start

        # Should load in reasonable time (< 1 second for 1000 keys)
        assert elapsed < 1.0, f"Large config took {elapsed:.2f}s to load"
        assert len(config) == 1000

    @pytest.mark.slow
    def test_deep_nesting_performance(self, tmp_path):
        """Test performance with deeply nested structures."""
        # Create deeply nested YAML
        deep_yaml = tmp_path / "deep.yaml"
        content = "root:\n"
        indent = "  "
        for i in range(50):
            content += indent * (i + 1) + f"level{i}:\n"
        content += indent * 51 + "value: deep_value"

        deep_yaml.write_text(content)

        import time

        start = time.time()
        config = load_yaml(str(deep_yaml), category="test")
        elapsed = time.time() - start

        # Should handle deep nesting efficiently
        assert elapsed < 0.5, f"Deep nesting took {elapsed:.2f}s to load"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
