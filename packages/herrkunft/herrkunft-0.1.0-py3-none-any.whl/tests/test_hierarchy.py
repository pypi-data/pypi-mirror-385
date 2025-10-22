"""
Tests for hierarchy management and conflict resolution.

Tests the HierarchyManager class including:
- Category level precedence
- Same-level conflict detection
- Choose block conflict resolution
- Custom hierarchy configurations
"""

from herrkunft.core import (
    CategoryLevel,
    HierarchyConfig,
    HierarchyManager,
    ProvenanceStep,
)
from herrkunft.exceptions import CategoryConflictError, ChooseConflictError


class TestCategoryLevel:
    """Tests for CategoryLevel enum."""

    def test_category_levels_ordered(self):
        """Test that category levels are properly ordered."""
        assert CategoryLevel.UNKNOWN < CategoryLevel.DEFAULTS
        assert CategoryLevel.DEFAULTS < CategoryLevel.COMPONENTS
        assert CategoryLevel.COMPONENTS < CategoryLevel.SETUPS
        assert CategoryLevel.SETUPS < CategoryLevel.RUNSCRIPT
        assert CategoryLevel.RUNSCRIPT < CategoryLevel.COMMAND_LINE
        assert CategoryLevel.COMMAND_LINE < CategoryLevel.BACKEND

    def test_all_levels_present(self):
        """Test that all expected levels are defined."""
        expected_levels = [
            "UNKNOWN",
            "DEFAULTS",
            "OTHER_SOFTWARE",
            "MACHINES",
            "COMPONENTS",
            "SETUPS",
            "COUPLINGS",
            "RUNSCRIPT",
            "COMMAND_LINE",
            "BACKEND",
        ]
        for level in expected_levels:
            assert hasattr(CategoryLevel, level)


class TestHierarchyConfig:
    """Tests for HierarchyConfig."""

    def test_default_config(self):
        """Test default hierarchy configuration."""
        config = HierarchyConfig()
        assert len(config.categories) > 0
        assert config.strict_mode is True
        assert config.allow_same_level_override is False

    def test_custom_config(self):
        """Test custom hierarchy configuration."""
        config = HierarchyConfig(
            categories=["base", "env", "user", "runtime"],
            strict_mode=False,
            allow_same_level_override=True,
        )
        assert config.categories == ["base", "env", "user", "runtime"]
        assert config.strict_mode is False
        assert config.allow_same_level_override is True


class TestHierarchyManager:
    """Tests for HierarchyManager."""

    def test_default_initialization(self):
        """Test initialization with default config."""
        manager = HierarchyManager()
        assert manager.config is not None
        assert manager.config.strict_mode is True

    def test_custom_initialization(self):
        """Test initialization with custom config."""
        config = HierarchyConfig(strict_mode=False)
        manager = HierarchyManager(config)
        assert manager.config.strict_mode is False

    def test_get_level_known_category(self):
        """Test getting level for known categories."""
        manager = HierarchyManager()
        assert manager.get_level("defaults") == CategoryLevel.DEFAULTS
        assert manager.get_level("components") == CategoryLevel.COMPONENTS
        assert manager.get_level("runscript") == CategoryLevel.RUNSCRIPT

    def test_get_level_case_insensitive(self):
        """Test that category lookup is case-insensitive."""
        manager = HierarchyManager()
        assert manager.get_level("DEFAULTS") == manager.get_level("defaults")
        assert manager.get_level("Components") == manager.get_level("components")

    def test_get_level_none_category(self):
        """Test that None category returns BACKEND level."""
        manager = HierarchyManager()
        assert manager.get_level(None) == CategoryLevel.BACKEND

    def test_get_level_unknown_category(self):
        """Test that unknown category returns UNKNOWN level."""
        manager = HierarchyManager()
        assert manager.get_level("nonexistent") == CategoryLevel.UNKNOWN


class TestConflictResolution:
    """Tests for conflict resolution logic."""

    def test_higher_level_overrides_lower(self):
        """Test that higher category levels override lower ones."""
        manager = HierarchyManager()
        old_step = ProvenanceStep(category="defaults")
        new_step = ProvenanceStep(category="components")

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is True
        assert error is None

    def test_lower_level_does_not_override(self):
        """Test that lower category levels cannot override higher ones."""
        manager = HierarchyManager()
        old_step = ProvenanceStep(category="runscript")
        new_step = ProvenanceStep(category="defaults")

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is False
        assert error is None

    def test_same_level_strict_mode_error(self):
        """Test that same level raises error in strict mode."""
        manager = HierarchyManager(HierarchyConfig(strict_mode=True))
        old_step = ProvenanceStep(category="components", yaml_file="old.yaml")
        new_step = ProvenanceStep(category="components", yaml_file="new.yaml")

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is False
        assert error is not None
        assert isinstance(error, CategoryConflictError)

    def test_same_level_non_strict_mode(self):
        """Test same level behavior in non-strict mode."""
        manager = HierarchyManager(HierarchyConfig(strict_mode=False))
        old_step = ProvenanceStep(category="components")
        new_step = ProvenanceStep(category="components")

        should_override, error = manager.should_override(old_step, new_step, "key")

        # In non-strict mode, error is returned but can be ignored
        assert should_override is False

    def test_same_level_allow_override(self):
        """Test same level with allow_same_level_override."""
        manager = HierarchyManager(
            HierarchyConfig(strict_mode=True, allow_same_level_override=True)
        )
        old_step = ProvenanceStep(category="components")
        new_step = ProvenanceStep(category="components")

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is True
        assert error is None


class TestChooseBlockResolution:
    """Tests for choose block conflict resolution."""

    def test_choose_block_can_override_at_same_level(self):
        """Test that choose blocks can override at the same level."""
        manager = HierarchyManager()
        old_step = ProvenanceStep(category="components")
        new_step = ProvenanceStep(
            category="components",
            from_choose=[{"choose_key": "resolution", "chosen_value": "high"}],
        )

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is True
        assert error is None

    def test_nested_choose_allowed(self):
        """Test that nested choose blocks are allowed."""
        manager = HierarchyManager()
        old_step = ProvenanceStep(
            category="components",
            from_choose=[{"choose_key": "resolution", "chosen_value": "high"}],
        )
        new_step = ProvenanceStep(
            category="components",
            from_choose=[
                {"choose_key": "resolution", "chosen_value": "high"},
                {"choose_key": "platform", "chosen_value": "linux"},
            ],
        )

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is True
        assert error is None

    def test_conflicting_choose_blocks_error(self):
        """Test that conflicting choose blocks raise error."""
        manager = HierarchyManager(HierarchyConfig(strict_mode=True))
        old_step = ProvenanceStep(
            category="components",
            from_choose=[{"choose_key": "resolution", "chosen_value": "high"}],
        )
        new_step = ProvenanceStep(
            category="components",
            from_choose=[{"choose_key": "platform", "chosen_value": "linux"}],
        )

        should_override, error = manager.should_override(old_step, new_step, "key")

        assert should_override is False
        assert error is not None
        assert isinstance(error, ChooseConflictError)

    def test_is_nested_choose(self):
        """Test nested choose detection."""
        old_choose = [{"choose_key": "resolution"}]
        new_choose_nested = [
            {"choose_key": "resolution"},
            {"choose_key": "platform"},
        ]
        new_choose_not_nested = [{"choose_key": "platform"}]

        assert HierarchyManager._is_nested_choose(old_choose, new_choose_nested) is True
        assert (
            HierarchyManager._is_nested_choose(old_choose, new_choose_not_nested)
            is False
        )

    def test_is_nested_choose_equal_length(self):
        """Test that equal length choose blocks are considered nested if identical."""
        old_choose = [{"choose_key": "resolution"}]
        new_choose = [{"choose_key": "resolution"}]

        assert HierarchyManager._is_nested_choose(old_choose, new_choose) is True


class TestCustomHierarchy:
    """Tests for custom hierarchy configurations."""

    def test_custom_category_order(self):
        """Test custom category ordering."""
        config = HierarchyConfig(categories=["base", "env", "user", "cli"])
        manager = HierarchyManager(config)

        assert manager.get_level("base") < manager.get_level("env")
        assert manager.get_level("env") < manager.get_level("user")
        assert manager.get_level("user") < manager.get_level("cli")

    def test_custom_hierarchy_override_behavior(self):
        """Test override behavior with custom hierarchy."""
        config = HierarchyConfig(categories=["dev", "staging", "production"])
        manager = HierarchyManager(config)

        dev_step = ProvenanceStep(category="dev")
        prod_step = ProvenanceStep(category="production")

        should_override, _ = manager.should_override(dev_step, prod_step, "key")
        assert should_override is True

        should_override, _ = manager.should_override(prod_step, dev_step, "key")
        assert should_override is False


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_none_categories(self):
        """Test handling of None categories."""
        manager = HierarchyManager()
        old_step = ProvenanceStep(category=None)
        new_step = ProvenanceStep(category="defaults")

        # None is BACKEND level, so defaults cannot override
        should_override, _ = manager.should_override(old_step, new_step, "key")
        assert should_override is False

    def test_empty_choose_lists(self):
        """Test handling of empty choose lists."""
        manager = HierarchyManager()
        old_step = ProvenanceStep(category="components", from_choose=[])
        new_step = ProvenanceStep(category="components", from_choose=[])

        # Both empty, should hit same-level logic
        should_override, error = manager.should_override(old_step, new_step, "key")
        assert should_override is False
        assert isinstance(error, CategoryConflictError)
