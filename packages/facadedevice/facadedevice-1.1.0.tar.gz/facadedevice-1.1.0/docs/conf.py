import os
import sys

sys.path.append(os.path.abspath("../"))

from facadedevice import __version__

project = "facadedevice"
version = __version__
author = "Vincent Michel"
copyright = "2016, MAX-IV"

master_doc = "index"
highlight_language = "python"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

html_theme = "sphinx_rtd_theme"

suppress_warnings = ["image.nonlocal_uri"]
