"""Type definitions and mappings for collections.abc types.

This module provides enums and mappings between abstract base classes
from collections.abc and typing modules to their corresponding attribute sets.
"""

import typing
from collections import abc
from enum import Enum
from typing import Any, Dict
from typing import Set as TypingSet

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


class ABC(Enum):
    """Enum of collections.abc abstract base classes."""

    Container = abc.Container
    Hashable = abc.Hashable
    Iterable = abc.Iterable
    Iterator = abc.Iterator
    Reversible = abc.Reversible
    Generator = abc.Generator
    Sized = abc.Sized
    Callable = abc.Callable
    Collection = abc.Collection
    Sequence = abc.Sequence
    MutableSequence = abc.MutableSequence
    ByteString = abc.ByteString
    Set = abc.Set
    MutableSet = abc.MutableSet
    Mapping = abc.Mapping
    MutableMapping = abc.MutableMapping
    MappingView = abc.MappingView
    ItemsView = abc.ItemsView
    KeysView = abc.KeysView
    ValuesView = abc.ValuesView
    Awaitable = abc.Awaitable
    Coroutine = abc.Coroutine
    AsyncIterable = abc.AsyncIterable
    AsyncIterator = abc.AsyncIterator
    AsyncGenerator = abc.AsyncGenerator


class Typing(Enum):
    """Enum of typing module abstract base classes."""

    Container = typing.Container
    Hashable = typing.Hashable
    Iterable = typing.Iterable
    Iterator = typing.Iterator
    Reversible = typing.Reversible
    Generator = typing.Generator
    Sized = typing.Sized
    Callable = typing.Callable
    Collection = typing.Collection
    Sequence = typing.Sequence
    MutableSequence = typing.MutableSequence
    ByteString = typing.ByteString
    Set = typing.Set
    MutableSet = typing.MutableSet
    Mapping = typing.Mapping
    MutableMapping = typing.MutableMapping
    MappingView = typing.MappingView
    ItemsView = typing.ItemsView
    KeysView = typing.KeysView
    ValuesView = typing.ValuesView
    Awaitable = typing.Awaitable
    Coroutine = typing.Coroutine
    AsyncIterable = typing.AsyncIterable
    AsyncIterator = typing.AsyncIterator
    AsyncGenerator = typing.AsyncGenerator


abc_attrs: Dict[Any, TypingSet[str]] = {
    abc.Container: CONTAINER,
    typing.Container: CONTAINER,
    "Container": CONTAINER,
    abc.Hashable: HASHABLE,
    typing.Hashable: HASHABLE,
    "Hashable": HASHABLE,
    abc.Iterable: ITERABLE,
    typing.Iterable: ITERABLE,
    "Iterable": ITERABLE,
    abc.Iterator: ITERATOR,
    typing.Iterator: ITERATOR,
    "Iterator": ITERATOR,
    abc.Reversible: REVERSIBLE,
    typing.Reversible: REVERSIBLE,
    "Reversible": REVERSIBLE,
    abc.Generator: GENERATOR,
    typing.Generator: GENERATOR,
    "Generator": GENERATOR,
    abc.Sized: SIZED,
    typing.Sized: SIZED,
    "Sized": SIZED,
    abc.Callable: CALLABLE,
    typing.Callable: CALLABLE,
    "Callable": CALLABLE,
    abc.Collection: COLLECTION,
    typing.Collection: COLLECTION,
    "Collection": COLLECTION,
    abc.Sequence: SEQUENCE,
    typing.Sequence: SEQUENCE,
    "Sequence": SEQUENCE,
    abc.MutableSequence: MUTABLE_SEQUENCE,
    typing.MutableSequence: MUTABLE_SEQUENCE,
    "MutableSequence": MUTABLE_SEQUENCE,
    abc.ByteString: BYTE_STRING,
    typing.ByteString: BYTE_STRING,
    "ByteString": BYTE_STRING,
    abc.Set: SET,
    typing.Set: SET,
    "Set": SET,
    abc.MutableSet: MUTABLE_SET,
    typing.MutableSet: MUTABLE_SET,
    "MutableSet": MUTABLE_SET,
    abc.Mapping: MAPPING,
    typing.Mapping: MAPPING,
    "Mapping": MAPPING,
    abc.MutableMapping: MUTABLE_MAPPING,
    typing.MutableMapping: MUTABLE_MAPPING,
    "MutableMapping": MUTABLE_MAPPING,
    abc.MappingView: MAPPING_VIEW,
    typing.MappingView: MAPPING_VIEW,
    "MappingView": MAPPING_VIEW,
    abc.ItemsView: ITEMS_VIEW,
    typing.ItemsView: ITEMS_VIEW,
    "ItemsView": ITEMS_VIEW,
    abc.KeysView: KEYS_VIEW,
    typing.KeysView: KEYS_VIEW,
    "KeysView": KEYS_VIEW,
    abc.ValuesView: VALUES_VIEW,
    typing.ValuesView: VALUES_VIEW,
    "ValuesView": VALUES_VIEW,
    abc.Awaitable: AWAITABLE,
    typing.Awaitable: AWAITABLE,
    "Awaitable": AWAITABLE,
    abc.Coroutine: COROUTINE,
    typing.Coroutine: COROUTINE,
    "Coroutine": COROUTINE,
    abc.AsyncIterable: ASYNC_ITERABLE,
    typing.AsyncIterable: ASYNC_ITERABLE,
    "AsyncIterable": ASYNC_ITERABLE,
    abc.AsyncIterator: ASYNC_ITERATOR,
    typing.AsyncIterator: ASYNC_ITERATOR,
    "AsyncIterator": ASYNC_ITERATOR,
    abc.AsyncGenerator: ASYNC_GENERATOR,
    typing.AsyncGenerator: ASYNC_GENERATOR,
    "AsyncGenerator": ASYNC_GENERATOR,
}
