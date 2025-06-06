# ArgParser

A lightweight utility to simplify and validate argument parsing in class constructors. I wrote this for a uni assignment, code is largely unmaintained.

## Features

- Supports both **positional** and **keyword** arguments
- Type checking via `dtype` (e.g. `int`, `str`, `MyClass`)
- Subclass enforcement via `subClass`
- Numeric range validation with `min` and `max`
- String length validation with `minLength` and `maxLength`
- Default values for optional arguments

## Installation:

```bash
git clone https://github.com/q3st1on/ArgParser.git
cd ArgParser
python -m build
pip install .\dist\argparser-1.0.0-py3-none-any.whl
```
If you get the error `ModuleNotFoundError: No module named 'build'` when trying to install, you first need to download build by running `pip install build`

## Usage

```python
from ArgParser import ArgParser

class MyClass:
    def __init__(self, *args, **kwargs):
        argParser = ArgParser()
        argParser.addPositionalArg("pos1", dtype=str, default="value")
        argParser.addKeywordArg("kw1", dtype=ParentClass)
        argParser.addKeywordArg("kw2", subClass=ParentClass)
        argParser.addKeywordArg("kw3", min=1, max=1.1, default=1.05)
        argParser.addKeywordArg("kw4", dtype=str, minLength=2, maxLength=4, default="str")
        argParser.parseArgs(*args, **kwargs)

        self.pos1 = argParser.pos1
        self.kw1 = argParser.kw1
        self.kw2 = argParser.kw2
        self.kw3 = argParser.kw3
        self.kw4 = argParser.kw4
```

## Argument Constraints

| Constraint                | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `dtype`                   | Ensures the argument is of a specific type     |
| `subClass`                | Ensures the argument is a subclass of the type |
| `min` / `max`             | Enforces numeric bounds (inclusive)            |
| `minLength` / `maxLength` | Enforces string length limits                  |
| `default`                 | Provides a fallback value if not supplied      |
