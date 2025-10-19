"""HasAttrs: Check if objects have the same attributes as collections.abc types.

This package provides functions to check if objects have the required attributes
for various abstract base classes from collections.abc and typing, without using
isinstance checks. This is useful for duck-typing validation.

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

from hasattrs.checks import (
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

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "has_attrs",
    "has_abc_attrs",
    "has_container_attrs",
    "has_hashable_attrs",
    "has_iterable_attrs",
    "has_iterator_attrs",
    "has_reversible_attrs",
    "has_generator_attrs",
    "has_sized_attrs",
    "has_callable_attrs",
    "has_collection_attrs",
    "has_sequence_attrs",
    "has_mutable_sequence_attrs",
    "has_byte_string_attrs",
    "has_set_attrs",
    "has_mutable_set_attrs",
    "has_mapping_attrs",
    "has_mutable_mapping_attrs",
    "has_mapping_view_attrs",
    "has_item_view_attrs",
    "has_keys_view_attrs",
    "has_values_view_attrs",
    "has_awaitable_attrs",
    "has_coroutine_attrs",
    "has_async_iterable_attrs",
    "has_async_iterator_attrs",
    "has_async_generator_attrs",
]
