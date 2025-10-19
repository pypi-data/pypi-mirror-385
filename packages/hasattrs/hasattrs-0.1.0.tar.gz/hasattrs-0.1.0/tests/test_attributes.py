"""Tests for attribute set definitions."""

from hasattrs.attributes import (
    ASYNC_GENERATOR,
    ASYNC_ITERABLE,
    ASYNC_ITERATOR,
    AWAITABLE,
    CALLABLE,
    COLLECTION,
    CONTAINER,
    COROUTINE,
    GENERATOR,
    HASHABLE,
    ITEMS_VIEW,
    ITERABLE,
    ITERATOR,
    KEYS_VIEW,
    MAPPING,
    MAPPING_VIEW,
    MUTABLE_MAPPING,
    MUTABLE_SEQUENCE,
    MUTABLE_SET,
    REVERSIBLE,
    SEQUENCE,
    SET,
    SIZED,
    VALUES_VIEW,
)


class TestAttributeSets:
    """Test that attribute sets contain the expected attributes."""

    def test_container_attrs(self):
        assert "__contains__" in CONTAINER

    def test_hashable_attrs(self):
        assert "__hash__" in HASHABLE

    def test_iterable_attrs(self):
        assert "__iter__" in ITERABLE

    def test_iterator_attrs(self):
        assert "__iter__" in ITERATOR
        assert "__next__" in ITERATOR

    def test_reversible_attrs(self):
        assert "__iter__" in REVERSIBLE
        assert "__reversed__" in REVERSIBLE

    def test_generator_attrs(self):
        assert "__iter__" in GENERATOR
        assert "__next__" in GENERATOR
        assert "send" in GENERATOR
        assert "throw" in GENERATOR
        assert "close" in GENERATOR

    def test_sized_attrs(self):
        assert "__len__" in SIZED

    def test_callable_attrs(self):
        assert "__call__" in CALLABLE

    def test_collection_attrs(self):
        assert "__len__" in COLLECTION
        assert "__iter__" in COLLECTION
        assert "__contains__" in COLLECTION

    def test_sequence_attrs(self):
        """Test that Sequence has all required attributes including __getitem__."""
        assert "__getitem__" in SEQUENCE
        assert "__len__" in SEQUENCE
        assert "__iter__" in SEQUENCE
        assert "__contains__" in SEQUENCE
        assert "__reversed__" in SEQUENCE
        assert "index" in SEQUENCE
        assert "count" in SEQUENCE

    def test_mutable_sequence_attrs(self):
        assert "__setitem__" in MUTABLE_SEQUENCE
        assert "__delitem__" in MUTABLE_SEQUENCE
        assert "insert" in MUTABLE_SEQUENCE
        assert "append" in MUTABLE_SEQUENCE
        assert "reverse" in MUTABLE_SEQUENCE
        assert "extend" in MUTABLE_SEQUENCE
        assert "pop" in MUTABLE_SEQUENCE
        assert "remove" in MUTABLE_SEQUENCE
        assert "__iadd__" in MUTABLE_SEQUENCE

    def test_set_attrs(self):
        assert "__le__" in SET
        assert "__lt__" in SET
        assert "__eq__" in SET
        assert "__ne__" in SET
        assert "__gt__" in SET
        assert "__ge__" in SET
        assert "isdisjoint" in SET

    def test_mutable_set_attrs(self):
        assert "add" in MUTABLE_SET
        assert "discard" in MUTABLE_SET
        assert "clear" in MUTABLE_SET
        assert "pop" in MUTABLE_SET
        assert "remove" in MUTABLE_SET

    def test_mapping_attrs(self):
        """Test that Mapping has all required attributes including __getitem__."""
        assert "__getitem__" in MAPPING
        assert "__len__" in MAPPING
        assert "__iter__" in MAPPING
        assert "__contains__" in MAPPING
        assert "keys" in MAPPING
        assert "items" in MAPPING
        assert "values" in MAPPING
        assert "get" in MAPPING
        assert "__eq__" in MAPPING
        assert "__ne__" in MAPPING

    def test_mutable_mapping_attrs(self):
        assert "__setitem__" in MUTABLE_MAPPING
        assert "__delitem__" in MUTABLE_MAPPING
        assert "pop" in MUTABLE_MAPPING
        assert "popitem" in MUTABLE_MAPPING
        assert "clear" in MUTABLE_MAPPING
        assert "update" in MUTABLE_MAPPING
        assert "setdefault" in MUTABLE_MAPPING

    def test_mapping_view_attrs(self):
        assert "__len__" in MAPPING_VIEW

    def test_items_view_attrs(self):
        assert "__len__" in ITEMS_VIEW

    def test_keys_view_attrs(self):
        assert "__len__" in KEYS_VIEW

    def test_values_view_attrs(self):
        assert "__len__" in VALUES_VIEW

    def test_awaitable_attrs(self):
        assert "__await__" in AWAITABLE

    def test_coroutine_attrs(self):
        assert "__await__" in COROUTINE
        assert "send" in COROUTINE
        assert "throw" in COROUTINE
        assert "close" in COROUTINE

    def test_async_iterable_attrs(self):
        assert "__aiter__" in ASYNC_ITERABLE

    def test_async_iterator_attrs(self):
        assert "__aiter__" in ASYNC_ITERATOR
        assert "__anext__" in ASYNC_ITERATOR

    def test_async_generator_attrs(self):
        assert "__aiter__" in ASYNC_GENERATOR
        assert "__anext__" in ASYNC_GENERATOR
        assert "asend" in ASYNC_GENERATOR
        assert "athrow" in ASYNC_GENERATOR
        assert "aclose" in ASYNC_GENERATOR
