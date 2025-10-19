"""Attribute checker functions for collections.abc types.

This module provides functions to check if objects have the required attributes
for various abstract base classes from collections.abc and typing.

Example:
    >>> from hasattrs import has_mapping_attrs
    >>> class MyDict:
    ...     def __getitem__(self, key): pass
    ...     def __iter__(self): pass
    ...     def __len__(self): pass
    ...     # ... other Mapping methods
    >>> has_mapping_attrs(MyDict())
    True
"""

import warnings
from typing import Any, Iterable

from hasattrs.attributes import (
    ASYNC_GENERATOR,
    ASYNC_ITERABLE,
    ASYNC_ITERATOR,
    AWAITABLE,
    BYTE_STRING,
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
from hasattrs.types import abc_attrs


def has_attrs(obj: Any, attrs: Iterable[str]) -> bool:
    """Check if an object has all specified attributes.

    Args:
        obj: The object to check.
        attrs: An iterable of attribute names (strings) to check for.

    Returns:
        True if the object has all specified attributes, False otherwise.

    Example:
        >>> has_attrs([], ['__len__', '__iter__'])
        True
        >>> has_attrs(5, ['__len__'])
        False
    """
    return all(hasattr(obj, a) for a in attrs)


def has_abc_attrs(obj: Any, abc: Any) -> bool:
    """Check if an object has all attributes for a collections.abc type.

    Args:
        obj: The object to check.
        abc: The abstract base class to check against. Can be:
            - A collections.abc class (e.g., abc.Mapping)
            - A typing class (e.g., typing.Mapping)
            - A string name (e.g., 'Mapping')

    Returns:
        True if the object has all required attributes, False otherwise.

    Example:
        >>> from collections.abc import Mapping
        >>> has_abc_attrs({}, Mapping)
        True
        >>> has_abc_attrs([], Mapping)
        False
    """
    return has_attrs(obj, abc_attrs[abc])


def has_container_attrs(obj: Any) -> bool:
    """Check if an object has Container attributes (__contains__)."""
    return has_attrs(obj, CONTAINER)


def has_hashable_attrs(obj: Any) -> bool:
    """Check if an object has Hashable attributes (__hash__)."""
    return has_attrs(obj, HASHABLE)


def has_iterable_attrs(obj: Any) -> bool:
    """Check if an object has Iterable attributes (__iter__)."""
    return has_attrs(obj, ITERABLE)


def has_iterator_attrs(obj: Any) -> bool:
    """Check if an object has Iterator attributes (__iter__, __next__)."""
    return has_attrs(obj, ITERATOR)


def has_reversible_attrs(obj: Any) -> bool:
    """Check if an object has Reversible attributes (__iter__, __reversed__)."""
    return has_attrs(obj, REVERSIBLE)


def has_generator_attrs(obj: Any) -> bool:
    """Check if an object has Generator attributes."""
    return has_attrs(obj, GENERATOR)


def has_sized_attrs(obj: Any) -> bool:
    """Check if an object has Sized attributes (__len__)."""
    return has_attrs(obj, SIZED)


def has_callable_attrs(obj: Any) -> bool:
    """Check if an object has Callable attributes (__call__)."""
    return has_attrs(obj, CALLABLE)


def has_collection_attrs(obj: Any) -> bool:
    """Check if an object has Collection attributes."""
    return has_attrs(obj, COLLECTION)


def has_sequence_attrs(obj: Any) -> bool:
    """Check if an object has Sequence attributes."""
    return has_attrs(obj, SEQUENCE)


def has_mutable_sequence_attrs(obj: Any) -> bool:
    """Check if an object has MutableSequence attributes."""
    return has_attrs(obj, MUTABLE_SEQUENCE)


def has_byte_string_attrs(obj: Any) -> bool:
    """Check if an object has ByteString attributes.

    .. deprecated:: 0.1.0
        ByteString is deprecated in Python 3.9+ and will be removed in Python 3.14.
        Use collections.abc.Sequence with isinstance checks instead.
    """
    warnings.warn(
        "has_byte_string_attrs is deprecated because collections.abc.ByteString "
        "is deprecated since Python 3.9 and will be removed in Python 3.14. "
        "Use has_sequence_attrs or isinstance checks instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return has_attrs(obj, BYTE_STRING)


def has_set_attrs(obj: Any) -> bool:
    """Check if an object has Set attributes."""
    return has_attrs(obj, SET)


def has_mutable_set_attrs(obj: Any) -> bool:
    """Check if an object has MutableSet attributes."""
    return has_attrs(obj, MUTABLE_SET)


def has_mapping_attrs(obj: Any) -> bool:
    """Check if an object has Mapping attributes."""
    return has_attrs(obj, MAPPING)


def has_mutable_mapping_attrs(obj: Any) -> bool:
    """Check if an object has MutableMapping attributes."""
    return has_attrs(obj, MUTABLE_MAPPING)


def has_mapping_view_attrs(obj: Any) -> bool:
    """Check if an object has MappingView attributes."""
    return has_attrs(obj, MAPPING_VIEW)


def has_item_view_attrs(obj: Any) -> bool:
    """Check if an object has ItemsView attributes."""
    return has_attrs(obj, ITEMS_VIEW)


def has_keys_view_attrs(obj: Any) -> bool:
    """Check if an object has KeysView attributes."""
    return has_attrs(obj, KEYS_VIEW)


def has_values_view_attrs(obj: Any) -> bool:
    """Check if an object has ValuesView attributes."""
    return has_attrs(obj, VALUES_VIEW)


def has_awaitable_attrs(obj: Any) -> bool:
    """Check if an object has Awaitable attributes (__await__)."""
    return has_attrs(obj, AWAITABLE)


def has_coroutine_attrs(obj: Any) -> bool:
    """Check if an object has Coroutine attributes."""
    return has_attrs(obj, COROUTINE)


def has_async_iterable_attrs(obj: Any) -> bool:
    """Check if an object has AsyncIterable attributes (__aiter__)."""
    return has_attrs(obj, ASYNC_ITERABLE)


def has_async_iterator_attrs(obj: Any) -> bool:
    """Check if an object has AsyncIterator attributes."""
    return has_attrs(obj, ASYNC_ITERATOR)


def has_async_generator_attrs(obj: Any) -> bool:
    """Check if an object has AsyncGenerator attributes."""
    return has_attrs(obj, ASYNC_GENERATOR)
