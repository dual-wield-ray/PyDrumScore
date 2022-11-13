import sys
import os

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PyDrumScore'
copyright = '2022, Rémy Lapointe'
author = 'Rémy Lapointe'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.githubpages']
# extensions = ['sphinx.ext.autodoc', 'myst_parser', 'sphinx.ext.githubpages']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "**/site-packages"]



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = []



# -- Add all relevant modules to PATH for autodoct ---------------------------
root_path = os.path.join(os.path.abspath('.'), "pydrumscore")
# root_path = os.path.join(os.path.abspath('.'), "pydrumscore", "core")
# sys.path.append(root_path)
# sys.path.insert(0, os.path.abspath('.'))
