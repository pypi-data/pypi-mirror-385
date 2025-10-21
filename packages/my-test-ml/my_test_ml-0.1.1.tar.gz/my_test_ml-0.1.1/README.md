# my-test-ml

A test package for ML explanation utilities.

## Installation

```bash
pip install my-test-ml
```

## Quick Start

```python
import mtml

# Print a simple greeting
mtml.hello()  # Output: Hello!
```

## Usage

```python
import mtml

# Call the hello function
mtml.hello()
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/my-test-ml.git
cd my-test-ml
pip install -e .
```

### Building the Package

```bash
pip install build
python -m build
```

### Publishing to PyPI

```bash
pip install twine
twine upload dist/*
```