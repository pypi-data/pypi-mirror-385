# dotenv-utils

[![Release Status](https://github.com/FynnFreyer/dotenv-utils/actions/workflows/build.yml/badge.svg)](https://pypi.org/project/dotenv-utils)
[![Doc Status](https://github.com/FynnFreyer/dotenv-utils/actions/workflows/docs.yml/badge.svg)][docs]
[![Test Status](https://github.com/FynnFreyer/dotenv-utils/actions/workflows/tests.yml/badge.svg)](https://codecov.io/gh/FynnFreyer/dotenv-utils/tests)
[![Coverage Status](https://codecov.io/gh/FynnFreyer/dotenv-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/FynnFreyer/dotenv-utils)

A tiny, self-contained package for parsing environment variables.
Works well in conjunction with [python-dotenv](https://pypi.org/project/python-dotenv/).

For a full-fledged solution, look at [environs](https://pypi.org/project/environs/) instead.

## Docs

You can find the [documentation][docs] for the project online.

## Installation

You can install the package via pip, with `pip install dotenv-utils`.

## Usage

Basic usage looks like this:

```python
# Load environment variables with python-dotenv (optional):
from dotenv import load_dotenv

load_dotenv()

# Basic functions to parse values and lists of values
from dotenv_utils import get_var, get_var_list

# Read a required variable (raises if missing):
SECRET_KEY: str = get_var("SECRET_KEY")  # e.g., "s3cr3t"

# Read an optional variable with default:
PROTOCOL: str = get_var("PROTOCOL", default="tcp")  # may be undefined

# Use a cast to set the value type:
PORT: int = get_var("PORT", cast=int)  # e.g., "22"

# Read a list from a semicolon-separated variable:
ALLOWED_HOSTS: list[str] = get_var_list(  # e.g., "example.com; my.domain.tld"
   "ALLOWED_HOSTS",
   default=["localhost"],
)

# By default, values are split by `;`. Pass, e.g., `sep=","` to use commas.
PORTS: list[int] = get_var_list(  # e.g., "22, 53, 80"
   "PORTS",
   sep=",",  # use commas
   cast=int,  # cast elements to int
)

# Examples of useful convenience functions from `dotenv_utils.casts`:
from dotenv_utils.casts import str2bool, str2timedelta
from datetime import timedelta

# The `str2bool` function will handle common ways to specify true/false as strings
DEBUG: bool = get_var("DEBUG", default=False, cast=str2bool)

# You can also use more exotic types - check the docs to see what's available
default_ttl = str2timedelta("5m")  # default arg is not cast - similar to argparse
CACHE_TTL: timedelta = get_var("CACHE_TTL", default=default_ttl, cast=str2timedelta)
```

## Contributing

Contributions are welcome!
To get started:

1. Fork the repository and clone your fork.
2. Create and activate a virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install development dependencies in editable mode.
   ```bash
   python -m pip install -e .[dev]
   ```
4. Run the test suite and linters, and build[^docs_reqs] the documentation.
   ```bash
   # see make help for all available rules
   make chores  # outputs are logged in logs/
   make docs  # output goes to docs/build
   ```
   The chores should not give you any complaints.
5. If everything looks good, you can open a pull request.
   Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) in your commit messages.

[^docs_reqs]:
    Documentation is built with Sphinx.
    Certain LaTeX packages might be required for the PDF.

[docs]: <https://fynnfreyer.github.io/dotenv-utils> "dotenv-utils documentation"
