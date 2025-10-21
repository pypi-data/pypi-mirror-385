# `my_package_lorenzouriel`

**A simple Python package by Lorenzo Uriel**  

`my_package_lorenzouriel` is a small Python package demonstrating basic package creation and distribution. It includes a simple function that prints a greeting message.
- [PyPI Profile](https://pypi.org/project/my-package-lorenzouriel/0.1.0/)

## Features
- Simple and easy to use
- Provides a friendly `hello()` function

## Installation
You can install the package via PyPI:
```bash
pip install my_package-lorenzouriel
```

Or install locally from your project:
```bash
pip install dist/my_package-0.1.0-py3-none-any.whl
```

## Usage
Import the package and use the `hello` function:

```python
from my_package import hello

hello()
# Output: Hello, I'm Lorenzo!
```

## Development
If you want to do the same, follow the steps below:
1. Clone the repository.

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install setuptools wheel twine
```

3. Build the package:
```bash
python setup.py sdist bdist_wheel
```

4. Upload to PyPI (optional):
```bash
twine upload dist/*
```