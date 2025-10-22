"""
Tests for type wrapper implementations.

This module tests the concrete wrapper classes for bool, None, str, int, and float
to ensure they behave correctly while maintaining provenance tracking.
"""

import pytest

from herrkunft.core.provenance import Provenance, ProvenanceStep
from herrkunft.types.wrappers import (
    BoolWithProvenance,
    FloatWithProvenance,
    IntWithProvenance,
    NoneWithProvenance,
    StrWithProvenance,
)


class TestBoolWithProvenance:
    """Tests for BoolWithProvenance wrapper."""

    def test_creation_with_true(self):
        """Test creating a BoolWithProvenance with True value."""
        prov_data = {"category": "defaults", "line": 42}
        val = BoolWithProvenance(True, prov_data)

        assert val.value is True
        assert bool(val) is True
        assert val.provenance is not None
        assert val.provenance.current.category == "defaults"
        assert val.provenance.current.line == 42

    def test_creation_with_false(self):
        """Test creating a BoolWithProvenance with False value."""
        val = BoolWithProvenance(False)

        assert val.value is False
        assert bool(val) is False
        assert len(val.provenance) == 0

    def test_boolean_conversion(self):
        """Test that BoolWithProvenance converts to bool correctly."""
        true_val = BoolWithProvenance(True)
        false_val = BoolWithProvenance(False)

        assert bool(true_val) is True
        assert bool(false_val) is False

        # Test in conditional
        if true_val:
            assert True
        else:
            pytest.fail("true_val should be truthy")

        if not false_val:
            assert True
        else:
            pytest.fail("false_val should be falsy")

    def test_equality_with_bool(self):
        """Test equality comparison with regular bool."""
        true_val = BoolWithProvenance(True)
        false_val = BoolWithProvenance(False)

        assert true_val == True
        assert true_val != False
        assert false_val == False
        assert false_val != True

    def test_equality_with_other_wrapped(self):
        """Test equality comparison with another BoolWithProvenance."""
        val1 = BoolWithProvenance(True, {"category": "a"})
        val2 = BoolWithProvenance(True, {"category": "b"})
        val3 = BoolWithProvenance(False)

        assert val1 == val2  # Same value, different provenance
        assert val1 != val3  # Different values

    def test_hash(self):
        """Test that BoolWithProvenance is hashable."""
        true_val = BoolWithProvenance(True)
        false_val = BoolWithProvenance(False)

        assert hash(true_val) == hash(True)
        assert hash(false_val) == hash(False)

        # Test in set
        bool_set = {true_val, false_val}
        assert len(bool_set) == 2

    def test_isinstance_bool(self):
        """Test that isinstance check works with bool."""
        val = BoolWithProvenance(True)

        # Due to __class__ override, isinstance should return True
        assert isinstance(val, bool)

    def test_repr_and_str(self):
        """Test string representation."""
        true_val = BoolWithProvenance(True)
        false_val = BoolWithProvenance(False)

        assert repr(true_val) == "True"
        assert repr(false_val) == "False"
        assert str(true_val) == "True"
        assert str(false_val) == "False"

    def test_provenance_modification(self):
        """Test modifying provenance after creation."""
        val = BoolWithProvenance(True, {"category": "defaults"})

        # Add a modification
        val.provenance.append_modified_by("my_function")

        assert len(val.provenance) == 2
        assert val.provenance[0].category == "defaults"
        assert val.provenance[1].modified_by == "my_function"


class TestNoneWithProvenance:
    """Tests for NoneWithProvenance wrapper."""

    def test_creation(self):
        """Test creating a NoneWithProvenance."""
        prov_data = {"category": "defaults", "line": 10}
        val = NoneWithProvenance(None, prov_data)

        assert val.value is None
        assert val.provenance is not None
        assert val.provenance.current.category == "defaults"

    def test_creation_without_provenance(self):
        """Test creating NoneWithProvenance without provenance."""
        val = NoneWithProvenance()

        assert val.value is None
        assert len(val.provenance) == 0

    def test_boolean_conversion(self):
        """Test that NoneWithProvenance is falsy."""
        val = NoneWithProvenance()

        assert bool(val) is False

        if not val:
            assert True
        else:
            pytest.fail("NoneWithProvenance should be falsy")

    def test_equality_with_none(self):
        """Test equality comparison with None."""
        val = NoneWithProvenance()

        assert val == None
        assert val is not None  # Identity check should fail
        assert not (val != None)

    def test_equality_with_other_wrapped(self):
        """Test equality with another NoneWithProvenance."""
        val1 = NoneWithProvenance(None, {"category": "a"})
        val2 = NoneWithProvenance(None, {"category": "b"})

        assert val1 == val2  # Both are None

    def test_inequality_with_non_none(self):
        """Test inequality with non-None values."""
        val = NoneWithProvenance()

        assert val != 0
        assert val != False
        assert val != ""
        assert val != []

    def test_hash(self):
        """Test that NoneWithProvenance is hashable."""
        val = NoneWithProvenance()

        assert hash(val) == hash(None)

        # Test in set
        none_set = {val, NoneWithProvenance()}
        assert len(none_set) == 1  # All None values hash the same

    def test_isinstance_none_type(self):
        """Test that isinstance check works with NoneType."""
        val = NoneWithProvenance()

        # Due to __class__ override, isinstance should return True
        assert isinstance(val, type(None))

    def test_repr_and_str(self):
        """Test string representation."""
        val = NoneWithProvenance()

        assert repr(val) == "None"
        assert str(val) == "None"


class TestStrWithProvenance:
    """Tests for StrWithProvenance wrapper."""

    def test_creation(self):
        """Test creating a StrWithProvenance."""
        prov_data = {"category": "defaults", "yaml_file": "config.yaml"}
        val = StrWithProvenance("hello", prov_data)

        assert val == "hello"
        assert val.value == "hello"
        assert val.provenance.current.category == "defaults"

    def test_isinstance_str(self):
        """Test that isinstance check works with str."""
        val = StrWithProvenance("test")

        assert isinstance(val, str)

    def test_string_methods(self):
        """Test that string methods work (but lose provenance)."""
        val = StrWithProvenance("hello", {"category": "defaults"})

        # String methods return regular strings
        upper = val.upper()
        assert upper == "HELLO"
        assert isinstance(upper, str)
        # Note: upper() returns a regular str, not StrWithProvenance
        # This is expected behavior for immutable type operations

    def test_concatenation(self):
        """Test string concatenation."""
        val = StrWithProvenance("hello", {"category": "defaults"})

        result = val + " world"
        assert result == "hello world"
        assert isinstance(result, str)

    def test_equality(self):
        """Test equality comparison."""
        val1 = StrWithProvenance("test", {"category": "a"})
        val2 = StrWithProvenance("test", {"category": "b"})
        val3 = StrWithProvenance("other")

        assert val1 == val2  # Same string value
        assert val1 != val3  # Different string value
        assert val1 == "test"  # Equality with regular string

    def test_hash(self):
        """Test that StrWithProvenance is hashable."""
        val = StrWithProvenance("test")

        assert hash(val) == hash("test")

        # Test in dict
        str_dict = {val: "value"}
        assert str_dict["test"] == "value"


class TestIntWithProvenance:
    """Tests for IntWithProvenance wrapper."""

    def test_creation(self):
        """Test creating an IntWithProvenance."""
        prov_data = {"category": "defaults", "line": 5}
        val = IntWithProvenance(42, prov_data)

        assert val == 42
        assert val.value == 42
        assert val.provenance.current.category == "defaults"

    def test_isinstance_int(self):
        """Test that isinstance check works with int."""
        val = IntWithProvenance(42)

        assert isinstance(val, int)

    def test_arithmetic_operations(self):
        """Test arithmetic operations (lose provenance)."""
        val = IntWithProvenance(10, {"category": "defaults"})

        # Arithmetic returns regular ints
        assert val + 5 == 15
        assert val * 2 == 20
        assert val - 3 == 7
        assert val // 2 == 5

    def test_comparison(self):
        """Test comparison operations."""
        val = IntWithProvenance(10)

        assert val > 5
        assert val < 15
        assert val == 10
        assert val != 11
        assert val >= 10
        assert val <= 10

    def test_hash(self):
        """Test that IntWithProvenance is hashable."""
        val = IntWithProvenance(42)

        assert hash(val) == hash(42)

        # Test in set
        int_set = {val, IntWithProvenance(42), IntWithProvenance(43)}
        assert len(int_set) == 2  # 42 appears twice but hashes the same


class TestFloatWithProvenance:
    """Tests for FloatWithProvenance wrapper."""

    def test_creation(self):
        """Test creating a FloatWithProvenance."""
        prov_data = {"category": "defaults"}
        val = FloatWithProvenance(3.14, prov_data)

        assert val == 3.14
        assert val.value == 3.14
        assert val.provenance.current.category == "defaults"

    def test_isinstance_float(self):
        """Test that isinstance check works with float."""
        val = FloatWithProvenance(3.14)

        assert isinstance(val, float)

    def test_arithmetic_operations(self):
        """Test arithmetic operations."""
        val = FloatWithProvenance(2.5, {"category": "defaults"})

        assert val + 1.5 == 4.0
        assert val * 2 == 5.0
        assert abs(val - 0.5 - 2.0) < 0.0001

    def test_comparison(self):
        """Test comparison operations."""
        val = FloatWithProvenance(3.14)

        assert val > 3.0
        assert val < 4.0
        assert val == 3.14
        assert val != 2.71

    def test_hash(self):
        """Test that FloatWithProvenance is hashable."""
        val = FloatWithProvenance(3.14)

        assert hash(val) == hash(3.14)


class TestProvenanceIntegration:
    """Tests for provenance integration across wrapper types."""

    def test_provenance_with_dict_data(self):
        """Test creating wrappers with dict provenance."""
        prov = {
            "category": "components",
            "subcategory": "fesom",
            "yaml_file": "/path/to/config.yaml",
            "line": 42,
            "col": 10,
        }

        val = StrWithProvenance("test", prov)

        assert val.provenance.current.category == "components"
        assert val.provenance.current.subcategory == "fesom"
        assert val.provenance.current.yaml_file == "/path/to/config.yaml"
        assert val.provenance.current.line == 42
        assert val.provenance.current.col == 10

    def test_provenance_with_list_data(self):
        """Test creating wrappers with list of provenance steps."""
        prov = [
            {"category": "defaults", "line": 1},
            {"category": "runtime", "line": 10, "modified_by": "my_func"},
        ]

        val = IntWithProvenance(42, prov)

        assert len(val.provenance) == 2
        assert val.provenance[0].category == "defaults"
        assert val.provenance[1].modified_by == "my_func"

    def test_provenance_with_provenance_object(self):
        """Test creating wrappers with Provenance object."""
        step = ProvenanceStep(category="defaults", line=5)
        prov = Provenance(step)

        val = FloatWithProvenance(3.14, prov)

        assert val.provenance is prov
        assert val.provenance.current.line == 5

    def test_modifying_provenance(self):
        """Test modifying provenance after creation."""
        val = StrWithProvenance("test", {"category": "defaults"})

        # Append modification
        val.provenance.append_modified_by("transform_function")

        assert len(val.provenance) == 2
        assert val.provenance[1].modified_by == "transform_function"

        # Extend with another provenance
        other_prov = Provenance({"category": "runtime"})
        val.provenance.extend_and_mark(other_prov, "merge_function")

        assert len(val.provenance) == 3
        assert val.provenance[2].extended_by == "merge_function"

    def test_empty_provenance(self):
        """Test wrappers with empty provenance."""
        val = BoolWithProvenance(True, None)

        assert len(val.provenance) == 0
        assert val.provenance.current is None

    def test_provenance_setter_validation(self):
        """Test that provenance setter validates input."""
        val = IntWithProvenance(42)

        # Valid: Setting with Provenance object
        new_prov = Provenance({"category": "runtime"})
        val.provenance = new_prov
        assert val.provenance is new_prov

        # Invalid: Setting with non-Provenance object
        with pytest.raises(TypeError):
            val.provenance = {"category": "invalid"}

        with pytest.raises(TypeError):
            val.provenance = "not a provenance"
