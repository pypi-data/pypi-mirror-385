"""
Tests for core provenance functionality.

Tests the Provenance and ProvenanceStep classes including:
- Initialization from various input types
- History tracking and modification
- Extension and marking operations
- Serialization and conversion
"""

import pytest

from herrkunft.core import Provenance, ProvenanceStep


class TestProvenanceStep:
    """Tests for ProvenanceStep class."""

    def test_create_minimal_step(self):
        """Test creating a minimal provenance step."""
        step = ProvenanceStep()
        assert step.category is None
        assert step.yaml_file is None
        assert step.from_choose == []

    def test_create_full_step(self):
        """Test creating a complete provenance step."""
        step = ProvenanceStep(
            category="components",
            subcategory="fesom",
            yaml_file="/path/to/config.yaml",
            line=42,
            col=10,
        )
        assert step.category == "components"
        assert step.subcategory == "fesom"
        assert step.yaml_file == "/path/to/config.yaml"
        assert step.line == 42
        assert step.col == 10

    def test_step_with_choose_history(self):
        """Test step with choose block history."""
        step = ProvenanceStep(
            category="components",
            from_choose=[
                {"choose_key": "resolution", "chosen_value": "high"},
                {"choose_key": "platform", "chosen_value": "linux"},
            ],
        )
        assert len(step.from_choose) == 2
        assert step.from_choose[0]["choose_key"] == "resolution"

    def test_step_dict_conversion(self):
        """Test converting step to dictionary."""
        step = ProvenanceStep(
            category="defaults", yaml_file="config.yaml", line=10, col=None
        )
        d = step.dict(exclude_none=True)
        assert "category" in d
        assert "yaml_file" in d
        assert "line" in d
        assert "col" not in d  # Excluded because None

    def test_step_update(self):
        """Test updating step fields."""
        step = ProvenanceStep(category="defaults")
        step.update({"modified_by": "my_function", "line": 100})
        assert step.modified_by == "my_function"
        assert step.line == 100

    def test_step_allows_extra_fields(self):
        """Test that extra fields are allowed."""
        step = ProvenanceStep(category="defaults", custom_field="custom_value")
        assert step.custom_field == "custom_value"  # type: ignore

    def test_line_col_validation(self):
        """Test that line and column numbers must be >= 1."""
        with pytest.raises(ValueError):
            ProvenanceStep(line=0)
        with pytest.raises(ValueError):
            ProvenanceStep(col=-1)


class TestProvenance:
    """Tests for Provenance class."""

    def test_create_empty(self):
        """Test creating empty provenance."""
        prov = Provenance(None)
        assert len(prov) == 0
        assert prov.current is None

    def test_create_from_dict(self):
        """Test creating provenance from dictionary."""
        prov = Provenance({"category": "defaults", "yaml_file": "test.yaml"})
        assert len(prov) == 1
        assert prov.current.category == "defaults"
        assert prov.current.yaml_file == "test.yaml"

    def test_create_from_step(self):
        """Test creating provenance from ProvenanceStep."""
        step = ProvenanceStep(category="components", line=42)
        prov = Provenance(step)
        assert len(prov) == 1
        assert prov[0] is step

    def test_create_from_list_of_dicts(self):
        """Test creating provenance from list of dictionaries."""
        prov = Provenance(
            [{"category": "defaults"}, {"category": "runtime", "modified_by": "func"}]
        )
        assert len(prov) == 2
        assert prov[0].category == "defaults"
        assert prov[1].category == "runtime"
        assert prov[1].modified_by == "func"

    def test_create_from_list_of_steps(self):
        """Test creating provenance from list of ProvenanceSteps."""
        steps = [
            ProvenanceStep(category="defaults"),
            ProvenanceStep(category="runtime"),
        ]
        prov = Provenance(steps)
        assert len(prov) == 2
        assert prov[0].category == "defaults"

    def test_current_property(self):
        """Test current property returns last step."""
        prov = Provenance([{"category": "a"}, {"category": "b"}])
        assert prov.current.category == "b"

    def test_append_modified_by(self):
        """Test append_modified_by duplicates and marks step."""
        prov = Provenance({"category": "defaults", "yaml_file": "test.yaml"})
        assert len(prov) == 1

        prov.append_modified_by("my_function")
        assert len(prov) == 2
        assert prov[1].modified_by == "my_function"
        assert prov[1].category == "defaults"  # Copied from original
        assert prov[1].yaml_file == "test.yaml"

    def test_append_modified_by_on_empty(self):
        """Test append_modified_by on empty provenance."""
        prov = Provenance(None)
        prov.append_modified_by("func")
        assert len(prov) == 1
        assert prov[0].modified_by == "func"

    def test_extend_and_mark_different(self):
        """Test extending with another provenance."""
        prov1 = Provenance({"category": "defaults"})
        prov2 = Provenance([{"category": "runtime", "line": 10}])

        prov1.extend_and_mark(prov2, "dict.__setitem__")

        assert len(prov1) == 2
        assert prov1[0].category == "defaults"
        assert prov1[1].category == "runtime"
        assert prov1[1].extended_by == "dict.__setitem__"

    def test_extend_and_mark_self(self):
        """Test extending with self just marks as modified."""
        prov = Provenance({"category": "defaults"})
        prov.extend_and_mark(prov, "self_reference")

        assert len(prov) == 2
        assert prov[1].modified_by == "self_reference"

    def test_to_dict(self):
        """Test converting provenance to list of dicts."""
        prov = Provenance(
            [{"category": "defaults", "line": 1}, {"category": "runtime", "col": 5}]
        )
        dicts = prov.to_dict()

        assert len(dicts) == 2
        assert dicts[0]["category"] == "defaults"
        assert dicts[0]["line"] == 1
        assert dicts[1]["col"] == 5

    def test_to_json(self):
        """Test converting provenance to JSON string."""
        prov = Provenance({"category": "defaults", "yaml_file": "test.yaml"})
        json_str = prov.to_json()

        assert '"category": "defaults"' in json_str
        assert '"yaml_file": "test.yaml"' in json_str

    def test_copy_shallow(self):
        """Test shallow copy of provenance."""
        prov = Provenance({"category": "defaults"})
        prov_copy = prov.copy(deep=False)

        assert len(prov_copy) == 1
        assert prov_copy[0] is prov[0]  # Same object

    def test_copy_deep(self):
        """Test deep copy of provenance."""
        prov = Provenance({"category": "defaults"})
        prov_copy = prov.copy(deep=True)

        assert len(prov_copy) == 1
        assert prov_copy[0] is not prov[0]  # Different objects
        assert prov_copy[0].category == prov[0].category

    def test_repr(self):
        """Test string representation."""
        prov = Provenance(
            {"category": "components", "yaml_file": "config.yaml", "line": 42}
        )
        repr_str = repr(prov)

        assert "Provenance" in repr_str
        assert "1 steps" in repr_str
        assert "category=components" in repr_str
        assert "line=42" in repr_str


class TestProvenanceIntegration:
    """Integration tests for provenance tracking."""

    def test_complete_modification_history(self):
        """Test tracking complete modification history."""
        # Original value from config file
        prov = Provenance(
            {"category": "defaults", "yaml_file": "defaults.yaml", "line": 10}
        )

        # Modified by first function
        prov.append_modified_by("parse_config")

        # Overridden by runtime value
        runtime_prov = Provenance(
            {"category": "runtime", "yaml_file": "runtime.yaml", "line": 5}
        )
        prov.extend_and_mark(runtime_prov, "merge_configs")

        # Final modification
        prov.append_modified_by("apply_overrides")

        # Verify complete history
        assert len(prov) == 4
        assert prov[0].category == "defaults"
        assert prov[1].modified_by == "parse_config"
        assert prov[2].category == "runtime"
        assert prov[2].extended_by == "merge_configs"
        assert prov[3].modified_by == "apply_overrides"

    def test_choose_block_tracking(self):
        """Test tracking choose block selections."""
        prov = Provenance(
            {
                "category": "components",
                "yaml_file": "component.yaml",
                "line": 20,
                "from_choose": [{"choose_key": "resolution", "chosen_value": "high"}],
            }
        )

        # Add nested choose
        prov.append_modified_by("resolve_choose")
        prov.current.from_choose.append(
            {"choose_key": "platform", "chosen_value": "linux"}
        )

        assert len(prov.current.from_choose) == 2
        assert prov.current.from_choose[0]["choose_key"] == "resolution"
        assert prov.current.from_choose[1]["choose_key"] == "platform"
