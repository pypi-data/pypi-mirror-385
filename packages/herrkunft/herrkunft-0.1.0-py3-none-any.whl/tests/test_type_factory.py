"""
Tests for the TypeWrapperFactory.

This module tests the factory pattern for dynamically creating provenance
wrappers for arbitrary types.
"""

from herrkunft.core.provenance import Provenance
from herrkunft.types.base import HasProvenance
from herrkunft.types.factory import TypeWrapperFactory, wrap_with_provenance
from herrkunft.types.wrappers import (
    BoolWithProvenance,
    IntWithProvenance,
    NoneWithProvenance,
    StrWithProvenance,
)


class TestTypeWrapperFactory:
    """Tests for TypeWrapperFactory class."""

    def test_wrap_string(self):
        """Test wrapping a string value."""
        wrapped = TypeWrapperFactory.wrap("hello", {"category": "defaults"})

        assert wrapped == "hello"
        assert isinstance(wrapped, str)
        assert isinstance(wrapped, HasProvenance)
        assert wrapped.provenance.current.category == "defaults"

    def test_wrap_integer(self):
        """Test wrapping an integer value."""
        wrapped = TypeWrapperFactory.wrap(42, {"category": "defaults"})

        assert wrapped == 42
        assert isinstance(wrapped, int)
        assert isinstance(wrapped, HasProvenance)
        assert wrapped.provenance.current.category == "defaults"

    def test_wrap_float(self):
        """Test wrapping a float value."""
        wrapped = TypeWrapperFactory.wrap(3.14, {"category": "defaults"})

        assert wrapped == 3.14
        assert isinstance(wrapped, float)
        assert isinstance(wrapped, HasProvenance)
        assert wrapped.provenance.current.category == "defaults"

    def test_wrap_bool_true(self):
        """Test wrapping True value."""
        wrapped = TypeWrapperFactory.wrap(True, {"category": "defaults"})

        assert wrapped == True
        assert bool(wrapped) is True
        assert isinstance(wrapped, BoolWithProvenance)
        assert isinstance(wrapped, HasProvenance)
        assert wrapped.provenance.current.category == "defaults"

    def test_wrap_bool_false(self):
        """Test wrapping False value."""
        wrapped = TypeWrapperFactory.wrap(False, {"category": "defaults"})

        assert wrapped == False
        assert bool(wrapped) is False
        assert isinstance(wrapped, BoolWithProvenance)

    def test_wrap_none(self):
        """Test wrapping None value."""
        wrapped = TypeWrapperFactory.wrap(None, {"category": "defaults"})

        assert wrapped == None
        assert isinstance(wrapped, NoneWithProvenance)
        assert isinstance(wrapped, HasProvenance)
        assert wrapped.provenance.current.category == "defaults"

    def test_wrap_without_provenance(self):
        """Test wrapping values without provenance."""
        str_wrapped = TypeWrapperFactory.wrap("test")
        int_wrapped = TypeWrapperFactory.wrap(123)

        assert str_wrapped == "test"
        assert int_wrapped == 123
        assert len(str_wrapped.provenance) == 0
        assert len(int_wrapped.provenance) == 0

    def test_wrap_already_wrapped(self):
        """Test wrapping an already wrapped value."""
        first_wrap = TypeWrapperFactory.wrap("test", {"category": "defaults"})
        second_wrap = TypeWrapperFactory.wrap(first_wrap, {"category": "runtime"})

        # Should return the same object but with updated provenance
        assert second_wrap is first_wrap
        assert second_wrap.provenance.current.category == "runtime"

    def test_wrap_already_wrapped_without_new_provenance(self):
        """Test wrapping an already wrapped value without new provenance."""
        first_wrap = TypeWrapperFactory.wrap("test", {"category": "defaults"})
        second_wrap = TypeWrapperFactory.wrap(first_wrap)

        # Should return the same object with unchanged provenance
        assert second_wrap is first_wrap
        assert second_wrap.provenance.current.category == "defaults"

    def test_wrap_with_provenance_object(self):
        """Test wrapping with a Provenance object."""
        prov = Provenance({"category": "components", "line": 42})
        wrapped = TypeWrapperFactory.wrap("test", prov)

        assert wrapped.provenance is prov
        assert wrapped.provenance.current.line == 42

    def test_wrap_with_list_provenance(self):
        """Test wrapping with a list of provenance steps."""
        prov_list = [
            {"category": "defaults", "line": 1},
            {"category": "runtime", "line": 10},
        ]
        wrapped = TypeWrapperFactory.wrap(42, prov_list)

        assert len(wrapped.provenance) == 2
        assert wrapped.provenance[0].category == "defaults"
        assert wrapped.provenance[1].category == "runtime"

    def test_class_caching(self):
        """Test that wrapper classes are cached."""
        # Clear cache first
        TypeWrapperFactory.clear_cache()

        # Predefined types like str are not cached in _class_cache
        # They're in _predefined_wrappers instead. Test with bytes which is dynamic.
        wrapped1 = TypeWrapperFactory.wrap(b"test1")
        class1 = type(wrapped1)

        # Second wrap should use cached class
        wrapped2 = TypeWrapperFactory.wrap(b"test2")
        class2 = type(wrapped2)

        assert class1 is class2
        assert bytes in TypeWrapperFactory._class_cache

    def test_clear_cache(self):
        """Test clearing the wrapper class cache."""
        # Predefined wrappers aren't cached, use bytes which is dynamic
        TypeWrapperFactory.wrap(b"test")
        assert len(TypeWrapperFactory._class_cache) > 0

        TypeWrapperFactory.clear_cache()
        assert len(TypeWrapperFactory._class_cache) == 0

    def test_get_wrapper_class_str(self):
        """Test getting wrapper class for str."""
        wrapper_class = TypeWrapperFactory.get_wrapper_class(str)

        assert wrapper_class is StrWithProvenance
        obj = wrapper_class("hello", {"category": "defaults"})
        assert isinstance(obj, str)
        assert obj.provenance.current.category == "defaults"

    def test_get_wrapper_class_int(self):
        """Test getting wrapper class for int."""
        wrapper_class = TypeWrapperFactory.get_wrapper_class(int)

        assert wrapper_class is IntWithProvenance
        obj = wrapper_class(42, {"category": "defaults"})
        assert isinstance(obj, int)

    def test_get_wrapper_class_bool(self):
        """Test getting wrapper class for bool."""
        wrapper_class = TypeWrapperFactory.get_wrapper_class(bool)

        assert wrapper_class is BoolWithProvenance

    def test_get_wrapper_class_none_type(self):
        """Test getting wrapper class for NoneType."""
        wrapper_class = TypeWrapperFactory.get_wrapper_class(type(None))

        assert wrapper_class is NoneWithProvenance

    def test_is_wrapped_true(self):
        """Test is_wrapped returns True for wrapped values."""
        wrapped_str = TypeWrapperFactory.wrap("test")
        wrapped_int = TypeWrapperFactory.wrap(42)
        wrapped_bool = TypeWrapperFactory.wrap(True)

        assert TypeWrapperFactory.is_wrapped(wrapped_str)
        assert TypeWrapperFactory.is_wrapped(wrapped_int)
        assert TypeWrapperFactory.is_wrapped(wrapped_bool)

    def test_is_wrapped_false(self):
        """Test is_wrapped returns False for unwrapped values."""
        assert not TypeWrapperFactory.is_wrapped("test")
        assert not TypeWrapperFactory.is_wrapped(42)
        assert not TypeWrapperFactory.is_wrapped(True)
        assert not TypeWrapperFactory.is_wrapped(None)

    def test_wrap_custom_type(self):
        """Test wrapping a custom class."""

        class CustomClass:
            def __init__(self, value):
                self.custom_value = value

        obj = CustomClass("test")
        wrapped = TypeWrapperFactory.wrap(obj, {"category": "custom"})

        # Should still have the custom attribute
        assert wrapped.custom_value == "test"
        assert isinstance(wrapped, CustomClass)
        assert isinstance(wrapped, HasProvenance)
        assert wrapped.provenance.current.category == "custom"

    def test_wrap_bytes(self):
        """Test wrapping bytes type."""
        data = b"hello"
        wrapped = TypeWrapperFactory.wrap(data, {"category": "defaults"})

        assert wrapped == b"hello"
        assert isinstance(wrapped, bytes)
        assert isinstance(wrapped, HasProvenance)

    def test_wrap_tuple(self):
        """Test wrapping tuple type."""
        data = (1, 2, 3)
        wrapped = TypeWrapperFactory.wrap(data, {"category": "defaults"})

        assert wrapped == (1, 2, 3)
        assert isinstance(wrapped, tuple)
        assert isinstance(wrapped, HasProvenance)


class TestWrapWithProvenanceFunction:
    """Tests for the wrap_with_provenance convenience function."""

    def test_function_alias(self):
        """Test that wrap_with_provenance wraps TypeWrapperFactory.wrap."""
        # wrap_with_provenance is a function wrapper, not a direct alias
        # Test that it behaves the same way
        value1 = wrap_with_provenance("test", {"category": "defaults"})
        value2 = TypeWrapperFactory.wrap("test", {"category": "defaults"})

        assert type(value1) == type(value2)
        assert value1 == value2

    def test_basic_usage(self):
        """Test basic usage of wrap_with_provenance function."""
        wrapped = wrap_with_provenance("hello", {"category": "defaults"})

        assert wrapped == "hello"
        assert isinstance(wrapped, str)
        assert wrapped.provenance.current.category == "defaults"

    def test_import_from_types_module(self):
        """Test importing from types module."""
        from herrkunft.types import wrap_with_provenance as wrap

        wrapped = wrap(42, {"line": 10})
        assert wrapped == 42
        assert wrapped.provenance.current.line == 10


class TestDynamicWrapperCreation:
    """Tests for dynamically created wrapper classes."""

    def test_dynamic_class_naming(self):
        """Test that dynamic wrapper classes have appropriate names."""
        TypeWrapperFactory.clear_cache()

        wrapped_str = TypeWrapperFactory.wrap("test")
        wrapped_bytes = TypeWrapperFactory.wrap(b"test")

        assert "WithProvenance" in type(wrapped_str).__name__
        assert "WithProvenance" in type(wrapped_bytes).__name__

    def test_dynamic_class_has_provenance_mixin(self):
        """Test that dynamic classes include ProvenanceMixin."""

        wrapped = TypeWrapperFactory.wrap(b"test")

        # Check that ProvenanceMixin methods are available
        assert hasattr(wrapped, "_init_provenance")
        assert hasattr(wrapped, "provenance")

    def test_dynamic_wrapper_behavior(self):
        """Test that dynamically created wrappers behave like original type."""
        original_bytes = b"hello world"
        wrapped_bytes = TypeWrapperFactory.wrap(original_bytes, {"category": "test"})

        # Should support bytes operations
        assert wrapped_bytes.upper() == b"HELLO WORLD"
        assert wrapped_bytes.startswith(b"hello")
        assert len(wrapped_bytes) == len(original_bytes)

    def test_wrapper_class_reuse(self):
        """Test that the same wrapper class is reused for the same type."""
        TypeWrapperFactory.clear_cache()

        obj1 = TypeWrapperFactory.wrap(b"first")
        obj2 = TypeWrapperFactory.wrap(b"second")

        assert type(obj1) is type(obj2)
        # But they are different instances
        assert obj1 is not obj2
        assert obj1 != obj2

    def test_multiple_custom_types(self):
        """Test wrapping multiple different custom types."""

        class Type1:
            pass

        class Type2:
            pass

        obj1 = Type1()
        obj2 = Type2()

        wrapped1 = TypeWrapperFactory.wrap(obj1)
        wrapped2 = TypeWrapperFactory.wrap(obj2)

        assert isinstance(wrapped1, Type1)
        assert isinstance(wrapped2, Type2)
        assert type(wrapped1) is not type(wrapped2)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_wrap_complex_number(self):
        """Test wrapping complex number."""
        num = complex(1, 2)
        wrapped = TypeWrapperFactory.wrap(num, {"category": "test"})

        assert wrapped == complex(1, 2)
        assert isinstance(wrapped, complex)
        assert isinstance(wrapped, HasProvenance)

    def test_wrap_zero_values(self):
        """Test wrapping zero/empty values."""
        zero_int = TypeWrapperFactory.wrap(0)
        zero_float = TypeWrapperFactory.wrap(0.0)
        empty_str = TypeWrapperFactory.wrap("")

        assert zero_int == 0
        assert zero_float == 0.0
        assert empty_str == ""
        assert isinstance(zero_int, HasProvenance)
        assert isinstance(zero_float, HasProvenance)
        assert isinstance(empty_str, HasProvenance)

    def test_wrap_negative_values(self):
        """Test wrapping negative values."""
        neg_int = TypeWrapperFactory.wrap(-42, {"category": "test"})
        neg_float = TypeWrapperFactory.wrap(-3.14, {"category": "test"})

        assert neg_int == -42
        assert neg_float == -3.14
        assert neg_int.provenance.current.category == "test"

    def test_provenance_persistence(self):
        """Test that provenance persists through wrapper lifecycle."""
        prov_data = {
            "category": "components",
            "subcategory": "fesom",
            "yaml_file": "/path/to/config.yaml",
            "line": 42,
            "col": 10,
        }

        wrapped = TypeWrapperFactory.wrap("test", prov_data)

        # Verify all provenance fields
        assert wrapped.provenance.current.category == "components"
        assert wrapped.provenance.current.subcategory == "fesom"
        assert wrapped.provenance.current.yaml_file == "/path/to/config.yaml"
        assert wrapped.provenance.current.line == 42
        assert wrapped.provenance.current.col == 10

        # Modify value reference (doesn't affect provenance)
        value_copy = wrapped
        assert value_copy.provenance.current.line == 42

    def test_wrapper_with_none_provenance(self):
        """Test wrapping with explicit None provenance."""
        wrapped = TypeWrapperFactory.wrap("test", None)

        assert wrapped == "test"
        assert len(wrapped.provenance) == 0
        assert wrapped.provenance.current is None


class TestProvenanceUpdateThroughFactory:
    """Tests for updating provenance through factory wrapping."""

    def test_update_provenance_on_wrapped_value(self):
        """Test updating provenance by wrapping an already wrapped value."""
        first = TypeWrapperFactory.wrap("test", {"category": "defaults", "line": 1})
        assert first.provenance.current.category == "defaults"

        # Wrap again with new provenance
        second = TypeWrapperFactory.wrap(first, {"category": "runtime", "line": 10})

        # Should be the same object
        assert second is first
        # But with updated provenance
        assert second.provenance.current.category == "runtime"
        assert second.provenance.current.line == 10

    def test_update_with_provenance_object(self):
        """Test updating with a Provenance object."""
        wrapped = TypeWrapperFactory.wrap("test", {"category": "defaults"})

        new_prov = Provenance(
            [{"category": "defaults"}, {"category": "runtime", "modified_by": "func"}]
        )

        # Wrap again with Provenance object
        TypeWrapperFactory.wrap(wrapped, new_prov)

        assert len(wrapped.provenance) == 2
        assert wrapped.provenance[1].modified_by == "func"
