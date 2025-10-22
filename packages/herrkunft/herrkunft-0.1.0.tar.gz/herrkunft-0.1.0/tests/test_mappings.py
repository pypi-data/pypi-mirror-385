"""
Tests for DictWithProvenance and ListWithProvenance.

This module tests the mapping types with integrated provenance tracking,
including nested structures, hierarchy resolution, and all dict/list operations.
"""

import copy

import pytest

from herrkunft.core.hierarchy import HierarchyConfig, HierarchyManager
from herrkunft.exceptions import CategoryConflictError, ChooseConflictError
from herrkunft.types.factory import TypeWrapperFactory
from herrkunft.types.mappings import DictWithProvenance, ListWithProvenance


class TestDictWithProvenance:
    """Tests for DictWithProvenance class."""

    def test_init_empty(self):
        """Test creating empty DictWithProvenance."""
        config = DictWithProvenance({}, {})
        assert isinstance(config, dict)
        assert len(config) == 0
        assert hasattr(config, "_hierarchy")
        assert hasattr(config, "_custom_setitem")

    def test_init_with_data_and_provenance(self):
        """Test creating DictWithProvenance with data and provenance."""
        data = {"key1": "value1", "key2": 42}
        prov = {
            "key1": {"category": "defaults", "line": 5},
            "key2": {"category": "defaults", "line": 6},
        }
        config = DictWithProvenance(data, prov)

        assert config["key1"] == "value1"
        assert config["key2"] == 42
        assert hasattr(config["key1"], "provenance")
        assert hasattr(config["key2"], "provenance")
        assert config["key1"].provenance.current.category == "defaults"
        assert config["key1"].provenance.current.line == 5

    def test_nested_dict_creation(self):
        """Test that nested dicts become DictWithProvenance."""
        data = {"outer": {"inner": "value"}}
        prov = {"outer": {"inner": {"category": "defaults", "line": 10}}}
        config = DictWithProvenance(data, prov)

        assert isinstance(config["outer"], DictWithProvenance)
        assert config["outer"]["inner"] == "value"
        assert hasattr(config["outer"]["inner"], "provenance")
        assert config["outer"]["inner"].provenance.current.line == 10

    def test_nested_list_creation(self):
        """Test that nested lists become ListWithProvenance."""
        data = {"items": ["a", "b", "c"]}
        prov = {
            "items": [
                {"category": "defaults", "line": 1},
                {"category": "defaults", "line": 2},
                {"category": "defaults", "line": 3},
            ]
        }
        config = DictWithProvenance(data, prov)

        assert isinstance(config["items"], ListWithProvenance)
        assert len(config["items"]) == 3
        assert config["items"][0] == "a"
        assert hasattr(config["items"][0], "provenance")

    def test_get_provenance(self):
        """Test extracting provenance tree."""
        data = {"key1": "value1", "key2": 42}
        prov = {
            "key1": {"category": "defaults", "yaml_file": "config.yaml", "line": 5},
            "key2": {"category": "components", "yaml_file": "comp.yaml", "line": 10},
        }
        config = DictWithProvenance(data, prov)

        prov_tree = config.get_provenance()

        assert "key1" in prov_tree
        assert "key2" in prov_tree
        assert prov_tree["key1"]["category"] == "defaults"
        assert prov_tree["key1"]["line"] == 5
        assert prov_tree["key2"]["category"] == "components"

    def test_get_provenance_nested(self):
        """Test extracting provenance from nested structure."""
        data = {"db": {"host": "localhost", "port": 5432}}
        prov = {
            "db": {
                "host": {"category": "defaults", "line": 5},
                "port": {"category": "defaults", "line": 6},
            }
        }
        config = DictWithProvenance(data, prov)

        prov_tree = config.get_provenance()

        assert "db" in prov_tree
        assert "host" in prov_tree["db"]
        assert prov_tree["db"]["host"]["category"] == "defaults"
        assert prov_tree["db"]["port"]["line"] == 6

    def test_set_provenance_extend(self):
        """Test set_provenance with extend method."""
        data = {"key1": "value1", "key2": "value2"}
        config = DictWithProvenance(data, {})

        new_prov = {"category": "runscript", "modified_by": "test"}
        config.set_provenance(new_prov, update_method="extend")

        assert config["key1"].provenance.current.category == "runscript"
        assert config["key2"].provenance.current.modified_by == "test"

    def test_set_provenance_update(self):
        """Test set_provenance with update method."""
        data = {"key": "value"}
        prov = {"key": {"category": "defaults", "line": 5}}
        config = DictWithProvenance(data, prov)

        # Update adds fields to last step
        config.set_provenance({"modified_by": "user"}, update_method="update")

        assert config["key"].provenance.current.category == "defaults"
        assert config["key"].provenance.current.modified_by == "user"

    def test_setitem_new_key(self):
        """Test setting new key."""
        config = DictWithProvenance({}, {})
        val = TypeWrapperFactory.wrap("value", {"category": "defaults"})
        config["new_key"] = val

        assert config["new_key"] == "value"
        assert config["new_key"].provenance.current.category == "defaults"

    def test_setitem_higher_category_overrides(self):
        """Test that higher category overrides lower category."""
        config = DictWithProvenance({}, {})

        # Set initial value with defaults category
        val1 = TypeWrapperFactory.wrap("old", {"category": "defaults", "line": 5})
        config["key"] = val1

        # Override with runscript category (higher than defaults)
        val2 = TypeWrapperFactory.wrap("new", {"category": "runscript", "line": 10})
        config["key"] = val2

        assert config["key"] == "new"
        # Should have both provenance steps
        assert len(config["key"].provenance) == 2
        assert config["key"].provenance.current.category == "runscript"

    def test_setitem_lower_category_rejected(self):
        """Test that lower category doesn't override higher category."""
        config = DictWithProvenance({}, {})

        # Set initial value with runscript category (high)
        val1 = TypeWrapperFactory.wrap("original", {"category": "runscript", "line": 5})
        config["key"] = val1

        # Try to override with defaults category (lower)
        val2 = TypeWrapperFactory.wrap("new", {"category": "defaults", "line": 10})
        config["key"] = val2

        # Should keep original value
        assert config["key"] == "original"
        assert config["key"].provenance.current.category == "runscript"

    def test_setitem_same_category_raises_error(self):
        """Test that same category override raises error in strict mode."""
        config = DictWithProvenance({}, {})

        # Set initial value
        val1 = TypeWrapperFactory.wrap("value1", {"category": "components", "line": 5})
        config["key"] = val1

        # Try to override with same category
        val2 = TypeWrapperFactory.wrap("value2", {"category": "components", "line": 10})

        with pytest.raises(CategoryConflictError) as exc_info:
            config["key"] = val2

        assert "key" in str(exc_info.value)
        assert "components" in str(exc_info.value)

    def test_setitem_same_category_allowed_with_config(self):
        """Test same category override when allow_same_level_override=True."""
        hierarchy_config = HierarchyConfig(allow_same_level_override=True)
        hierarchy = HierarchyManager(hierarchy_config)
        config = DictWithProvenance({}, {}, hierarchy_manager=hierarchy)

        # Set initial value
        val1 = TypeWrapperFactory.wrap("value1", {"category": "components"})
        config["key"] = val1

        # Override with same category (should succeed)
        val2 = TypeWrapperFactory.wrap("value2", {"category": "components"})
        config["key"] = val2

        assert config["key"] == "value2"

    def test_setitem_choose_block_override(self):
        """Test that choose block can override at same level."""
        config = DictWithProvenance({}, {})

        # Set initial value
        val1 = TypeWrapperFactory.wrap("value1", {"category": "components", "line": 5})
        config["key"] = val1

        # Override with choose block at same level
        val2 = TypeWrapperFactory.wrap(
            "value2",
            {
                "category": "components",
                "line": 10,
                "from_choose": [{"choose_key": "resolution"}],
            },
        )
        config["key"] = val2

        assert config["key"] == "value2"

    def test_setitem_choose_conflict_raises_error(self):
        """Test that conflicting choose blocks raise error."""
        config = DictWithProvenance({}, {})

        # Set initial value with choose block
        val1 = TypeWrapperFactory.wrap(
            "value1",
            {
                "category": "components",
                "from_choose": [{"choose_key": "resolution"}],
            },
        )
        config["key"] = val1

        # Try to override with different choose block (not nested)
        val2 = TypeWrapperFactory.wrap(
            "value2",
            {
                "category": "components",
                "from_choose": [{"choose_key": "platform"}],
            },
        )

        with pytest.raises(ChooseConflictError) as exc_info:
            config["key"] = val2

        assert "resolution" in str(exc_info.value)
        assert "platform" in str(exc_info.value)

    def test_setitem_nested_choose_allowed(self):
        """Test that nested choose blocks are allowed."""
        config = DictWithProvenance({}, {})

        # Set initial value with choose block
        val1 = TypeWrapperFactory.wrap(
            "value1",
            {
                "category": "components",
                "from_choose": [{"choose_key": "resolution"}],
            },
        )
        config["key"] = val1

        # Override with nested choose block (should succeed)
        val2 = TypeWrapperFactory.wrap(
            "value2",
            {
                "category": "components",
                "from_choose": [
                    {"choose_key": "resolution"},
                    {"choose_key": "platform"},
                ],
            },
        )
        config["key"] = val2

        assert config["key"] == "value2"

    def test_super_setitem(self):
        """Test super_setitem bypasses hierarchy."""
        config = DictWithProvenance({}, {})

        # Set initial value with high category
        val1 = TypeWrapperFactory.wrap("original", {"category": "runscript"})
        config["key"] = val1

        # Force override with super_setitem
        config.super_setitem("key", "forced")

        assert config["key"] == "forced"

    def test_update_method(self):
        """Test dict.update() with provenance."""
        config = DictWithProvenance({}, {})
        val1 = TypeWrapperFactory.wrap("value1", {"category": "defaults"})
        config["key1"] = val1

        # Update with new keys
        config.update({"key2": "value2", "key3": "value3"})

        assert "key2" in config
        assert "key3" in config
        assert config["key2"] == "value2"

    def test_update_extends_provenance(self):
        """Test that update extends provenance for existing keys."""
        config = DictWithProvenance({}, {})
        val1 = TypeWrapperFactory.wrap("original", {"category": "defaults", "line": 5})
        config["key"] = val1

        # Update existing key
        val2 = TypeWrapperFactory.wrap("updated", {"category": "runscript", "line": 10})
        config.update({"key": val2})

        # Provenance should be extended
        assert len(config["key"].provenance) >= 2

    def test_empty_provenance(self):
        """Test handling empty/None provenance."""
        data = {"key": "value"}
        config = DictWithProvenance(data, None)

        assert config["key"] == "value"
        # Should have empty provenance
        assert hasattr(config["key"], "provenance")

    def test_deeply_nested_structure(self):
        """Test deeply nested dict and list structures."""
        data = {"level1": {"level2": {"level3": ["a", "b", {"level4": "value"}]}}}
        prov = {
            "level1": {
                "level2": {
                    "level3": [
                        {"category": "defaults", "line": 1},
                        {"category": "defaults", "line": 2},
                        {"level4": {"category": "defaults", "line": 3}},
                    ]
                }
            }
        }
        config = DictWithProvenance(data, prov)

        # Navigate to deepest value
        deepest = config["level1"]["level2"]["level3"][2]["level4"]
        assert deepest == "value"
        assert hasattr(deepest, "provenance")
        assert deepest.provenance.current.line == 3

    def test_provenance_history_tracking(self):
        """Test that provenance history is correctly tracked."""
        config = DictWithProvenance({}, {})

        # Set initial value
        val1 = TypeWrapperFactory.wrap("v1", {"category": "defaults", "line": 5})
        config["key"] = val1
        assert len(config["key"].provenance) == 1

        # Override with higher category
        val2 = TypeWrapperFactory.wrap("v2", {"category": "components", "line": 10})
        config["key"] = val2
        assert len(config["key"].provenance) == 2

        # Override again with even higher category
        val3 = TypeWrapperFactory.wrap("v3", {"category": "runscript", "line": 15})
        config["key"] = val3
        assert len(config["key"].provenance) == 3

        # Check history
        prov = config["key"].provenance
        assert prov[0].category == "defaults"
        assert prov[1].category == "components"
        assert prov[2].category == "runscript"


class TestListWithProvenance:
    """Tests for ListWithProvenance class."""

    def test_init_empty(self):
        """Test creating empty ListWithProvenance."""
        config = ListWithProvenance([], [])
        assert isinstance(config, list)
        assert len(config) == 0
        assert hasattr(config, "_hierarchy")
        assert hasattr(config, "_custom_setitem")

    def test_init_with_data_and_provenance(self):
        """Test creating ListWithProvenance with data and provenance."""
        data = ["value1", "value2", 42]
        prov = [
            {"category": "defaults", "line": 1},
            {"category": "defaults", "line": 2},
            {"category": "defaults", "line": 3},
        ]
        config = ListWithProvenance(data, prov)

        assert len(config) == 3
        assert config[0] == "value1"
        assert config[1] == "value2"
        assert config[2] == 42
        assert hasattr(config[0], "provenance")
        assert config[0].provenance.current.line == 1

    def test_nested_dict_creation(self):
        """Test that nested dicts become DictWithProvenance."""
        data = [{"key": "value"}]
        prov = [{"key": {"category": "defaults", "line": 5}}]
        config = ListWithProvenance(data, prov)

        assert isinstance(config[0], DictWithProvenance)
        assert config[0]["key"] == "value"
        assert hasattr(config[0]["key"], "provenance")

    def test_nested_list_creation(self):
        """Test that nested lists become ListWithProvenance."""
        data = [["a", "b"], ["c", "d"]]
        prov = [
            [{"category": "defaults", "line": 1}, {"category": "defaults", "line": 2}],
            [{"category": "defaults", "line": 3}, {"category": "defaults", "line": 4}],
        ]
        config = ListWithProvenance(data, prov)

        assert isinstance(config[0], ListWithProvenance)
        assert isinstance(config[1], ListWithProvenance)
        assert config[0][0] == "a"
        assert hasattr(config[0][0], "provenance")

    def test_get_provenance(self):
        """Test extracting provenance list."""
        data = ["value1", "value2"]
        prov = [
            {"category": "defaults", "line": 5},
            {"category": "components", "line": 10},
        ]
        config = ListWithProvenance(data, prov)

        prov_list = config.get_provenance()

        assert len(prov_list) == 2
        assert prov_list[0]["category"] == "defaults"
        assert prov_list[0]["line"] == 5
        assert prov_list[1]["category"] == "components"

    def test_get_provenance_nested(self):
        """Test extracting provenance from nested structure."""
        data = [{"host": "localhost", "port": 5432}]
        prov = [
            {
                "host": {"category": "defaults", "line": 5},
                "port": {"category": "defaults", "line": 6},
            }
        ]
        config = ListWithProvenance(data, prov)

        prov_list = config.get_provenance()

        assert len(prov_list) == 1
        assert "host" in prov_list[0]
        assert prov_list[0]["host"]["category"] == "defaults"
        assert prov_list[0]["port"]["line"] == 6

    def test_set_provenance_extend(self):
        """Test set_provenance with extend method."""
        data = ["value1", "value2"]
        config = ListWithProvenance(data, [])

        new_prov = {"category": "runscript", "modified_by": "test"}
        config.set_provenance(new_prov, update_method="extend")

        assert config[0].provenance.current.category == "runscript"
        assert config[1].provenance.current.modified_by == "test"

    def test_set_provenance_update(self):
        """Test set_provenance with update method."""
        data = ["value"]
        prov = [{"category": "defaults", "line": 5}]
        config = ListWithProvenance(data, prov)

        # Update adds fields to last step
        config.set_provenance({"modified_by": "user"}, update_method="update")

        assert config[0].provenance.current.category == "defaults"
        assert config[0].provenance.current.modified_by == "user"

    def test_setitem_extends_provenance(self):
        """Test that setitem extends provenance."""
        data = ["original"]
        prov = [{"category": "defaults", "line": 5}]
        config = ListWithProvenance(data, prov)

        # Set new value
        val = TypeWrapperFactory.wrap("new", {"category": "runscript", "line": 10})
        config[0] = val

        # Should have both provenance steps
        assert len(config[0].provenance) >= 2

    def test_setitem_without_provenance(self):
        """Test setitem with value that has no provenance."""
        data = ["original"]
        prov = [{"category": "defaults", "line": 5}]
        config = ListWithProvenance(data, prov)

        # Set plain value without provenance
        config[0] = "plain_value"

        # Should still have provenance (from old value)
        assert hasattr(config[0], "provenance")

    def test_super_setitem(self):
        """Test super_setitem bypasses provenance tracking."""
        data = ["original"]
        prov = [{"category": "defaults"}]
        config = ListWithProvenance(data, prov)

        # Force set without provenance tracking
        config.super_setitem(0, "forced")

        assert config[0] == "forced"

    def test_empty_provenance(self):
        """Test handling empty/None provenance."""
        data = ["value1", "value2"]
        config = ListWithProvenance(data, None)

        assert config[0] == "value1"
        # Should have provenance (created during init)
        assert hasattr(config[0], "provenance")

    def test_mismatched_provenance_length(self):
        """Test handling provenance shorter than data."""
        data = ["v1", "v2", "v3"]
        prov = [{"category": "defaults", "line": 1}]  # Only one entry
        config = ListWithProvenance(data, prov)

        # All elements should still be wrapped
        assert len(config) == 3
        assert hasattr(config[0], "provenance")
        assert hasattr(config[1], "provenance")
        assert hasattr(config[2], "provenance")
        # First has provenance
        assert config[0].provenance.current.line == 1

    def test_deeply_nested_structure(self):
        """Test deeply nested list and dict structures."""
        data = [[[{"key": "value"}]]]
        prov = [[[{"key": {"category": "defaults", "line": 5}}]]]
        config = ListWithProvenance(data, prov)

        # Navigate to deepest value
        deepest = config[0][0][0]["key"]
        assert deepest == "value"
        assert hasattr(deepest, "provenance")
        assert deepest.provenance.current.line == 5

    def test_provenance_history_tracking(self):
        """Test that provenance history is correctly tracked."""
        data = ["v1"]
        prov = [{"category": "defaults", "line": 5}]
        config = ListWithProvenance(data, prov)

        assert len(config[0].provenance) == 1

        # Update value
        val2 = TypeWrapperFactory.wrap("v2", {"category": "components", "line": 10})
        config[0] = val2

        # Should have history
        assert len(config[0].provenance) == 2


class TestIntegration:
    """Integration tests for Dict and List with Provenance."""

    def test_mixed_nested_structures(self):
        """Test complex nested structures with both dicts and lists."""
        data = {
            "servers": [
                {"host": "server1", "port": 8080},
                {"host": "server2", "port": 8081},
            ],
            "config": {
                "timeout": 30,
                "retries": [1, 2, 3],
            },
        }
        prov = {
            "servers": [
                {
                    "host": {"category": "defaults", "line": 1},
                    "port": {"category": "defaults", "line": 2},
                },
                {
                    "host": {"category": "defaults", "line": 3},
                    "port": {"category": "defaults", "line": 4},
                },
            ],
            "config": {
                "timeout": {"category": "defaults", "line": 5},
                "retries": [
                    {"category": "defaults", "line": 6},
                    {"category": "defaults", "line": 7},
                    {"category": "defaults", "line": 8},
                ],
            },
        }
        config = DictWithProvenance(data, prov)

        # Verify structure types
        assert isinstance(config["servers"], ListWithProvenance)
        assert isinstance(config["servers"][0], DictWithProvenance)
        assert isinstance(config["config"], DictWithProvenance)
        assert isinstance(config["config"]["retries"], ListWithProvenance)

        # Verify provenance
        assert config["servers"][0]["host"].provenance.current.line == 1
        assert config["config"]["retries"][2].provenance.current.line == 8

    def test_provenance_preserved_through_copy(self):
        """Test that provenance is preserved through deep copy."""
        data = {"key": "value"}
        prov = {"key": {"category": "defaults", "line": 5}}
        config = DictWithProvenance(data, prov)

        # Deep copy
        config_copy = copy.deepcopy(config)

        assert config_copy["key"] == "value"
        assert hasattr(config_copy["key"], "provenance")
        assert config_copy["key"].provenance.current.line == 5

    def test_hierarchy_manager_sharing(self):
        """Test that hierarchy manager is shared in nested structures."""
        hierarchy_config = HierarchyConfig(strict_mode=False)
        hierarchy = HierarchyManager(hierarchy_config)

        data = {"nested": {"key": "value"}}
        prov = {"nested": {"key": {"category": "defaults"}}}
        config = DictWithProvenance(data, prov, hierarchy_manager=hierarchy)

        # Nested dict should share the same hierarchy manager
        assert config["nested"]._hierarchy is hierarchy

    def test_get_provenance_index_parameter(self):
        """Test get_provenance with different index values."""
        data = {"key": "v1"}
        prov = {"key": {"category": "defaults", "line": 5}}
        config = DictWithProvenance(data, prov)

        # Update to create history
        val2 = TypeWrapperFactory.wrap("v2", {"category": "components", "line": 10})
        config["key"] = val2

        # Get first provenance step
        prov_tree_first = config.get_provenance(index=0)
        assert prov_tree_first["key"]["category"] == "defaults"

        # Get last provenance step
        prov_tree_last = config.get_provenance(index=-1)
        assert prov_tree_last["key"]["category"] == "components"

    def test_round_trip_provenance(self):
        """Test extracting and re-applying provenance."""
        data = {"key1": "value1", "key2": "value2"}
        prov = {
            "key1": {"category": "defaults", "line": 5},
            "key2": {"category": "components", "line": 10},
        }
        config = DictWithProvenance(data, prov)

        # Extract provenance
        extracted_prov = config.get_provenance()

        # Create new dict with extracted provenance
        new_data = {"key1": "value1", "key2": "value2"}
        new_config = DictWithProvenance(new_data, extracted_prov)

        # Should have same provenance
        assert new_config["key1"].provenance.current.category == "defaults"
        assert new_config["key2"].provenance.current.category == "components"
