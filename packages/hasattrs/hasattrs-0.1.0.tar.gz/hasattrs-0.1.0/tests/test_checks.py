"""Tests for attribute checker functions."""

import contextlib
import warnings
from collections import abc
from typing import Mapping as TypingMapping

from hasattrs import (
    has_abc_attrs,
    has_async_generator_attrs,
    has_async_iterable_attrs,
    has_async_iterator_attrs,
    has_attrs,
    has_awaitable_attrs,
    has_byte_string_attrs,
    has_callable_attrs,
    has_collection_attrs,
    has_container_attrs,
    has_coroutine_attrs,
    has_generator_attrs,
    has_hashable_attrs,
    has_item_view_attrs,
    has_iterable_attrs,
    has_iterator_attrs,
    has_keys_view_attrs,
    has_mapping_attrs,
    has_mapping_view_attrs,
    has_mutable_mapping_attrs,
    has_mutable_sequence_attrs,
    has_mutable_set_attrs,
    has_reversible_attrs,
    has_sequence_attrs,
    has_set_attrs,
    has_sized_attrs,
    has_values_view_attrs,
)


class TestHasAttrs:
    """Test the basic has_attrs function."""

    def test_has_attrs_true(self):
        assert has_attrs([], ["__len__", "__iter__"])

    def test_has_attrs_false(self):
        assert not has_attrs(5, ["__len__"])

    def test_has_attrs_empty(self):
        assert has_attrs(None, [])

    def test_has_attrs_partial(self):
        assert not has_attrs([1, 2], ["__len__", "__missing_attr__"])


class TestHasAbcAttrs:
    """Test the generic has_abc_attrs function."""

    def test_with_abc_class(self):
        assert has_abc_attrs({}, abc.Mapping)

    def test_with_typing_class(self):
        assert has_abc_attrs({}, TypingMapping)

    def test_with_string(self):
        assert has_abc_attrs({}, "Mapping")

    def test_fails_correctly(self):
        assert not has_abc_attrs([], abc.Mapping)


class TestContainerAttrs:
    """Test has_container_attrs function."""

    def test_list(self):
        assert has_container_attrs([1, 2, 3])

    def test_dict(self):
        assert has_container_attrs({})

    def test_set(self):
        assert has_container_attrs(set())

    def test_int(self):
        assert not has_container_attrs(5)


class TestHashableAttrs:
    """Test has_hashable_attrs function."""

    def test_int(self):
        assert has_hashable_attrs(5)

    def test_str(self):
        assert has_hashable_attrs("hello")

    def test_tuple(self):
        assert has_hashable_attrs((1, 2, 3))

    def test_list(self):
        # Lists have __hash__ attribute (set to None), so they pass the attribute check
        # This is a quirk of Python - the attribute exists but is set to None
        assert has_hashable_attrs([1, 2, 3])


class TestIterableAttrs:
    """Test has_iterable_attrs function."""

    def test_list(self):
        assert has_iterable_attrs([1, 2, 3])

    def test_dict(self):
        assert has_iterable_attrs({})

    def test_str(self):
        assert has_iterable_attrs("hello")

    def test_int(self):
        assert not has_iterable_attrs(5)


class TestIteratorAttrs:
    """Test has_iterator_attrs function."""

    def test_list_iterator(self):
        assert has_iterator_attrs(iter([1, 2, 3]))

    def test_list(self):
        assert not has_iterator_attrs([1, 2, 3])


class TestReversibleAttrs:
    """Test has_reversible_attrs function."""

    def test_list(self):
        assert has_reversible_attrs([1, 2, 3])

    def test_tuple(self):
        # In Python 3.8, tuples don't have __reversed__ method
        # They use the default reversed() which doesn't require the method
        assert not has_reversible_attrs((1, 2, 3))

    def test_dict(self):
        assert has_reversible_attrs({})

    def test_set(self):
        # Sets are not reversible
        assert not has_reversible_attrs(set())


class TestGeneratorAttrs:
    """Test has_generator_attrs function."""

    def test_generator(self):
        def gen():
            yield 1

        assert has_generator_attrs(gen())

    def test_list(self):
        assert not has_generator_attrs([1, 2, 3])


class TestSizedAttrs:
    """Test has_sized_attrs function."""

    def test_list(self):
        assert has_sized_attrs([1, 2, 3])

    def test_dict(self):
        assert has_sized_attrs({})

    def test_str(self):
        assert has_sized_attrs("hello")

    def test_int(self):
        assert not has_sized_attrs(5)


class TestCallableAttrs:
    """Test has_callable_attrs function."""

    def test_function(self):
        def f():
            pass

        assert has_callable_attrs(f)

    def test_lambda(self):
        assert has_callable_attrs(lambda x: x)

    def test_callable_class(self):
        class C:
            def __call__(self):
                pass

        assert has_callable_attrs(C())

    def test_int(self):
        assert not has_callable_attrs(5)


class TestCollectionAttrs:
    """Test has_collection_attrs function."""

    def test_list(self):
        assert has_collection_attrs([1, 2, 3])

    def test_dict(self):
        assert has_collection_attrs({})

    def test_set(self):
        assert has_collection_attrs(set())

    def test_str(self):
        assert has_collection_attrs("hello")

    def test_int(self):
        assert not has_collection_attrs(5)


class TestSequenceAttrs:
    """Test has_sequence_attrs function."""

    def test_list(self):
        assert has_sequence_attrs([1, 2, 3])

    def test_tuple(self):
        # Tuples don't have __reversed__ in Python 3.8
        assert not has_sequence_attrs((1, 2, 3))

    def test_str(self):
        # Strings don't have __reversed__ in Python 3.8
        assert not has_sequence_attrs("hello")

    def test_dict(self):
        assert not has_sequence_attrs({})

    def test_set(self):
        assert not has_sequence_attrs(set())


class TestMutableSequenceAttrs:
    """Test has_mutable_sequence_attrs function."""

    def test_list(self):
        assert has_mutable_sequence_attrs([1, 2, 3])

    def test_tuple(self):
        assert not has_mutable_sequence_attrs((1, 2, 3))


class TestByteStringAttrs:
    """Test has_byte_string_attrs function (deprecated)."""

    def test_bytes(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # bytes don't have __reversed__ in Python 3.8, so they don't pass Sequence check
            result = has_byte_string_attrs(b"hello")
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert result is False

    def test_bytearray(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            has_byte_string_attrs(bytearray(b"hello"))
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)


class TestSetAttrs:
    """Test has_set_attrs function."""

    def test_set(self):
        assert has_set_attrs({1, 2, 3})

    def test_frozenset(self):
        assert has_set_attrs(frozenset([1, 2, 3]))

    def test_list(self):
        assert not has_set_attrs([1, 2, 3])


class TestMutableSetAttrs:
    """Test has_mutable_set_attrs function."""

    def test_set(self):
        assert has_mutable_set_attrs({1, 2, 3})

    def test_frozenset(self):
        assert not has_mutable_set_attrs(frozenset([1, 2, 3]))


class TestMappingAttrs:
    """Test has_mapping_attrs function."""

    def test_dict(self):
        assert has_mapping_attrs({})

    def test_list(self):
        assert not has_mapping_attrs([])

    def test_custom_mapping(self):
        class MyMapping:
            def __getitem__(self, key):
                pass

            def __iter__(self):
                pass

            def __len__(self):
                pass

            def __contains__(self, key):
                pass

            def keys(self):
                pass

            def items(self):
                pass

            def values(self):
                pass

            def get(self, key):
                pass

            def __eq__(self, other):
                pass

            def __ne__(self, other):
                pass

        assert has_mapping_attrs(MyMapping())


class TestMutableMappingAttrs:
    """Test has_mutable_mapping_attrs function."""

    def test_dict(self):
        assert has_mutable_mapping_attrs({})

    def test_tuple(self):
        assert not has_mutable_mapping_attrs((1, 2))


class TestMappingViewAttrs:
    """Test has_mapping_view_attrs function."""

    def test_dict_keys(self):
        assert has_mapping_view_attrs({}.keys())

    def test_dict_values(self):
        assert has_mapping_view_attrs({}.values())

    def test_dict_items(self):
        assert has_mapping_view_attrs({}.items())


class TestItemViewAttrs:
    """Test has_item_view_attrs function."""

    def test_dict_items(self):
        assert has_item_view_attrs({}.items())

    def test_list(self):
        assert not has_item_view_attrs([])


class TestKeysViewAttrs:
    """Test has_keys_view_attrs function."""

    def test_dict_keys(self):
        assert has_keys_view_attrs({}.keys())

    def test_list(self):
        # Lists have __len__, __iter__, __contains__ which satisfies KEYS_VIEW (MAPPING_VIEW | COLLECTION)
        assert has_keys_view_attrs([])


class TestValuesViewAttrs:
    """Test has_values_view_attrs function."""

    def test_dict_values(self):
        # dict_values don't have __contains__ in any Python version (as of 3.12)
        # ValuesView requires __len__, __iter__, and __contains__,
        # but dict_values only has __len__ and __iter__
        assert not has_values_view_attrs({}.values())

    def test_list(self):
        # Lists have __len__, __iter__, __contains__ which satisfies VALUES_VIEW (MAPPING_VIEW | COLLECTION)
        assert has_values_view_attrs([])


class TestAwaitableAttrs:
    """Test has_awaitable_attrs function."""

    def test_coroutine(self):
        async def f():
            pass

        coro = f()
        try:
            assert has_awaitable_attrs(coro)
        finally:
            coro.close()

    def test_int(self):
        assert not has_awaitable_attrs(5)


class TestCoroutineAttrs:
    """Test has_coroutine_attrs function."""

    def test_coroutine(self):
        async def f():
            pass

        coro = f()
        try:
            assert has_coroutine_attrs(coro)
        finally:
            coro.close()

    def test_int(self):
        assert not has_coroutine_attrs(5)


class TestAsyncIterableAttrs:
    """Test has_async_iterable_attrs function."""

    def test_async_generator(self):
        async def gen():
            yield 1

        assert has_async_iterable_attrs(gen())

    def test_list(self):
        assert not has_async_iterable_attrs([])


class TestAsyncIteratorAttrs:
    """Test has_async_iterator_attrs function."""

    def test_async_generator(self):
        async def gen():
            yield 1

        assert has_async_iterator_attrs(gen())

    def test_list(self):
        assert not has_async_iterator_attrs([])


class TestAsyncGeneratorAttrs:
    """Test has_async_generator_attrs function."""

    def test_async_generator(self):
        async def gen():
            yield 1

        agen = gen()
        try:
            assert has_async_generator_attrs(agen)
        finally:
            # Clean up async generator
            with contextlib.suppress(Exception):
                agen.aclose()

    def test_list(self):
        assert not has_async_generator_attrs([])


class TestCustomClasses:
    """Test with custom classes that implement protocols."""

    def test_custom_sequence(self):
        class MySequence:
            def __getitem__(self, index):
                pass

            def __len__(self):
                pass

            def __contains__(self, value):
                pass

            def __iter__(self):
                pass

            def __reversed__(self):
                pass

            def index(self, value):
                pass

            def count(self, value):
                pass

        assert has_sequence_attrs(MySequence())

    def test_custom_mapping(self):
        class MyMapping:
            def __getitem__(self, key):
                pass

            def __iter__(self):
                pass

            def __len__(self):
                pass

            def __contains__(self, key):
                pass

            def keys(self):
                pass

            def items(self):
                pass

            def values(self):
                pass

            def get(self, key, default=None):
                pass

            def __eq__(self, other):
                pass

            def __ne__(self, other):
                pass

        assert has_mapping_attrs(MyMapping())
        assert not has_mutable_mapping_attrs(MyMapping())

    def test_incomplete_protocol(self):
        class IncompleteMapping:
            def __getitem__(self, key):
                pass

            def __len__(self):
                pass

            # Missing __iter__, keys, items, values, get, etc.

        assert not has_mapping_attrs(IncompleteMapping())
