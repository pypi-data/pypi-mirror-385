"""Attribute set definitions for collections.abc types.

This module defines sets of attribute names (dunder methods and regular methods)
that correspond to the abstract base classes in collections.abc and typing.
"""

CONTAINER = {"__contains__"}
HASHABLE = {"__hash__"}
ITERABLE = {"__iter__"}
ITERATOR = ITERABLE | {"__next__"}
REVERSIBLE = ITERABLE | {"__reversed__"}
GENERATOR = ITERATOR | {"send", "throw", "close"}
SIZED = {"__len__"}
CALLABLE = {"__call__"}
COLLECTION = SIZED | ITERABLE | CONTAINER
SEQUENCE = REVERSIBLE | COLLECTION | {"__getitem__", "index", "count"}
MUTABLE_SEQUENCE = SEQUENCE | {
    "__setitem__",
    "__delitem__",
    "insert",
    "append",
    "reverse",
    "extend",
    "pop",
    "remove",
    "__iadd__",
}
BYTE_STRING = SEQUENCE
SET = COLLECTION | {
    "__le__",
    "__lt__",
    "__eq__",
    "__ne__",
    "__gt__",
    "__ge__",
    "__and__",
    "__or__",
    "__sub__",
    "__xor__",
    "isdisjoint",
}
MUTABLE_SET = SET | {
    "add",
    "discard",
    "clear",
    "pop",
    "remove",
    "__ior__",
    "__iand__",
    "__ixor__",
    "__isub__",
}
MAPPING = COLLECTION | {"__getitem__", "keys", "items", "values", "get", "__eq__", "__ne__"}
MUTABLE_MAPPING = MAPPING | {
    "__setitem__",
    "__delitem__",
    "pop",
    "popitem",
    "clear",
    "update",
    "setdefault",
}
MAPPING_VIEW = SIZED
ITEMS_VIEW = MAPPING_VIEW | SET
KEYS_VIEW = MAPPING_VIEW | COLLECTION
VALUES_VIEW = MAPPING_VIEW | COLLECTION
AWAITABLE = {"__await__"}
COROUTINE = AWAITABLE | {"send", "throw", "close"}
ASYNC_ITERABLE = {"__aiter__"}
ASYNC_ITERATOR = ASYNC_ITERABLE | {"__anext__"}
ASYNC_GENERATOR = ASYNC_ITERATOR | {"asend", "athrow", "aclose"}
