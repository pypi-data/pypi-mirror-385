Presentation
============

This python package provide a descriptive interface for reactive high-level
Tango devices.

Requirements
------------

The library requires:

 - **python** >= 3.6
 - **pytango** >= 9.2.1

Installation
------------

Install the library by running:

.. sourcecode:: console

  $ pip install facadedevice

Unit-testing
------------

Run the tests using:

.. sourcecode:: console

  $ pip install -e ".[tests]"
  $ pytest

Documentation
-------------

Generating the documentation requires:

- sphinx
- sphinx-rtd-theme
- sphinx.ext.autodoc
- sphinx.ext.napoleon

Build the documentation using:

.. sourcecode:: console

  $ pip install -e ".[doc]"
  $ python -m sphinx -n -W docs build/html
  $ sensible-browser build/html/index.html
