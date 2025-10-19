# python-gamedig

[![Versions][versions-image]][versions-url]
[![PyPI][pypi-image]][pypi-url]
[![Downloads][downloads-image]][downloads-url]
[![License][license-image]][license-url]

[versions-image]: https://img.shields.io/pypi/pyversions/gamedig
[versions-url]: https://github.com/DoctorJohn/python-gamedig/blob/main/pyproject.toml
[pypi-image]: https://img.shields.io/pypi/v/gamedig
[pypi-url]: https://pypi.org/project/gamedig/
[downloads-image]: https://img.shields.io/pypi/dm/gamedig
[downloads-url]: https://pypi.org/project/gamedig/
[license-image]: https://img.shields.io/pypi/l/gamedig
[license-url]: https://github.com/DoctorJohn/python-gamedig/blob/main/LICENSE

Unofficial high-level Python bindings for the Rust [gamedig](https://crates.io/crates/gamedig) crate.

## Installation

```bash
pip install gamedig
```

## Usage

```python
from socket import gethostbyname
from gamedig import query

ip_address = gethostbyname('minecraftonline.com')

response = query('minecraft', ip_address)

print(response)
```

## Development

1. Install dependencies into a virtual env: `uv sync`
2. Make changes to the code and tests
3. Build the package: `uv run maturin develop`
4. Run the tests: `uv run pytest`
