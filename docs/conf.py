"""
    Configuration file for the Sphinx documentation builder.

    For the full list of built-in configuration values, see the documentation:
    https://www.sphinx-doc.org/en/master/usage/configuration.htm
    -- Project information -----------------------------------------------------
    https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

# pylint: disable=invalid-name, redefined-builtin

import sys
import os

project = 'PyDrumScore'
copyright = '2022, Rémy Lapointe'
author = 'Rémy Lapointe'

root_doc = "globaltoc"

# TODO: Autogenerate from metadata
release = '0.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'myst_parser', 'sphinx.ext.githubpages']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "**/site-packages"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

# -- Add all relevant modules to PATH for autodoct ---------------------------
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))
