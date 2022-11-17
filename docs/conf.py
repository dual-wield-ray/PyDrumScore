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
html_static_path = ['_static']
# html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

html_css_files = [
    'custom.css',
]

html_sidebars = {
    '**': [
        'about.html',
        'globaltoc.html',
        'relations.html',
        'searchbox.html',
        # 'donate.html',
    ]
}

# Various options for Alabaster theme
html_theme_options = {
    'github_button': True,
    'github_user': 'dual-wield-ray',
    'github_repo': 'pydrumscore',
    'sidebar_collapse': True,
    'sidebar_width': '30%',
    'caption_font_size': 'large',
    'sidebar_hr': '#FF8C00',
    # 'sidebar_header': '#FF8C00',
    'code_highlight': '#FF8C00',
    #'fixed_sidebar': True,
    'description': 'A Python scripting interface for creating drum sheet music',
    'logo_name': True,
    'logo': 'python-logo-only.png',
}

# -- Add all relevant modules to PATH for autodoct ---------------------------
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))
