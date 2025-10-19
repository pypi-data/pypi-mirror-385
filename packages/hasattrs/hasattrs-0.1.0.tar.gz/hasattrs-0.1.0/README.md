# HasAttrs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/eddiethedean/hasattrs/workflows/Tests/badge.svg)](https://github.com/eddiethedean/hasattrs/actions/workflows/tests.yml)
[![Lint](https://github.com/eddiethedean/hasattrs/workflows/Lint/badge.svg)](https://github.com/eddiethedean/hasattrs/actions/workflows/lint.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A pure Python package to check if objects have the same attributes as collections.abc types.

## Description

Use HasAttrs to check if objects have the same attributes as the abstract base classes in `collections.abc` and `typing`, such as `Mapping`, `MutableSequence`, and more. This is useful for duck-typing validation without using `isinstance()` checks.

HasAttrs has no dependencies outside the Python standard library and is fully typed (PEP 561 compatible).

## Installation

```bash
pip install hasattrs
```

## Requirements

* Python >= 3.8

## Usage

### Basic Example

```python
from collections.abc import Mapping
from hasattrs import has_mapping_attrs, has_abc_attrs

class MyDict:
    def __getitem__(self, key): ...
    def __iter__(self): ...
    def __len__(self): ...
    def __contains__(self, value): ...
    def keys(self): ...
    def items(self): ...
    def values(self): ...
    def get(self, key): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...

# isinstance does not work for custom classes without registration
isinstance(MyDict(), Mapping)  # False

# but hasattrs has_mapping_attrs does work
has_mapping_attrs(MyDict())  # True

# has_abc_attrs also works by passing in collections.abc classes
has_abc_attrs(MyDict(), Mapping)  # True
```

### Checking Different Types

```python
from hasattrs import (
    has_sequence_attrs,
    has_iterable_attrs,
    has_mutable_mapping_attrs,
)

# Check if an object has Sequence attributes
has_sequence_attrs([1, 2, 3])  # True
has_sequence_attrs({1, 2, 3})  # False

# Check if an object has Iterable attributes
has_iterable_attrs([1, 2, 3])  # True
has_iterable_attrs(5)  # False

# Check if an object has MutableMapping attributes
has_mutable_mapping_attrs({})  # True
has_mutable_mapping_attrs([])  # False
```

### Using the Generic Checker

```python
from collections import abc
from hasattrs import has_abc_attrs

my_list = [1, 2, 3]

# Check using collections.abc class
has_abc_attrs(my_list, abc.Sequence)  # True

# Check using typing class
from typing import Sequence
has_abc_attrs(my_list, Sequence)  # True

# Check using string name
has_abc_attrs(my_list, 'Sequence')  # True
```

## Available Checkers

HasAttrs provides checker functions for all major collections.abc types:

- `has_container_attrs()` - Check for `__contains__`
- `has_hashable_attrs()` - Check for `__hash__`
- `has_iterable_attrs()` - Check for `__iter__`
- `has_iterator_attrs()` - Check for `__iter__`, `__next__`
- `has_reversible_attrs()` - Check for `__iter__`, `__reversed__`
- `has_generator_attrs()` - Check for Generator protocol
- `has_sized_attrs()` - Check for `__len__`
- `has_callable_attrs()` - Check for `__call__`
- `has_collection_attrs()` - Check for Collection protocol
- `has_sequence_attrs()` - Check for Sequence protocol
- `has_mutable_sequence_attrs()` - Check for MutableSequence protocol
- `has_set_attrs()` - Check for Set protocol
- `has_mutable_set_attrs()` - Check for MutableSet protocol
- `has_mapping_attrs()` - Check for Mapping protocol
- `has_mutable_mapping_attrs()` - Check for MutableMapping protocol
- `has_mapping_view_attrs()` - Check for MappingView protocol
- `has_item_view_attrs()` - Check for ItemsView protocol
- `has_keys_view_attrs()` - Check for KeysView protocol
- `has_values_view_attrs()` - Check for ValuesView protocol
- `has_awaitable_attrs()` - Check for Awaitable protocol
- `has_coroutine_attrs()` - Check for Coroutine protocol
- `has_async_iterable_attrs()` - Check for AsyncIterable protocol
- `has_async_iterator_attrs()` - Check for AsyncIterator protocol
- `has_async_generator_attrs()` - Check for AsyncGenerator protocol

### Deprecation Warning

Note: `has_byte_string_attrs()` is deprecated as `collections.abc.ByteString` is deprecated in Python 3.9+ and will be removed in Python 3.14.

## Why Use HasAttrs?

1. **Duck Typing Validation**: Verify that objects implement the required protocol without inheritance
2. **Type Flexibility**: Works with any object, not just registered ABC subclasses
3. **No Dependencies**: Pure Python with no external dependencies
4. **Fully Typed**: Complete type hints for better IDE support and type checking
5. **Lightweight**: Minimal overhead, just attribute checking

## Development

### For Contributors

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

#### Quick Start

```bash
# Clone the repository
git clone https://github.com/eddiethedean/hasattrs.git
cd hasattrs

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (recommended)
pre-commit install

# Run tests
make test

# Run all checks (lint, type check, test)
make check
```

#### Pre-commit Hooks

We use pre-commit hooks to ensure code quality. After installing the hooks with `pre-commit install`, they will run automatically on every commit. You can also run them manually:

```bash
pre-commit run --all-files
```

The hooks include:
- **ruff**: Fast Python linter and formatter
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with a newline

## Contributing

Contributions are welcome! Please:

1. Read our [Contributing Guidelines](CONTRIBUTING.md)
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes and commit (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please ensure:
- All tests pass (`make test`)
- Code is formatted (`make format`)
- Linters pass (`make lint`)
- Type checks pass (`make type`)
- Test coverage remains at 100%

## Author

**Odos Matthews**
- Email: odosmatthews@gmail.com
- GitHub: [@eddiethedean](https://github.com/eddiethedean)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.