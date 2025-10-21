# tango-facadedevice

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![image](https://img.shields.io/pypi/v/facadedevice.svg)](https://pypi.python.org/pypi/facadedevice)
[![image](https://img.shields.io/pypi/l/facadedevice.svg)](https://gitlab.com/MaxIV/tango-facadedevice/-/blob/main/LICENSE.txt)
[![image](https://readthedocs.org/projects/tango-facadedevice/badge/?version=latest)](https://tango-facadedevice.readthedocs.io/en/latest/)
[![image](https://gitlab.com/MaxIV/tango-facadedevice/badges/main/pipeline.svg)](https://gitlab.com/MaxIV/tango-facadedevice)
[![image](https://gitlab.com/MaxIV/tango-facadedevice/badges/main/coverage.svg)](https://gitlab.com/MaxIV/tango-facadedevice)

This python package provide a descriptive interface for reactive high-level
Tango devices.

## Requirements

The library requires:

- **python** >= 3.6
- **pytango** >= 9.2.1

## Installation

Install the library by running:

```console
$ pip install facadedevice
```

## Documentation

The documentation is hosted on [ReadTheDocs](http://tango-facadedevice.readthedocs.io/en/latest).

Generating the documentation requires:

- sphinx
- sphinx-rtd-theme

Build the documentation using:

```console
$ pip install -e ".[doc]"
$ python -m sphinx -n -W docs build/html
$ sensible-browser build/html/index.html
```

## Unit testing

The tests run on gitlab-ci.

Run the tests using::

```console
$ pip install -e ".[tests]"
$ pytest
```

The following libraries are used:

- pytest
- pytest-forked
- pytest-cov

## Contact

Vincent Michel: vincent.michel@esrf.fr
